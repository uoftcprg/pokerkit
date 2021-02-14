from __future__ import annotations

from enum import unique
from functools import total_ordering
from typing import Any, Union

from pokertools.utils import OrderedEnum


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


@unique
class Suit(OrderedEnum):
    """Suit is the enum for suits."""
    CLUB = 'c'
    DIAMOND = 'd'
    HEART = 'h'
    SPADE = 's'


@total_ordering
class Card:
    """Card is the base class for all cards."""

    def __init__(self, rank: Rank, suit: Suit):
        self.__rank = rank
        self.__suit = suit

    def __repr__(self) -> str:
        return self.rank.value + self.suit.value

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return self.suit < other.suit if self.rank == other.rank else self.rank < other.rank
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.rank) ^ hash(self.suit)

    @property
    def rank(self) -> Rank:
        """
        :return: the rank of this card
        """
        return self.__rank

    @property
    def suit(self) -> Suit:
        """
        :return: the suit of this card
        """
        return self.__suit


class HoleCard(Card):
    """HoleCard is the class for hole cards."""

    def __init__(self, card_like: CardLike, status: bool):
        card = parse_card(card_like)

        super().__init__(card.rank, card.suit)

        self.__status = status

    def __repr__(self) -> str:
        return super().__repr__() if self.status else '??'

    @property
    def status(self) -> bool:
        """
        :return: True if this hole card is exposed, else False
        """
        return self.__status


CardLike = Union[str, Card]


def parse_card(card: CardLike) -> Card:
    """Parses the card-like object.

    :param card: the card-like object.
    :return: the parsed card
    """
    if isinstance(card, str) and len(card) == 2:
        return Card(Rank(card[0]), Suit(card[1]))
    elif isinstance(card, Card):
        return card
    else:
        raise TypeError('Invalid card type')
