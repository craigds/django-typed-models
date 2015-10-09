#!/usr/bin/env python
import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=('typedmodels',),
    MIDDLEWARE_CLASSES=(),
    DATABASES={
        'default': {'ENGINE': 'django.db.backends.sqlite3'}
    })

django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()


from django.core.management import call_command
call_command('test', 'typedmodels', verbosity=2)
