#!/usr/bin/env python
from setuptools import setup
from os.path import abspath, dirname, join


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


setup(
    name="django-typed-models",
    description="""Sane single table model inheritance for Django""",
    long_description=read_relative_file("README.rst"),
    version=read_relative_file("VERSION").strip(),
    author="Craig de Stigter",
    author_email="craig@destigter.nz",
    url="http://github.com/craigds/django-typed-models",
    packages=["typedmodels"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
)
