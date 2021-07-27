from abc import ABC
from collections.abc import Hashable, Iterator
from functools import total_ordering

from auxiliary import SupportsLessThan, distinct

from pokertools.cards import Card, rainbow


@total_ordering
class Hand(Hashable, SupportsLessThan, ABC):
    """Hand is the abstract base class for all hands."""
    ...


class IndexedHand(Hand, ABC):
    """IndexedHand is the abstract base class for all indexed hands."""

    def __init__(self, index):
        self.__index = index

    def __eq__(self, other):
        return self.__index == other.__index if type(self) == type(other) else NotImplemented

    def __hash__(self):
        return hash(self.__index)

    @property
    def index(self):
        """Returns the index of this indexed hand.

        :return: The index of this indexed hand.
        """
        return self.__index


class HighIndexedHand(IndexedHand):
    """HighIndexedHand is the abstract base class for all high indexed hands."""

    def __lt__(self, other):
        return self.index > other.index if type(self) == type(other) else NotImplemented


class LowIndexedHand(IndexedHand):
    """LowIndexedHand is the abstract base class for all low indexed hands."""

    def __lt__(self, other):
        return self.index < other.index if type(self) == type(other) else NotImplemented


class LookupHandMixin(IndexedHand, ABC):
    """LookupHandMixin is the abstract base class for all lookup hands.

    :param cards: The cards in this hand.
    :raises ValueError: If the cards do not form a valid hand.
    """
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


class Lowball27Hand(LookupHandMixin, LowIndexedHand):
    """Lowball27Hand is the class for Deuce-to-Seven Lowball hands."""
    from pokertools._lookups import StandardLookup as _Lowball27Lookup

    _lookup = _Lowball27Lookup()


class LowballA5Hand(LookupHandMixin, LowIndexedHand):
    """LowballA5Hand is the class for Ace-to-Five Lowball hands."""
    from pokertools._lookups import LowballA5Lookup as _LowballA5Lookup

    _lookup = _LowballA5Lookup()


class BadugiHand(LookupHandMixin, LowIndexedHand):
    """BadugiHand is the class for Badugi hands."""
    from pokertools._lookups import BadugiLookup as _BadugiLookup

    _lookup = _BadugiLookup()

    @classmethod
    def _is_valid(cls, cards):
        return distinct(map(Card.rank.fget, cards)) and rainbow(cards)

    def __init__(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        if not self._is_valid(cards):
            raise ValueError('Not a valid Badugi hand')

        super().__init__(cards)
