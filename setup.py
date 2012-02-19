#!/usr/bin/env python
import os
import sys
from distutils.core import setup

# Dynamically calculate the version based on typedmodels.VERSION
# .. but first set a settings module so this import doesnt throw a hissy
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
sys.path.insert(0, os.path.dirname(__file__))
version_tuple = __import__('typedmodels').VERSION
version = ".".join([str(v) for v in version_tuple])

setup(
    name='django-typed-models',
    description='''Sane single table model inheritance for Django''',
    version=version,
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    url='http://github.com/craigds/django-typed-models',
    packages=['typedmodels'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
