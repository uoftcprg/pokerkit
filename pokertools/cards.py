from __future__ import annotations

from enum import unique
from functools import total_ordering
from typing import Any, Final

from auxiliary import OrderedEnum, SupportsLessThan


@unique
class Rank(OrderedEnum):
    """Rank is the enum for ranks."""
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'


STANDARD_RANKS = tuple(Rank)
SHORT_RANKS = tuple(Rank)[Rank.SIX.index:]
ACE_LOW_RANKS = (Rank.ACE,) + tuple(Rank)[:Rank.ACE.index]


@unique
class Suit(OrderedEnum):
    """Suit is the enum for suits."""
    CLUB = 'c'
    DIAMOND = 'd'
    HEART = 'h'
    SPADE = 's'


@total_ordering
class Card(SupportsLessThan):
    """Card is the class for cards."""

    def __init__(self, rank: Rank, suit: Suit):
        self.rank: Final = rank
        self.suit: Final = suit

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

    def __init__(self, card: Card, status: bool):
        super().__init__(card.rank, card.suit)

        self.status: Final = status

    def __repr__(self) -> str:
        return super().__repr__() if self.status else '??'
