# How to Release django-typed-models

This document describes the release process for django-typed-models.

## Prerequisites

- Write access to the GitHub repository
- PyPI account with maintainer access to django-typed-models
- PyPI API token configured locally (or use `twine upload` with username/password)

## Release Checklist

### 1. Update CHANGES.md

Add a new section at the top of `CHANGES.md` for the new version:

```markdown
## X.Y.Z

* Brief description of changes ([#issue](link))
* Another change if applicable
```

Look at recent commits and PRs to identify what changed since the last release:
```bash
git log v0.15.1..HEAD --oneline
gh pr list --state merged --limit 20
```

### 2. Bump Version

Update the version in `typedmodels/__init__.py`:

```python
__version__ = "X.Y.Z"
```

Commit these changes:
```bash
git add CHANGES.md typedmodels/__init__.py
git commit -m "Bump version to X.Y.Z"
```

### 3. Verify Tests Pass in CI

Push to GitHub and ensure all CI checks pass:
```bash
git push origin master
```

Check the GitHub Actions at: https://github.com/craigds/django-typed-models/actions

Wait for all checks to pass:
- Linting (pre-commit)
- Type checking (mypy)
- Tests (multiple Python/Django versions)

### 4. Create and Push Git Tag

Create a tag for the release:
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Note: Use the `v` prefix for tags (e.g., `v0.15.2`).

### 5. Build the Package

Use [build](https://github.com/pypa/build) via `pyproject-build`:

Build the distribution packages:
```bash
pyproject-build
```

This creates:
- `dist/django_typed_models-X.Y.Z.tar.gz` (source distribution)
- `dist/django_typed_models-X.Y.Z-py3-none-any.whl` (wheel)

### 6. Upload to PyPI

Upload the built packages to PyPI:
```bash
twine upload dist/django_typed_models-X.Y.Z*
```

You'll be prompted for your PyPI credentials or API token.

Verify the upload at: https://pypi.org/project/django-typed-models/

### 7. Create GitHub Release

Create a release on GitHub:
```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Brief release notes here"
```

Or use the GitHub web UI:
1. Go to https://github.com/craigds/django-typed-models/releases/new
2. Select the tag you created
3. Title: `vX.Y.Z`
4. Description: Copy relevant section from CHANGES.md
5. Click "Publish release"

## Post-Release

Verify the release:
- Check PyPI page shows the new version
- Install in a test environment: `pip install django-typed-models==X.Y.Z`
- GitHub release is visible at releases page

## Troubleshooting

**Build fails**: Ensure `hatchling` is installed and pyproject.toml is valid

**PyPI upload fails**: Check your credentials/token and that the version doesn't already exist

**Tests failing in CI**: Fix issues before releasing - do not proceed with a failing build
