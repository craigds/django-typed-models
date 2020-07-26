from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import ForeignKey, PositiveIntegerField, CharField
from typedmodels.models import TypedModel


class UniqueIdentifier(models.Model):
    referent = GenericForeignKey()
    content_type = ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.CASCADE
    )
    object_id = PositiveIntegerField(null=True, blank=True)
    created = models.DateTimeField(db_index=True, auto_now_add=True)
    name = CharField(max_length=255)


class UniqueIdentifierMixin(models.Model):
    unique_identifiers = GenericRelation(
        UniqueIdentifier, related_query_name='referents'
    )

    class Meta:
        abstract = True


class Animal(TypedModel, UniqueIdentifierMixin):
    """
    Abstract model
    """

    name = models.CharField(max_length=255)

    def say_something(self):
        raise NotImplementedError

    # def __repr__(self):
    #     return u'<%s: %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return str(self.name)


class Canine(Animal):
    def say_something(self):
        return "woof"


class Feline(Animal):
    def say_something(self):
        return "meoww"

    mice_eaten = models.IntegerField(default=0)


class BigCat(Feline):
    """
    This model tests doubly-proxied models.
    """

    def say_something(self):
        return "roar"


class AngryBigCat(BigCat):
    """
    This model tests triple-proxied models. Because we can
    """

    canines_eaten = models.ManyToManyField(Canine)

    def say_something(self):
        return "raawr"


class Parrot(Animal):
    known_words = models.IntegerField(null=True)

    def say_something(self):
        return "hello"


class AbstractVegetable(TypedModel):
    """
    This is an entirely different typed model.
    """

    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    yumness = models.FloatField(null=False)

    mymanager = models.Manager()


class Fruit(AbstractVegetable):
    pass


class Vegetable(AbstractVegetable):
    pass


class Parent(TypedModel):
    a = models.CharField(max_length=1)


class Child1(Parent):
    b = models.OneToOneField('self', null=True, on_delete=models.CASCADE)


class Child2(Parent):
    pass
