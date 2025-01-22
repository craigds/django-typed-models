# django-typed-models

![example workflow](https://github.com/craigds/django-typed-models/actions/workflows/tests.yml/badge.svg)

## Intro

`django-typed-models` provides an extra type of model inheritance for Django. It is similar to single-table inheritance in Ruby on Rails.

The actual type of each object is stored in the database, and when the object is retrieved it is automatically cast to the correct model class.

Licensed under the New BSD License.


## Features

* Models in querysets have the right class automatically
* All models subclassing a common base are stored in the same table
* Object types are stored in a 'type' field in the database
* No extra queries or joins to retrieve multiple types


## Usage:

An example says a bunch of words:

```python

# myapp/models.py

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
    mice_eaten = models.IntegerField(
        default = 0
        )

    def say_something(self):
        return "meoww"
```

Later:

```python
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
```

You can actually change the types of objects. Simply run an update query:

```python
Feline.objects.update(type='myapp.bigcat')
```

If you want to change the type of an object without refreshing it from the database, you can call ``recast``:

```python
kitty.recast(BigCat)
# or kitty.recast('myapp.bigcat')
kitty.save()
```


## Listing subclasses

Occasionally you might need to list the various subclasses of your abstract type.

One current use for this is connecting signals, since currently they don't fire on the base class (see [#1](https://github.com/craigds/django-typed-models/issues/1))

```python
    for sender in Animal.get_type_classes():
        post_save.connect(on_animal_saved, sender=sender)
```


## Django admin

If you plan to use typed models with Django admin, consider inheriting from typedmodels.admin.TypedModelAdmin.
This will hide the type field from subclasses admin by default, and allow to create new instances from the base class admin.

```python
from django.contrib import admin
from typedmodels.admin import TypedModelAdmin
from .models import Animal, Canine, Feline

@admin.register(Animal)
class AnimalAdmin(TypedModelAdmin):
    pass

@admin.register(Canine)
class CanineAdmin(TypedModelAdmin):
    pass

@admin.register(Feline)
class FelineAdmin(TypedModelAdmin):
    pass
```

## Limitations

* Since all objects are stored in the same table, all fields defined in subclasses are nullable.
* Fields defined on subclasses can only be defined on *one* subclass, unless the duplicate fields are exactly identical.


## Requirements

* Django 4.2+
* Python 3.9+
