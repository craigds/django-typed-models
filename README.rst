===================
django-typed-models
===================

Intro
=====

``django-typed-models`` provides an extra type of model inheritance for django.

The concrete type of each object is stored in the database, and when the object is retrieved it is automatically cast to the correct concrete type. These are basically proxy models, but with a known type.

Licensed under the New BSD License.


Features
========

* Automatic downcasting of models from querysets
* All models subclassing a common base are stored in the same table
* object types are stored in a 'type' field in the database
* No extra queries or joins to retrieve multiple types


Usage:
======

An example says a bunch of words::

    # myapp/models.py

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

::
    
    # later
    >>> from myapp.models import Animal, Canine, Feline
    >>> Feline.objects.create(name="kitteh")
    >>> Feline.objects.create(name="cheetah")
    >>> Canine.objects.create(name="fido")
    >>> print Animal.objects.all()
    [<Feline: kitteh>, <Feline: cheetah>, <Canine: fido>]

    >>> print Canine.objects.all()
    [<Canine: fido>]

    >>> print Feline.objects.all()
    [<Feline: kitteh>, <Feline: cheetah>]


Limitations
===========

These are just special proxy models, so all the objects are stored in the same table. As a result, subclasses can't have new fields defined. If you need to do that, you should just use django's built-in multiple-table inheritance.

Requirements
============

* Python 2.5+ (tested in 2.6)

* Django 1.2+ (tested in 1.3)
