
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from typedmodels.models import TypedModel

from django.utils.six import text_type


@python_2_unicode_compatible
class Animal(TypedModel):
    """
    Abstract model
    """
    name = models.CharField(max_length=255)

    def say_something(self):
        raise NotImplementedError

    # def __repr__(self):
    #     return u'<%s: %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return text_type(self.name)


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
    canines_eaten = models.ManyToManyField(
        Canine
        )

    def say_something(self):
        return "raawr"


class Parrot(Animal):
    known_words = models.IntegerField()

    def say_something(self):
        return "hello"


class AbstractVegetable(TypedModel):
    """
    This is an entirely different typed model.
    """
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    yumness = models.FloatField(null=False)


class Fruit(AbstractVegetable):
    pass


class Vegetable(AbstractVegetable):
    pass
