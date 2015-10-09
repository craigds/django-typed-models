# Upgrade notes

Backward-incompatible changes for released versions are listed here (for 0.5 onwards.)

## 0.5

This import path no longer works, as recent Django changes make it impossible:

```
from typedmodels import TypedModel
```

Instead, use:

```
from typedmodels.models import TypedModel
```
