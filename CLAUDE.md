# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

django-typed-models is a Django package that provides single-table inheritance with automatic type-based downcasting. It allows storing different model subclasses in the same database table while automatically casting objects to their correct subclass when retrieved.

## Architecture

### Core Components

- **TypedModel**: Base abstract model that other models inherit from
- **TypedModelMetaclass**: Metaclass that handles proxy model creation and type registration  
- **TypedModelManager**: Custom manager that filters querysets by model type
- **TypedModelAdmin**: Django admin class for managing typed models

### Key Concepts

- **Base Class**: The concrete model that defines the database table (inherits from TypedModel)
- **Proxy Subclasses**: Type-specific models that are automatically created as Django proxy models
- **Type Registry**: Dict mapping type strings (app_label.model_name) to model classes
- **Auto-recasting**: Objects are automatically cast to correct subclass on retrieval

## Development Commands

### Testing
```bash
# Run tests using pytest
pytest --ds=test_settings typedmodels/tests.py

# Run tests with coverage
coverage run $(which pytest) --ds=test_settings typedmodels/tests.py
coverage report --omit=typedmodels/test*

# Run full test matrix (all Python/Django versions)
tox

# Run specific tox environment
tox -e py312-dj51
```

### Type Checking
```bash
# Run MyPy type checking
python -m mypy .

# Or via tox
tox -e mypy
```

### Linting
```bash
# Run flake8 (used in CI)
flake8 --select=E9,F63,F7,F82 .
```

## Important Implementation Details

### Field Constraints for Subclasses
All fields defined on TypedModel subclasses must be:
- Nullable (`null=True`)
- Have a default value
- Be a ManyToManyField

This is enforced by the metaclass and will raise FieldError if violated.

### Type Field Management
- Each subclass gets a unique type string: `{app_label}.{model_name}`
- Type choices are automatically populated on the base class
- The `type` field is indexed and required

### Proxy Model Behavior  
- Subclasses are automatically converted to proxy models
- Fields are contributed to the base class, not the proxy
- Querysets are filtered by type in the custom manager

### Serialization Patches
The code monkey-patches Django's Python and XML serializers to use the base class model name for TypedModel instances.