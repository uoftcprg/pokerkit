from __future__ import annotations

from collections import Hashable, Iterable, Iterator, Mapping, Sequence
from enum import Enum
from functools import cached_property, total_ordering, reduce
from numbers import Complex
from operator import mul
from typing import Any, TypeVar, Union


@total_ordering
class OrderedEnum(Enum):
    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.index < other.index
        else:
            return NotImplemented

    @cached_property
    def index(self) -> int:
        values: list[OrderedEnum] = list(type(self))

        return values.index(self)


_KT = TypeVar('_KT', bound=Hashable)
_VT_co = TypeVar('_VT_co', bound=Hashable, covariant=True)


class FrozenDict(Mapping[_KT, _VT_co], Hashable):
    def __init__(self, data: Union[Mapping[_KT, _VT_co], Iterable[tuple[_KT, _VT_co]]]):
        self.__map = dict(data)

        if not all(isinstance(value, Hashable) for value in self.__map.values()):
            raise ValueError('All values must be hashable types')

    def __hash__(self) -> int:
        return hash(frozenset(self.__map.items()))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FrozenDict):
            return self.__map == other.__map
        else:
            return NotImplemented

    def __getitem__(self, k: _KT) -> _VT_co:
        return self.__map[k]

    def __len__(self) -> int:
        return len(self.__map)

    def __iter__(self) -> Iterator[_KT]:
        return iter(self.__map)

    def __repr__(self) -> str:
        return f'FrozenDict({repr(self.__map)})'


T = TypeVar('T')


def window(iterable: Iterable[T], n: int) -> Iterable[Sequence[T]]:
    seq = list(iterable)
    return map(lambda i: seq[i:i + n], range(0, len(seq) - n + 1))


def rotate(s: Sequence[T], i: int) -> list[T]:
    return list(s[i:]) + list(s[:i])
