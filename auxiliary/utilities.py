"""This module implements all the classes and functions in Auxiliary."""

from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterator, Mapping, Sequence, Set
from enum import Enum
from functools import reduce, total_ordering
from operator import mul


@total_ordering
class IndexedEnum(Enum):
    """The enum class for all ordered enums.

    The members of indexed enums have an :attr:`index` indicating the
    ordinal of each member. They can be compared with others by their
    indices.

    Derive from this class to define new indexed enumerations.

    >>> class Status(IndexedEnum):
    ...     DEBUG = 'Debug:'
    ...     INFO = 'By the way...'
    ...     WARNING = 'Not good,'
    ...     ERROR = 'Terrible!'
    ...
    >>> Status.INFO
    <Status.INFO: 'By the way...'>
    >>> Status.WARNING.index
    2
    >>> Status.INFO < Status.ERROR
    True
    >>> Status.DEBUG > Status.WARNING
    False
    """

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.index < other.index
        else:
            return NotImplemented

    @property
    def index(self):
        """Return the index of this indexed enum element.

        The index corresponds to the ordinal of the enum member.

        >>> class Number(IndexedEnum):
        ...     ZERO = 0
        ...     ONE = 1
        ...     TWO = 2
        ...     THREE = 3
        ...
        >>> Number.TWO.index
        2
        >>> Number.ONE.index
        1

        :return: The index of this indexed enum element.
        """
        return tuple(type(self)).index(self)


class SupportsLessThan(ABC):
    """The protocol for types that support the less than comparison
    operator.

    :class:`SupportsLessThan` implements subclass checks for any class
    that implements a less than comparison method, in addition to the
    instance checks for their instances.

    >>> isinstance(3, SupportsLessThan)
    True
    >>> isinstance(object, SupportsLessThan)
    False
    >>> issubclass(float, SupportsLessThan)
    True
    >>> class WrappedValue(SupportsLessThan):
    ...     def __init__(self, value):
    ...         self.value = value
    ...
    ...     def __lt__(self, other):
    ...         if isinstance(other, WrappedValue):
    ...             return self.value < other.value
    ...         else:
    ...             return NotImplemented
    ...
    >>> x, y = WrappedValue(3), WrappedValue(10)
    >>> x < y
    True
    >>> isinstance(3, WrappedValue)
    False
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is SupportsLessThan:
            return subclass.__lt__ != object.__lt__
        else:
            return NotImplemented

    @abstractmethod
    def __lt__(self, other):
        ...


class MappingView(Mapping):
    """The class for mapping views.

    This class serves as a view for mappings like dictionaries. Changes
    made on the original mapping argument with which a view was created
    will change the view as well.

    >>> mapping = {1: 'one', 2: 'two', 3: 'three'}
    >>> view = MappingView(mapping)
    >>> view
    MappingView({1: 'one', 2: 'two', 3: 'three'})
    >>> view[1]
    'one'
    >>> mapping[4] = 'four'
    >>> view
    MappingView({1: 'one', 2: 'two', 3: 'three', 4: 'four'})
    """

    def __init__(self, mapping):
        self.__mapping = mapping

    def __getitem__(self, k):
        return self.__mapping[k]

    def __len__(self):
        return len(self.__mapping)

    def __iter__(self):
        return iter(self.__mapping)

    def __repr__(self):
        return f'MappingView({repr(self.__mapping)})'


class SequenceView(Sequence):
    """The class for sequence views.

    This class serves as a view for sequences like lists and tuples.
    Changes made on the original sequence argument with which a view
    was created will change the view as well.

    >>> sequence = [1, 2, 3, 4, 5]
    >>> view = SequenceView(sequence)
    >>> view
    SequenceView([1, 2, 3, 4, 5])
    >>> view[0]
    1
    >>> sequence.insert(0, 0)
    >>> view
    SequenceView([0, 1, 2, 3, 4, 5])
    >>> view[0]
    0
    """

    def __init__(self, sequence):
        self.__sequence = sequence

    def __getitem__(self, i):
        return self.__sequence[i]

    def __len__(self):
        return len(self.__sequence)

    def __repr__(self):
        return f'SequenceView({repr(self.__sequence)})'


class SetView(Set):
    """The class for set views.

    This class serves as a view for sets like sets or frozensets.
    Changes made on the original set argument with which a view was
    created will change the view as well.

    >>> set_ = {1, 2, 3, 4, 5}
    >>> view = SetView(set_)
    >>> view
    SetView({1, 2, 3, 4, 5})
    >>> 0 in view
    False
    >>> set_.add(0)
    >>> view
    SetView({0, 1, 2, 3, 4, 5})
    >>> 0 in view
    True
    """

    def __init__(self, set_):
        self.__set = set_

    def __contains__(self, x):
        return x in self.__set

    def __len__(self):
        return len(self.__set)

    def __iter__(self):
        return iter(self.__set)

    def __repr__(self):
        return f'SetView({repr(self.__set)})'


def distinct(iterable):
    """Check if all elements inside the iterable are unique to each
    other.

    If the iterable is empty, ``True`` is returned.

    >>> distinct((1, 3, 5))
    True
    >>> distinct((1, 3, 3, 5))
    False
    >>> distinct([])
    True

    :param iterable: The iterable.
    :return: ``True`` if all elements are unique, else ``False``.
    """
    if not isinstance(iterable, Sequence):
        iterable = tuple(iterable)

    if not iterable:
        return True
    elif all(map(Hashable.__instancecheck__, iterable)):
        return len(iterable) == len(set(iterable))
    elif all(map(SupportsLessThan.__instancecheck__, iterable)):
        for x, y in windowed(sorted(iterable), 2):
            if x == y:
                return False

        return True
    else:
        for i in range(len(iterable)):
            for j in range(i + 1, len(iterable)):
                if iterable[i] == iterable[j]:
                    return False

        return True


def const(iterable):
    """Check if all elements inside the iterable are equal to each
    other.

    If the iterable is empty, ``True`` is returned.

    >>> const((0, 0, 0, 0))
    True
    >>> const([1, 1, 1, 3, 1])
    False
    >>> const({})
    True

    :param iterable: The iterable to check.
    :return: ``True`` if all elements are equal, else ``False``.
    """
    iterable = iter(iterable)

    try:
        first_value = next(iterable)
    except StopIteration:
        return True

    for value in iterable:
        if value != first_value:
            return False

    return True


def chunked(iterable, width):
    """Chunk the iterable by the given width.

    >>> message = 'Hello, world!'
    >>> for substr in chunked(message, 4):
    ...     print(substr)
    ...
    Hell
    o, w
    orld
    !

    :param iterable: The iterable to chunk.
    :param width: The width of the chunks.
    :return: The chunks.
    """
    return windowed(iterable, width, width, True)


def windowed(iterable, width, step=1, partial_=False):
    """Yield the sliding window views of the supplied iterable.

    >>> message = 'Hello!'
    >>> for substr in windowed(message, 3):
    ...     print(substr)
    ...
    Hel
    ell
    llo
    lo!
    >>> for substr in windowed(message, 3, 2, True):
    ...     print(substr)
    ...
    Hel
    llo
    o!

    :param iterable: The values to generate the window views on.
    :param width: The sliding window width.
    :param step: The step of the window views, defaults to ``1``.
    :param partial_: Allow partial views, defaults to ``False``.
    :return: The window views.
    """
    if not isinstance(iterable, Sequence):
        iterable = tuple(iterable)

    stop = len(iterable) if partial_ else len(iterable) - width + 1

    for i in range(0, stop, step):
        yield iterable[i: i + width]


def rotated(iterable, index):
    """Return a rotated sequence of the iterable by the index.

    >>> rotated('hello', 2)
    'llohe'
    >>> rotated(range(5), -1)
    (4, 0, 1, 2, 3)

    :param iterable: The iterable to rotate.
    :param index: The index of rotation.
    :return: The rotated sequence.
    """
    if type(iterable) not in (list, tuple, str):
        iterable = tuple(iterable)

    return iterable[index:] + iterable[:index]


def prod(values, start=1):
    """Multiply the supplied values together and return the product.

    >>> prod(range(1, 5))
    24
    >>> prod(())
    1

    :param values: The values to multiply.
    :param start: The start value, defaults to ``1``.
    :return: The product of the supplied values.
    """
    return reduce(mul, values, start)


def clip(value, lower, upper):
    """Clip the value by the given interval.

    >>> clip(2, 3, 6)
    3
    >>> clip(4, 2, 10)
    4

    :param value: The value to be bound.
    :param lower: The lower limit.
    :param upper: The upper limit.
    :return: The clipped value.
    :raises ValueError: If the lower bound is greater than the upper
                        bound.
    """
    if upper < lower:
        raise ValueError('lower bound exceeds upper bound')
    elif value < lower:
        return lower
    elif upper < value:
        return upper

    return value


def next_or_none(iterator):
    """Consume the iterator and return the yielded value, or ``None``,
    if all elements in the iterator are already consumed.

    >>> it = iter((1, 2))
    >>> print(next_or_none(it))
    1
    >>> print(next_or_none(it))
    2
    >>> print(next_or_none(it))
    None

    :param iterator: The iterator to optionally consume.
    :return: The consumed value if possible, else ``None``.
    """
    try:
        return next(iterator)
    except StopIteration:
        return None


def reverse_args(function):
    """Return a new function that, when invoked, reverses the arguments
    and passes it to the supplied function along with any keyword
    arguments.

    >>> reverse_print = reverse_args(print)
    >>> reverse_print('Hello,', 'world!')
    world! Hello,

    :param function: The function to wrap.
    :return: The wrapped function.
    """
    return lambda *args, **kwargs: function(*reversed(args), **kwargs)


def maxima(iterable, key=lambda argument: argument):
    """Return the maxima of the iterable.

    Maxima are values that are equal to the maximum value of the
    iterable.

    >>> tuple(maxima((1, 3, 3.0, 2, 3)))
    (3, 3.0, 3)

    :param iterable: The iterable to operate on.
    :param key: The key function, defaults to a constant function.
    :return: The maxima.
    """
    if isinstance(iterable, Iterator):
        iterable = tuple(iterable)

    try:
        max_key = max(map(key, iterable))
    except ValueError:
        return

    for value in iterable:
        if key(value) == max_key:
            yield value


def minima(iterable, key=lambda argument: argument):
    """Return the minima of the iterable.

    Minima are values that are equal to the minimum value of the
    iterable.

    >>> tuple(minima((1, 3, 3.0, 2, 1.0)))
    (1, 1.0)

    :param iterable: The iterable to operate on.
    :param key: The key function, defaults to a constant function.
    :return: The minima.
    """
    if isinstance(iterable, Iterator):
        iterable = tuple(iterable)

    try:
        min_key = min(map(key, iterable))
    except ValueError:
        return

    for value in iterable:
        if key(value) == min_key:
            yield value
