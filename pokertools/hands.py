from abc import ABC, abstractmethod
from collections.abc import Hashable
from functools import total_ordering


@total_ordering
class Hand(Hashable, ABC):
    """Hand is the abstract base class for all hands."""

    @abstractmethod
    def __lt__(self, other): ...


class IndexedHand(Hand, ABC):
    """IndexedHand is the abstract base class for all indexed hands."""

    def __init__(self, index):
        self._index = index

    def __eq__(self, other):
        if type(self) == type(other):
            return self._index == other._index
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self._index)


class HighIndexedHand(IndexedHand, ABC):
    """HighIndexedHand is the abstract base class for all high indexed hands."""

    def __lt__(self, other):
        if type(self) == type(other):
            return self._index > other._index
        else:
            return NotImplemented


class LowIndexedHand(IndexedHand, ABC):
    """LowIndexedHand is the abstract base class for all low indexed hands."""

    def __lt__(self, other):
        if type(self) == type(other):
            return self._index < other._index
        else:
            return NotImplemented


class LookupHandMixin(IndexedHand, ABC):
    """LookupHandMixin is the abstract base class for all lookup hands."""
    _lookup = None

    def __init__(self, cards):
        super().__init__(self._lookup.get_index(cards))


class StandardHand(LookupHandMixin, HighIndexedHand):
    """StandardHand is the class for standard hands."""
    from pokertools._lookups import StandardLookup as _StandardLookup

    _lookup = _StandardLookup()


class ShortDeckHand(LookupHandMixin, HighIndexedHand):
    """ShortDeckHand is the class for short-deck hands."""
    from pokertools._lookups import ShortDeckLookup as _ShortDeckLookup

    _lookup = _ShortDeckLookup()


class BadugiHand(LookupHandMixin, LowIndexedHand):
    """BadugiHand is the class for Badugi hands."""
    from pokertools._lookups import BadugiLookup as _BadugiLookup

    _lookup = _BadugiLookup()


class LowballA5Hand(LookupHandMixin, LowIndexedHand):
    """LowballA5Hand is the class for Ace-to-Five Lowball hands."""
    from pokertools._lookups import LowballA5Lookup as _LowballA5Lookup

    _lookup = _LowballA5Lookup()


class Lowball27Hand(LookupHandMixin, LowIndexedHand):
    """Lowball27Hand is the class for Deuce-to-Seven Lowball hands."""
    from pokertools._lookups import StandardLookup as _Lowball27Lookup

    _lookup = _Lowball27Lookup()
