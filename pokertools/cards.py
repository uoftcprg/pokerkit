from __future__ import annotations

from enum import unique
from functools import total_ordering
from typing import Any, Final

from auxiliary import OrderedEnum, SupportsLessThan


@unique
class Rank(OrderedEnum):
    """Rank is the enum class for ranks."""
    TWO = '2'
    '''The rank of 2.'''
    THREE = '3'
    '''The rank of 3.'''
    FOUR = '4'
    '''The rank of 4.'''
    FIVE = '5'
    '''The rank of 5.'''
    SIX = '6'
    '''The rank of 6.'''
    SEVEN = '7'
    '''The rank of 7.'''
    EIGHT = '8'
    '''The rank of 8.'''
    NINE = '9'
    '''The rank of 9.'''
    TEN = 'T'
    '''The rank of 10.'''
    JACK = 'J'
    '''The rank of Jacks.'''
    QUEEN = 'Q'
    '''The rank of Queens.'''
    KING = 'K'
    '''The rank of Kings.'''
    ACE = 'A'
    '''The rank of Aces.'''


STANDARD_RANKS = tuple(Rank)
'''The standard ranks (from deuce to ace).'''
SHORT_DECK_RANKS = tuple(Rank)[Rank.SIX.index:]
'''The short-deck ranks (from six to ace).'''
ACE_LOW_RANKS = (Rank.ACE,) + tuple(Rank)[:Rank.ACE.index]
'''The ace-low ranks (from ace to king).'''


@unique
class Suit(OrderedEnum):
    """Suit is the enum class for suits."""
    CLUB = 'c'
    '''The suit of clubs.'''
    DIAMOND = 'd'
    '''The suit of diamonds.'''
    HEART = 'h'
    '''The suit of hearts.'''
    SPADE = 's'
    '''The suit of spades.'''


@total_ordering
class Card(SupportsLessThan):
    """Card is the class for cards."""

    def __init__(self, rank: Rank, suit: Suit):
        self.rank: Final = rank
        '''The rank of this card.'''
        self.suit: Final = suit
        '''The suit of this card.'''

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.rank) ^ hash(self.suit)

    def __repr__(self) -> str:
        return self.rank.value + self.suit.value

    def __lt__(self, other: Card) -> bool:
        if isinstance(other, Card):
            return self.suit < other.suit if self.rank == other.rank else self.rank < other.rank
        else:
            return NotImplemented


class HoleCard(Card):
    """HoleCard is the class for hole cards."""

    def __init__(self, status: bool, card: Card):
        super().__init__(card.rank, card.suit)

        self.status: Final = status
        '''The status of this hole card. True if exposed, False otherwise.'''

    def __repr__(self) -> str:
        return super().__repr__() if self.status else '??'
