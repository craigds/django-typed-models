
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
