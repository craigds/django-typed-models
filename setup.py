#!/usr/bin/env python
from distutils.core import setup

version = '0.2.1'

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
