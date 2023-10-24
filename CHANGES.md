# Upgrade notes

Backward-incompatible changes for released versions are listed here (for 0.5 onwards.)

## 0.14

* Added support for Django 4.2 and 5.0.
* Added support for Python 3.12.
* Dropped the `VERSION` and `__version__` attributes. To check the version of the package, use `importlib.metadata.version("django-typed-models")` ([docs](https://docs.python.org/3/library/importlib.metadata.html#distribution-versions) /
  [backport](https://pypi.org/project/importlib-metadata/)).

## 0.13

* Dropped support for Django 3.1.
* Some apps using typedmodels may generate new migrations, due to [#68](https://github.com/craigds/django-typed-models/pull/68) - these are harmless and don't actually change anything in your database.

## 0.12

No backward-incompatible changes. Added support for Django 4.x

## 0.11

* Dropped support for djangoes older than 3.1
* Fields on concrete typed models must now have `null=True`. Previously the null=True was added automatically ([#39](https://github.com/craigds/django-typed-models/issues/39))
* If you defer the `type` field (via `queryset.only()` or `queryset.defer()`), typedmodels will no longer automatically cast the model instances from that queryset.

## 0.10

* Dropped Python 2 support
* Added support for django 2.2 and 3.0, and dropped support for <2.2.

## 0.9

Removed shims for unsupported django versions (now supports 1.11+)

## 0.8

Fields defined in typed subclasses no longer get `null=True` added silently.

* If the field has a default value, we will use the default value instead of `None` for other types. You may need to either add `null=True` yourself, or create a migration for your app.
* If the field doesn't have a default value, a warning is logged and the `null=True` is added implicitly. This will be removed in typedmodels 0.9.

## 0.7

This release removes some magic around manager setup. Managers are now inherited using the normal Django mechanism.

If you are using a custom default manager on a TypedModel subclass, you need to make sure it is a subclass
of TypedModelManager. Otherwise type filtering will not work as expected.

## 0.5

This import path no longer works, as recent Django changes make it impossible:

```
from typedmodels import TypedModel
```

Instead, use:

```
from typedmodels.models import TypedModel
```
