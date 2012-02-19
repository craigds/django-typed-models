from django.db import models
from django.db.models.base import ModelBase


class TypedModelManager(models.Manager):
    def get_query_set(self):
        qs = super(TypedModelManager, self).get_query_set()
        if hasattr(self.model, '_typedmodels_type'):
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
            return super(TypedModelMetaclass, meta).__new__(meta, classname, bases, classdict)

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
            Meta = classdict.get('Meta', Meta)
            Meta.proxy = True

            # set app_label to the same as the base class, unless explicitly defined otherwise
            if not hasattr(Meta, 'app_label'):
                if hasattr(getattr(base_class, '_meta', None), 'app_label'):
                    Meta.app_label = base_class._meta.app_label

            classdict.update({
                'Meta': Meta,
            })

            # TODO enforce that typed subclasses cannot have defined fields
            # (since that's not obvious if the user isn't explicitly defining proxy=True)
            pass

        cls = super(TypedModelMetaclass, meta).__new__(meta, classname, bases, classdict)

        if base_class:
            opts = cls._meta
            typ = "%s.%s" % (opts.app_label, opts.object_name.lower())
            cls._typedmodels_type = typ
            cls._typedmodels_subtypes = [typ]
            if typ in base_class._typedmodels_registry:
                raise ValueError("Can't register %s type %r to %r (already registered to %r )" % (typ, classname, base_class._typedmodels_registry))
            base_class._typedmodels_registry[typ] = cls
            type_name = getattr(cls._meta, 'verbose_name', cls.__name__)
            type_field = base_class._meta.get_field('type')
            type_field._choices = tuple(list(type_field.choices) + [(typ, type_name)])

            # look for any other proxy superclasses, they'll need to know
            # about this subclass
            for superclass in cls.mro():
                if (issubclass(superclass, base_class)
                        and superclass not in (cls, base_class)
                        and hasattr(superclass, '_typedmodels_type')):
                    superclass._typedmodels_subtypes.append(typ)

            # need to populate local_fields, otherwise no fields get serialized in fixtures
            cls._meta.local_fields = base_class._meta.local_fields[:]
        else:
            # this is the base class
            cls._typedmodels_registry = {}

            # set default manager. this will be inherited by subclasses, since they are proxy models
            cls.add_to_class('objects', TypedModelManager())
            cls._default_manager = cls.objects

            # add a get_type_classes classmethod to allow fetching of all the subclasses (useful for admin)

            def get_type_classes(subcls):
                if subcls is not cls:
                    raise ValueError("get_type_classes() is not accessible from subclasses of %s (was called from %s)" % (cls.__name__, subcls.__name__))
                return cls._typedmodels_registry.values()[:]
            cls.get_type_classes = classmethod(get_type_classes)
        return cls


class TypedModel(models.Model):
    '''
    This class contains the functionality required to auto-downcast a model based
    on its ``type`` attribute.

    To use, simply subclass TypedModel for your base type, and then subclass
    that for your concrete types.

    Example usage::

        from django.db import models
        from typedmodels import TypedModel

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

    __metaclass__ = TypedModelMetaclass

    type = models.CharField(choices=(), max_length=255, null=False, blank=False, db_index=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TypedModel, self).__init__(*args, **kwargs)
        self.recast()

    def recast(self):
        if not self.type:
            if not hasattr(self, '_typedmodels_type'):
                # Ideally we'd raise an error here, but the django admin likes to call
                # model() and doesn't expect an error.
                # Instead, we raise an error when the object is saved.
                return
            self.type = self._typedmodels_type

        for base in self.__class__.mro():
            if issubclass(base, TypedModel) and hasattr(base, '_typedmodels_registry'):
                break
        else:
            raise ValueError("No suitable base class found to recast!")

        try:
            correct_cls = base._typedmodels_registry[self.type]
        except KeyError:
            raise ValueError("Invalid %s identifier : %r" % (base.__name__, self.type))

        if self.__class__ != correct_cls:
            self.__class__ = correct_cls

    def save(self, *args, **kwargs):
        if not getattr(self, '_typedmodels_type', None):
            raise RuntimeError("Untyped %s cannot be saved." % self.__class__.__name__)
        return super(TypedModel, self).save(*args, **kwargs)
