# -*- coding: utf-8 -*-

import sys

text_type = str
if sys.version < '3':
    text_type = unicode


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    return meta("NewBase", bases, {})
