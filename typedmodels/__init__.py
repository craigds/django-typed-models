from __future__ import absolute_import
from .models import TypedModel

pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('django-typed-models')

VERSION = __version__ = distribution.version
