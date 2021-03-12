from abc import ABC
from collections.abc import Hashable, Iterable
from functools import total_ordering
from typing import Any

from auxiliary import SupportsLessThan

from pokertools.cards import Card


@total_ordering
class Hand(Hashable, SupportsLessThan):
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


class _LookupHand(Hand, ABC):
    """_LookupHand is the abstract base class for all lookup hands."""
    from pokertools._lookups import Lookup

    _lookup: Lookup

    def __init__(self, cards: Iterable[Card]):
        super().__init__(self._lookup.index(cards))


class StandardHand(_LookupHand):
    """StandardHand is the class for standard hands."""
    from pokertools._lookups import StandardLookup

    _lookup = StandardLookup()


class ShortHand(_LookupHand):
    """ShortHand is the class for short hands."""
    from pokertools._lookups import ShortLookup

    _lookup = ShortLookup()


class BadugiHand(_LookupHand):
    """BadugiHand is the class for Badugi hands."""
    from pokertools._lookups import BadugiLookup

    _lookup = BadugiLookup()


class LowballA5Hand(_LookupHand):
    """LowballA5Hand is the class for Ace-to-Five Lowball hands."""
    from pokertools._lookups import LowballA5Lookup

    _lookup = LowballA5Lookup()


class Lowball27Hand(_LookupHand):
    """Lowball27Hand is the class for Deuce-to-Seven Lowball hands."""
    from pokertools._lookups import Lowball27Lookup

    _lookup = Lowball27Lookup()
