===================
django-typed-models
===================

.. image:: https://travis-ci.org/craigds/django-typed-models.png?branch=master
   :target: https://travis-ci.org/craigds/django-typed-models

.. image:: https://coveralls.io/repos/craigds/django-typed-models/badge.png?branch=master
   :target: https://coveralls.io/r/craigds/django-typed-models?branch=master

Intro
=====

``django-typed-models`` provides an extra type of model inheritance for Django. It is similar to single-table inheritance in Ruby on Rails.

The concrete type of each object is stored in the database, and when the object is retrieved it is automatically cast to the correct concrete type.

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
        mice_eaten = models.IntegerField(
    	    default = 0
            )
    
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

You can actually change the types of objects. Simply run an update query::

    Feline.objects.update(type='myapp.bigcat')

If you want to change the type of an object without refreshing it from the database, you can call ``recast``::

    kitty.recast(BigCat)
    # or kitty.recast('myapp.bigcat')
    kitty.save()


Limitations
===========

Since all objects are stored in the same table, all fields defined in subclasses are nullable.

Known issues
============

* Error in South migration when m2m field related to model not inheriting directly from TypedModel is used.
* XML serialization doesn’t work.

Requirements
============

* Python 2.6, 2.7, 3.3

* Django 1.5+
