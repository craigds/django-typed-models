
from django.db import models
from typedmodels import TypedModel


class Animal(TypedModel):
    """
    Abstract model
    """
    name = models.CharField(max_length=255)

    def say_something(self):
        raise NotImplemented

    # def __repr__(self):
    #     return u'<%s: %s>' % (self.__class__.__name__, self.name)

    def __unicode__(self):
        return unicode(self.name)


class Canine(Animal):
    def say_something(self):
        return "woof"

class Feline(Animal):
    def say_something(self):
        return "meoww"

    mice_eaten = models.IntegerField(
        default = 0
        )
    

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

