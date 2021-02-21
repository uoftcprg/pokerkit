from abc import ABC
from collections import Hashable
from functools import total_ordering
from typing import Any

from pokertools._lookups import Lookup, StandardLookup
from pokertools.cards import Card


@total_ordering
class Hand(Hashable, ABC):
    """Hand is the base class for all hands."""

    def __init__(self, index: int):
        self.__index = index

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Hand):
            return self.__index > other.__index
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Hand):
            return self.__index == other.__index
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__index)


class LookupHand(Hand):
    """LookupHand is the abstract base class for all lookup hands."""
    _lookup: Lookup

    def __init__(self, *cards: Card):
        super().__init__(self._lookup.index(*cards))


class StandardHand(LookupHand):
    """StandardHand is the base class for all standard hands."""
    _lookup = StandardLookup()
