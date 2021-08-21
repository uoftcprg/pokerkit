from collections.abc import Hashable
from enum import Enum, unique
from functools import total_ordering

from auxiliary import IndexedEnum, SupportsLessThan, chunked, const, distinct


@unique
class Rank(IndexedEnum):
    """The enum class for ranks."""

    TWO = '2'
    """The rank of 2."""
    THREE = '3'
    """The rank of 3."""
    FOUR = '4'
    """The rank of 4."""
    FIVE = '5'
    """The rank of 5."""
    SIX = '6'
    """The rank of 6."""
    SEVEN = '7'
    """The rank of 7."""
    EIGHT = '8'
    """The rank of 8."""
    NINE = '9'
    """The rank of 9."""
    TEN = 'T'
    """The rank of 10."""
    JACK = 'J'
    """The rank of Jacks."""
    QUEEN = 'Q'
    """The rank of Queens."""
    KING = 'K'
    """The rank of Kings."""
    ACE = 'A'
    """The rank of Aces."""


@unique
class Suit(IndexedEnum):
    """The enum class for suits."""

    CLUB = 'c'
    """The suit of clubs."""
    DIAMOND = 'd'
    """The suit of diamonds."""
    HEART = 'h'
    """The suit of hearts."""
    SPADE = 's'
    """The suit of spades."""


@unique
class Ranks(Enum):
    """The enum class for tuples of ranks."""

    STANDARD = tuple(Rank)
    """The standard ranks (from deuce to ace)."""
    SHORT_DECK = tuple(Rank)[Rank.SIX.index:]
    """The short-deck ranks (from six to ace)."""
    ACE_LOW = (Rank.ACE,) + tuple(Rank)[:Rank.ACE.index]
    """The ace-low ranks (from ace to king)."""


@total_ordering
class Card(SupportsLessThan, Hashable):
    """The class for cards.

    :param rank: The optional rank of this card.
    :param suit: The optional suit of this card.
    """

    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        elif self.suit == other.suit:
            return self.rank < other.rank
        else:
            return self.suit < other.suit

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.rank) ^ hash(self.suit)

    def __repr__(self):
        rank_str = '?' if self.rank is None else self.rank.value
        suit_str = '?' if self.suit is None else self.suit.value

        return rank_str + suit_str

    @property
    def rank(self):
        """Return the rank of this card.

        :return: The rank of this card.
        """
        return self._rank

    @property
    def suit(self):
        """Return the suit of this card.

        :return: The suit of this card.
        """
        return self._suit


class HoleCard(Card):
    """The class for hole cards.

    :param status: ``True`` if this hole card is exposed, ``False``
                   otherwise.
    :param card: The card value.
    """

    def __init__(self, status, card):
        super().__init__(card.rank, card.suit)

        self._status = status

    def __str__(self):
        return repr(self) if self.status else '??'

    @property
    def status(self):
        """Return the status of this hole card.

        :return: ``True`` if this hole card is exposed, ``False``
                 otherwise.
        """
        return self._status

    def show(self):
        """Return the shown version of this hole card.

        The operation is not done in-place.

        :return: The shown version of this hole card.
        """
        return HoleCard(True, self)


def parse_cards(cards):
    """Parse the string of card representations.

    :param cards: The string of card representations.
    :return: The parsed cards.
    :raises ValueError: If any card-representation is invalid.
    """
    return map(parse_card, chunked(cards, 2))


def parse_card(card):
    """Parse the string of the card representation.

    :param card: The string of the card representation.
    :return: The parsed card.
    :raises ValueError: If the card-representation is invalid.
    """
    if len(card) != 2:
        raise ValueError('invalid card representation')

    rank_str, suit_str = card
    rank = None if rank_str == '?' else Rank(rank_str)
    suit = None if suit_str == '?' else Suit(suit_str)

    return Card(rank, suit)


def rainbow(cards):
    """Check if all cards have a rainbow texture.

    Cards have a rainbow texture when their suits are all unique to each
    other.

    :param cards: The cards to check.
    :return: ``True`` if the cards have a rainbow texture, else
             ``False``.
    """
    return distinct(map(Card.suit.fget, cards))


def suited(cards):
    """Check if all cards are of the same suit.

    :param cards: The cards to check.
    :return: ``True`` if the cards are suited, else ``False``.
    """
    return const(map(Card.suit.fget, cards))
