"""This is the auxiliary package.

All classes and functions defined in auxiliary are imported here.
"""

__all__ = (
    '__version__',

    'IndexedEnum', 'MappingView', 'SequenceView', 'SetView',
    'SupportsLessThan', 'chunked', 'clip', 'const', 'distinct', 'maxima',
    'minima', 'next_or_none', 'prod', 'reverse_args', 'rotated', 'windowed',
)
__version__ = '1.0.1'

from auxiliary.utilities import (
    IndexedEnum, MappingView, SequenceView, SetView, SupportsLessThan, chunked,
    clip, const, distinct, maxima, minima, next_or_none, prod, reverse_args,
    rotated, windowed,
)
