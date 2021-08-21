from abc import ABC
from collections.abc import Hashable, Iterator
from functools import total_ordering

from auxiliary import SupportsLessThan, distinct

from pokerface.cards import Card, rainbow


@total_ordering
class Hand(Hashable, SupportsLessThan, ABC):
    """The abstract base class for all hands."""
    ...


class IndexedHand(Hand, ABC):
    """The abstract base class for all indexed hands."""

    def __init__(self, index):
        self._index = index

    def __eq__(self, other):
        if type(self) == type(other):
            return self.index == other.index
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.index)

    @property
    def index(self):
        """Return the index of this indexed hand.

        :return: The index of this indexed hand.
        """
        return self._index


class HighIndexedHand(IndexedHand):
    """The abstract base class for all high indexed hands."""

    def __lt__(self, other):
        if type(self) == type(other):
            return self.index > other.index
        else:
            return NotImplemented


class LowIndexedHand(IndexedHand):
    """The abstract base class for all low indexed hands."""

    def __lt__(self, other):
        if type(self) == type(other):
            return self.index < other.index
        else:
            return NotImplemented


class LookupHandMixin(IndexedHand, ABC):
    """The abstract base class for all lookup hands.

    :param cards: The cards in this hand.
    :raises ValueError: If the cards do not form a valid hand.
    """

    _lookup = None

    def __init__(self, cards):
        super().__init__(self._lookup.get_index(cards))


class StandardHand(LookupHandMixin, HighIndexedHand):
    """The class for standard hands."""

    from pokerface._lookups import StandardLookup as _StandardLookup

    _lookup = _StandardLookup()


class ShortDeckHand(LookupHandMixin, HighIndexedHand):
    """The class for short-deck hands."""

    from pokerface._lookups import ShortDeckLookup as _ShortDeckLookup

    _lookup = _ShortDeckLookup()


class Lowball27Hand(LookupHandMixin, LowIndexedHand):
    """The class for Deuce-to-Seven Lowball hands."""

    from pokerface._lookups import StandardLookup as _Lowball27Lookup

    _lookup = _Lowball27Lookup()


class LowballA5Hand(LookupHandMixin, LowIndexedHand):
    """The class for Ace-to-Five Lowball hands."""

    from pokerface._lookups import LowballA5Lookup as _LowballA5Lookup

    _lookup = _LowballA5Lookup()


class BadugiHand(LookupHandMixin, LowIndexedHand):
    """The class for Badugi hands."""

    from pokerface._lookups import BadugiLookup as _BadugiLookup

    _lookup = _BadugiLookup()

    @classmethod
    def _is_valid(cls, cards):
        return distinct(map(Card.rank.fget, cards)) and rainbow(cards)

    def __init__(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        if not self._is_valid(cards):
            raise ValueError('not a badugi hand')

        super().__init__(cards)
