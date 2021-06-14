from abc import ABC
from collections.abc import Hashable
from functools import total_ordering


@total_ordering
class Hand(Hashable):
    """Hand is the class for hands.

    :param index: The index of this hand.
    """

    def __init__(self, index):
        self.__index = index

    def __eq__(self, other):
        if isinstance(other, Hand):
            return self.__index == other.__index
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.__index)

    def __lt__(self, other):
        if isinstance(other, Hand):
            return self.__index > other.__index
        else:
            return NotImplemented


class _LookupHand(Hand, ABC):
    _lookup = None

    def __init__(self, cards):
        super().__init__(self._lookup.get_index(cards))


class StandardHand(_LookupHand):
    """StandardHand is the class for standard hands."""
    from pokertools._lookups import StandardLookup as _StandardLookup

    _lookup = _StandardLookup()


class ShortHand(_LookupHand):
    """ShortHand is the class for short hands."""
    from pokertools._lookups import ShortLookup as _ShortLookup

    _lookup = _ShortLookup()


class BadugiHand(_LookupHand):
    """BadugiHand is the class for Badugi hands."""
    from pokertools._lookups import BadugiLookup as _BadugiLookup

    _lookup = _BadugiLookup()


class LowballA5Hand(_LookupHand):
    """LowballA5Hand is the class for Ace-to-Five Lowball hands."""
    from pokertools._lookups import LowballA5Lookup as _LowballA5Lookup

    _lookup = _LowballA5Lookup()


class Lowball27Hand(_LookupHand):
    """Lowball27Hand is the class for Deuce-to-Seven Lowball hands."""
    from pokertools._lookups import Lowball27Lookup as _Lowball27Lookup

    _lookup = _Lowball27Lookup()
