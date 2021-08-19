from functools import partial
import types

from django.core.exceptions import FieldDoesNotExist, FieldError
from django.core.serializers.python import Serializer as _PythonSerializer
from django.core.serializers.xml_serializer import Serializer as _XmlSerializer
from django.db import models
from django.db.models.base import ModelBase, DEFERRED
from django.db.models.fields import Field
from django.db.models.options import make_immutable_fields_list
from django.utils.encoding import smart_str


class TypedModelManager(models.Manager):
    def get_queryset(self):
        qs = super(TypedModelManager, self).get_queryset()
        return self._filter_by_type(qs)

    def _filter_by_type(self, qs):
        if hasattr(self.model, "_typedmodels_type"):
            if len(self.model._typedmodels_subtypes) > 1:
                qs = qs.filter(type__in=self.model._typedmodels_subtypes)
            else:
                qs = qs.filter(type=self.model._typedmodels_type)
        return qs


class TypedModelMetaclass(ModelBase):
    """
    This metaclass enables a model for auto-downcasting using a ``type`` attribute.
    """

    def __new__(meta, classname, bases, classdict):
        try:
            TypedModel
        except NameError:
            # don't do anything for TypedModel class itself
            #
            # ...except updating Meta class to instantiate fields_from_subclasses attribute
            typed_model = super(TypedModelMetaclass, meta).__new__(
                meta, classname, bases, classdict
            )
            # We have to set this attribute after _meta has been created, otherwise an
            # exception would be thrown by Options class constructor.
            typed_model._meta.fields_from_subclasses = {}
            return typed_model

        # look for a non-proxy base class that is a subclass of TypedModel
        mro = list(bases)
        while mro:
            base_class = mro.pop(-1)
            if issubclass(base_class, TypedModel) and base_class is not TypedModel:
                if base_class._meta.proxy:
                    # continue up the mro looking for non-proxy base classes
                    mro.extend(base_class.__bases__)
                else:
                    break
        else:
            base_class = None

        if base_class:
            # Enforce that subclasses are proxy models.
            # Update an existing metaclass, or define an empty one
            # then set proxy=True
            class Meta:
                pass

            Meta = classdict.get("Meta", Meta)
            if getattr(Meta, "proxy", False):
                # If user has specified proxy=True explicitly, we assume that he wants it to be treated like ordinary
                # proxy class, without TypedModel logic.
                return super(TypedModelMetaclass, meta).__new__(
                    meta, classname, bases, classdict
                )
            Meta.proxy = True

            declared_fields = dict(
                (name, element)
                for name, element in list(classdict.items())
                if isinstance(element, Field)
            )

            for field_name, field in list(declared_fields.items()):
                # We need fields defined on subclasses to either:
                #  * be a ManyToManyField
                #  * have a default
                #  * be nullable
                if not (field.many_to_many or field.null or field.has_default()):
                    raise FieldError(
                        "All fields defined on typedmodels subclasses must be nullable, "
                        "or have a default set. "
                        "Add null=True to the {}.{} field definition.".format(
                            classname, field_name
                        )
                    )

                if isinstance(field, models.fields.related.RelatedField):
                    # Monkey patching field instance to make do_related_class use created class instead of base_class.
                    # Actually that class doesn't exist yet, so we just monkey patch base_class for a while,
                    # changing _meta.model_name, so accessor names are generated properly.
                    # We'll do more stuff when the class is created.
                    old_do_related_class = field.do_related_class

                    def do_related_class(self, other, cls):
                        base_class_name = base_class.__name__
                        cls._meta.model_name = classname.lower()
                        old_do_related_class(other, cls)
                        cls._meta.model_name = base_class_name.lower()

                    field.do_related_class = types.MethodType(do_related_class, field)
                if isinstance(field, models.fields.related.RelatedField):
                    remote_field = field.remote_field
                    if (
                        isinstance(remote_field.model, TypedModel)
                        and remote_field.model.base_class
                    ):
                        remote_field.limit_choices_to[
                            "type__in"
                        ] = remote_field.model._typedmodels_subtypes
                field.contribute_to_class(base_class, field_name)
                classdict.pop(field_name)
            base_class._meta.fields_from_subclasses.update(declared_fields)

            # set app_label to the same as the base class, unless explicitly defined otherwise
            if not hasattr(Meta, "app_label"):
                if hasattr(getattr(base_class, "_meta", None), "app_label"):
                    Meta.app_label = base_class._meta.app_label

            classdict.update(
                {
                    "Meta": Meta,
                }
            )

        classdict["base_class"] = base_class

        cls = super(TypedModelMetaclass, meta).__new__(
            meta, classname, bases, classdict
        )

        cls._meta.fields_from_subclasses = {}

        if base_class:
            opts = cls._meta

            model_name = opts.model_name
            typ = "%s.%s" % (opts.app_label, model_name)
            cls._typedmodels_type = typ
            cls._typedmodels_subtypes = [typ]
            if typ in base_class._typedmodels_registry:
                raise ValueError(
                    "Can't register type %r to %r (already registered to %r)"
                    % (typ, classname, base_class._typedmodels_registry[typ].__name__)
                )
            base_class._typedmodels_registry[typ] = cls

            type_name = getattr(cls._meta, "verbose_name", cls.__name__)
            type_field = base_class._meta.get_field("type")
            choices = tuple(list(type_field.choices) + [(typ, type_name)])
            type_field.choices = choices

            cls._meta.declared_fields = declared_fields

            # look for any other proxy superclasses, they'll need to know
            # about this subclass
            for superclass in cls.mro():
                if (
                    issubclass(superclass, base_class)
                    and superclass not in (cls, base_class)
                    and hasattr(superclass, "_typedmodels_type")
                ):
                    superclass._typedmodels_subtypes.append(typ)

            meta._patch_fields_cache(cls, base_class)
        else:
            # this is the base class
            cls._typedmodels_registry = {}

            # Since fields may be added by subclasses, save original fields.
            cls._meta._typedmodels_original_fields = {f.name for f in cls._meta.fields}
            cls._meta._typedmodels_original_many_to_many = {
                f.name for f in cls._meta.many_to_many
            }

            # add a get_type_classes classmethod to allow fetching of all the subclasses (useful for admin)

            def get_type_classes(subcls):
                if subcls is cls:
                    return list(cls._typedmodels_registry.values())
                else:
                    return [
                        cls._typedmodels_registry[k]
                        for k in subcls._typedmodels_subtypes
                    ]

            cls.get_type_classes = classmethod(get_type_classes)

            def get_types(subcls):
                if subcls is cls:
                    return list(cls._typedmodels_registry.keys())
                else:
                    return subcls._typedmodels_subtypes[:]

            cls.get_types = classmethod(get_types)

        return cls

    @staticmethod
    def _model_has_field(cls, base_class, field_name):
        if field_name in base_class._meta._typedmodels_original_many_to_many:
            return True
        if field_name in base_class._meta._typedmodels_original_fields:
            return True
        if any(f.name == field_name for f in base_class._meta.private_fields):
            return True
        for ancestor in cls.mro():
            if issubclass(ancestor, base_class) and ancestor != base_class:
                if field_name in ancestor._meta.declared_fields.keys():
                    return True

        if field_name in cls._meta.fields_map:
            # Crazy case where a reverse M2M from another typedmodels proxy points to this proxy
            # (this is an m2m reverse field)
            return True
        return False

    @staticmethod
    def _patch_fields_cache(cls, base_class):
        orig_get_fields = cls._meta._get_fields

        def _get_fields(
            self,
            forward=True,
            reverse=True,
            include_parents=True,
            include_hidden=False,
            seen_models=None,
        ):
            cache_key = (
                forward,
                reverse,
                include_parents,
                include_hidden,
                seen_models is None,
            )

            was_cached = cache_key in self._get_fields_cache
            fields = orig_get_fields(
                forward=forward,
                reverse=reverse,
                include_parents=include_parents,
                include_hidden=include_hidden,
                seen_models=seen_models,
            )
            # If it was cached already, it's because we've already filtered this, skip it
            if not was_cached:
                fields = [
                    f
                    for f in fields
                    if TypedModelMetaclass._model_has_field(cls, base_class, f.name)
                ]
                fields = make_immutable_fields_list("get_fields()", fields)
                self._get_fields_cache[cache_key] = fields
            return fields

        cls._meta._get_fields = partial(_get_fields, cls._meta)

        # If fields are already cached, expire the cache.
        cls._meta._expire_cache()


class TypedModel(models.Model, metaclass=TypedModelMetaclass):
    '''
    This class contains the functionality required to auto-downcast a model based
    on its ``type`` attribute.

    To use, simply subclass TypedModel for your base type, and then subclass
    that for your concrete types.

    Example usage::

        from django.db import models
        from typedmodels.models import TypedModel

        class Animal(TypedModel):
            """
            Abstract model
            """
            name = models.CharField(max_length=255)

            def say_something(self):
                raise NotImplemented

            def __repr__(self):
                return u'<%s: %s>' % (self.__class__.__name__, self.name)

        class Canine(Animal):
            def say_something(self):
                return "woof"

        class Feline(Animal):
            def say_something(self):
                return "meoww"
    '''

    objects = TypedModelManager()

    type = models.CharField(
        choices=(), max_length=255, null=False, blank=False, db_index=True
    )

    # Class variable indicating if model should be automatically recasted after initialization
    _auto_recast = True

    class Meta:
        abstract = True

    @classmethod
    def from_db(cls, db, field_names, values):
        # Called when django instantiates a model class from a queryset.
        _typedmodels_do_recast = True
        if "type" not in field_names:
            # LIMITATION:
            # `type` was deferred in the queryset.
            # So we can't cast this model without generating another query.
            # That'd be *really* bad for performance.
            # Most likely, this would have happened in `obj.fieldname`, where `fieldname` is deferred.
            # This will populate a queryset with .only('fieldname'),
            # leading to this situation where 'type' is deferred.
            # Django will then copy the fieldname from those model instances onto the original obj.
            # In this case we don't really need a typed subclass, so we choose to just not recast in
            # this situation.
            #
            # Unfortunately we can't tell the difference between this situation and
            # MyModel.objects.only('myfield'). If you do that, we will also not recast.
            #
            # If you want you can recast manually (call obj.recast() on each object in your
            # queryset) - but by far a better solution would be to not defer the `type` field
            # to start with.
            _typedmodels_do_recast = False

        if len(values) != len(cls._meta.concrete_fields):
            values_iter = iter(values)
            values = [
                next(values_iter) if f.attname in field_names else DEFERRED
                for f in cls._meta.concrete_fields
            ]
        new = cls(*values, _typedmodels_do_recast=_typedmodels_do_recast)
        new._state.adding = False
        new._state.db = db
        return new

    def __init__(self, *args, _typedmodels_do_recast=None, **kwargs):
        # Calling __init__ on base class because some functions (e.g. save()) need access to field values from base
        # class.

        # Move args to kwargs since base_class may have more fields defined with different ordering
        args = list(args)
        if len(args) > len(self._meta.fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        for field_value, field in zip(args, self._meta.fields):
            kwargs[field.attname] = field_value
        args = []  # args were all converted to kwargs

        if self.base_class:
            before_class = self.__class__
            self.__class__ = self.base_class
        else:
            before_class = None
        super(TypedModel, self).__init__(*args, **kwargs)
        if before_class:
            self.__class__ = before_class

        if _typedmodels_do_recast is None:
            _typedmodels_do_recast = self._auto_recast
        if _typedmodels_do_recast:
            self.recast()

    def recast(self, typ=None):
        for base in self.__class__.mro():
            if issubclass(base, TypedModel) and hasattr(base, "_typedmodels_registry"):
                break
        else:
            raise ValueError("No suitable base class found to recast!")

        if not self.type:
            if not hasattr(self, "_typedmodels_type"):
                # This is an instance of an untyped model
                if typ is None:
                    # recast() is probably being called by __init__() here.
                    # Ideally we'd raise an error here, but the django admin likes to call
                    # model() and doesn't expect an error.
                    # Instead, we raise an error when the object is saved.
                    return
            else:
                self.type = self._typedmodels_type

        if typ is None:
            typ = self.type
        else:
            if isinstance(typ, type) and issubclass(typ, base):
                model_name = typ._meta.model_name
                typ = "%s.%s" % (typ._meta.app_label, model_name)

        try:
            correct_cls = base._typedmodels_registry[typ]
        except KeyError:
            raise ValueError("Invalid %s identifier: %r" % (base.__name__, typ))

        self.type = typ

        current_cls = self.__class__

        if current_cls != correct_cls:
            self.__class__ = correct_cls

    def save(self, *args, **kwargs):
        if not getattr(self, "_typedmodels_type", None):
            raise RuntimeError("Untyped %s cannot be saved." % self.__class__.__name__)
        return super(TypedModel, self).save(*args, **kwargs)

    def _get_unique_checks(self, exclude=None):
        unique_checks, date_checks = super(TypedModel, self)._get_unique_checks(
            exclude=exclude
        )

        for i, (model_class, field_names) in reversed(list(enumerate(unique_checks))):
            for fn in field_names:
                try:
                    self._meta.get_field(fn)
                except FieldDoesNotExist:
                    # Some field in this unique check isn't actually on this proxy model.
                    unique_checks.pop(i)
                    break
        return unique_checks, date_checks


# Monkey patching Python and XML serializers in Django to use model name from base class.
# This should be preferably done by changing __unicode__ method for ._meta attribute in each model,
# but it doesn’t work.
_python_serializer_get_dump_object = _PythonSerializer.get_dump_object


def _get_dump_object(self, obj):
    if isinstance(obj, TypedModel):
        return {
            "pk": smart_str(obj._get_pk_val(), strings_only=True),
            "model": smart_str(getattr(obj, "base_class", obj)._meta),
            "fields": self._current,
        }
    else:
        return _python_serializer_get_dump_object(self, obj)


_PythonSerializer.get_dump_object = _get_dump_object

_xml_serializer_start_object = _XmlSerializer.start_object


def _start_object(self, obj):
    if isinstance(obj, TypedModel):
        self.indent(1)
        obj_pk = obj._get_pk_val()
        modelname = smart_str(getattr(obj, "base_class", obj)._meta)
        if obj_pk is None:
            attrs = {
                "model": modelname,
            }
        else:
            attrs = {
                "pk": smart_str(obj._get_pk_val()),
                "model": modelname,
            }

        self.xml.startElement("object", attrs)
    else:
        return _xml_serializer_start_object(self, obj)


_XmlSerializer.start_object = _start_object
