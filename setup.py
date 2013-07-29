#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

version = '0.3.alpha'

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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: 3.3',
        'Topic :: Utilities'
    ],
)
