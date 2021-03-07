from abc import ABC
from collections import Hashable, Iterable
from functools import total_ordering
from typing import Any

from pokertools._lookups import Lookup, ShortLookup, StandardLookup
from pokertools.cards import Card


@total_ordering
class Hand(Hashable):
    """Hand is the class for hands."""

    def __init__(self, index: int):
        self.__index = index

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Hand):
            return self.__index == other.__index
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__index)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Hand):
            return self.__index > other.__index
        else:
            return NotImplemented


class LookupHand(Hand, ABC):
    """LookupHand is the abstract base class for all lookup hands."""
    _lookup: Lookup

    def __init__(self, cards: Iterable[Card]):
        super().__init__(self._lookup.index(cards))


class StandardHand(LookupHand):
    """StandardHand is the class for standard hands."""
    _lookup = StandardLookup()


class ShortHand(LookupHand):
    """ShortHand is the class for short hands."""
    _lookup = ShortLookup()
