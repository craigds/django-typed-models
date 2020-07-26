

pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('django-typed-models')

VERSION = __version__ = distribution.version
