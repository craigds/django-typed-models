# Upgrade notes

Backward-incompatible changes for released versions are listed here (for 0.5 onwards.)

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
