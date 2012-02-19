from django.db import models
from django.db.models.base import ModelBase


class TypedModelManager(models.Manager):
    def get_query_set(self):
        qs = super(TypedModelManager, self).get_query_set()
        if hasattr(self.model, 'TYPE'):
            qs = qs.filter(type=self.model.TYPE)
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

        typ = classdict.get('TYPE', None)
        if typ is not None:
            if not isinstance(typ, basestring):
                raise ValueError("TYPE should be a unicode (got: %r)" % typ)

            # Enforce that typed subclasses are proxy models.
            # Update an existing metaclass, or define an empty one
            # then set proxy=True

            class Meta:
                pass
            Meta = classdict.get('Meta', Meta)
            Meta.proxy = True

            # set app_label to the same as the base class, unless explicitly defined otherwise
            if not hasattr(Meta, 'app_label'):
                for base in bases:
                    if hasattr(getattr(base, '_meta', None), 'app_label'):
                        Meta.app_label = base._meta.app_label
                        break

            classdict.update({
                'Meta': Meta,
            })

            # TODO enforce that typed subclasses cannot have defined fields
            # (since that's not obvious if the user isn't explicitly defining proxy=True)
            pass

        cls = super(TypedModelMetaclass, meta).__new__(meta, classname, bases, classdict)

        base = None
        if typ:
            for base in cls.mro():
                if issubclass(base, TypedModel) and not hasattr(base, 'TYPE'):
                    break
            else:
                raise ValueError("A typed TypedModel must be a subclass of an untyped non-abstract base")
            if typ in base._autocast_types:
                raise ValueError("Can't register %s type %r to %r (already registered to %r )" % (typ, classname, base._autocast_types))
            base._autocast_types[typ] = cls
            type_name = getattr(cls._meta, 'verbose_name', cls.__name__)
            type_field = base._meta.get_field('type')
            type_field._choices = tuple(list(type_field.choices) + [(typ, type_name)])

            # need to populate local_fields, otherwise no fields get serialized in fixtures
            cls._meta.local_fields = base._meta.local_fields[:]
        else:
            # this is the base class
            cls._autocast_types = {}

            # set default manager. this will be inherited by subclasses, since they are proxy models
            cls.add_to_class('objects', TypedModelManager())
            cls._default_manager = cls.objects

            # add a get_type_classes classmethod to allow fetching of all the subclasses (useful for admin)

            def get_type_classes(cls_):
                if cls_ is not cls:
                    raise ValueError("get_type_classes() is not accessible from subclasses of %s (was called from %s)" % (cls.__name__, cls_.__name__))
                return cls._autocast_types.values()[:]
            cls.get_type_classes = classmethod(get_type_classes)
        return cls


class TypedModel(models.Model):
    """
    This class contains the functionality required to auto-downcast a model based
    on its ``type`` attribute.

    To use, simply subclass TypedModel for your base type, and then subclass
    that for your concrete types.

    Each concrete type should specify a unique TYPE attribute (must be a string)

    Example usage:

        class Animal(TypedModel):
            some_field = models.CharField(max_length=100)

        class Canine(Animal):
            TYPE = "datasources.canine"

        class Bovine(Animal):
            TYPE = "datasources.bovine"
    """

    __metaclass__ = TypedModelMetaclass

    type = models.CharField(choices=(), max_length=255, null=False, blank=False, db_index=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(TypedModel, self).__init__(*args, **kwargs)
        self.recast()

    def recast(self):
        if not self.type:
            if not hasattr(self, 'TYPE'):
                # Ideally we'd raise an error here, but the django admin likes to call
                # model() and doesn't expect an error.
                # Instead, we raise an error when the object is saved.
                return
            self.type = self.TYPE

        for base in self.__class__.mro():
            if issubclass(base, TypedModel) and hasattr(base, '_autocast_types'):
                break
        else:
            raise ValueError("No suitable base class found to recast!")

        try:
            correct_cls = base._autocast_types[self.type]
        except KeyError:
            raise ValueError("Invalid %s identifier : %r" % (base.__name__, self.type))

        if self.__class__ != correct_cls:
            self.__class__ = correct_cls

    def save(self, *args, **kwargs):
        if not getattr(self, 'TYPE', None):
            raise RuntimeError("Untyped %s cannot be saved." % self.__class__.__name__)
        return super(TypedModel, self).save(*args, **kwargs)
