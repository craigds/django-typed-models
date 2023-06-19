INSTALLED_APPS = (
    "typedmodels",
    "django.contrib.contenttypes",
    "second_testapp",  # purposefully before to test related models with lazy loading
    "testapp",
)
MIDDLEWARE_CLASSES = ()
DATABASES = {"default": {"NAME": ":memory:", "ENGINE": "django.db.backends.sqlite3"}}
SECRET_KEY = "abc123"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# avoid RemovedInDjango50Warning when running tests:
USE_TZ = True
