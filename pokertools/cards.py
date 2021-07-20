from enum import Enum, unique
from itertools import islice

from auxiliary import IndexedEnum, chunk, const, distinct


@unique
class Rank(IndexedEnum):
    """Rank is the enum class for ranks."""
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
class Suit(Enum):
    """Suit is the enum class for suits."""
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
    """Ranks is the enum class for tuples of ranks."""
    STANDARD = tuple(Rank)
    """The standard ranks (from deuce to ace)."""
    SHORT_DECK = tuple(Rank)[Rank.SIX.index:]
    """The short-deck ranks (from six to ace)."""
    ACE_LOW = (Rank.ACE,) + tuple(Rank)[:Rank.ACE.index]
    """The ace-low ranks (from ace to king)."""


class Card:
    """Card is the class for cards.

    :param rank: The optional rank of this card.
    :param suit: The optional suit of this card.
    """

    def __init__(self, rank, suit):
        self.__rank = rank
        self.__suit = suit

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.rank) ^ hash(self.suit)

    def __repr__(self):
        return self.rank.value + self.suit.value

    @property
    def rank(self):
        """Returns the rank of this card.

        :return: The rank of this card.
        """
        return self.__rank

    @property
    def suit(self):
        """Returns the suit of this card.

        :return: The suit of this card.
        """
        return self.__suit


class HoleCard(Card):
    """HoleCard is the class for hole cards.

    :param status: The status of this hole card. True if exposed, False otherwise.
    :param card: The card value.
    """

    def __init__(self, status, card):
        super().__init__(card.rank, card.suit)

        self.__status = status

    def __str__(self):
        return repr(self) if self.status else '??'

    @property
    def status(self):
        """Returns the status of this hole card.

        :return: True if this hole card is exposed, False otherwise.
        """
        return self.__status


def rainbow(cards):
    """Checks if all cards have a rainbow texture.

    Cards have a rainbow texture when their suits are all unique to each other.

    :param cards: The cards to check.
    :return: True if the cards have a rainbow texture, else False.
    """
    return distinct(map(Card.suit.fget, cards))


def suited(cards):
    """Checks if all cards are of the same suit.

    :param cards: The cards to check.
    :return: True if the cards are suited, else False.
    """
    return const(map(Card.suit.fget, cards))


def parse_card(card):
    """Parses the string of the card representation.

    :param card: The string of the card representation.
    :return: The parsed card.
    :raises ValueError: If the card-representation is invalid.
    """
    if len(card) == 2:
        rank, suit = card

        return Card(None if rank == '?' else Rank(rank), None if suit == '?' else Suit(suit))
    else:
        raise ValueError('Invalid card representation')


def parse_cards(cards):
    """Parses the string of card representations.

    :param cards: The string of card representations.
    :return: The parsed cards.
    :raises ValueError: If any card-representation is invalid.
    """
    return map(parse_card, chunk(cards, 2))


def parse_range(pattern):
    """Parses the supplied pattern.

    >>> from pokertools import parse_range
    >>> parse_range('AKo')
    frozenset({frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), ..., frozenset({Ks, Ac})})
    >>> parse_range('AKs')
    frozenset({frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})})
    >>> parse_range('AK')
    frozenset({frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), ..., frozenset({Kh, Ac})})
    >>> parse_range('AA')
    frozenset({frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), ..., frozenset({As, Ac})})
    >>> parse_range('QQ+')
    frozenset({frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), ..., frozenset({Qd, Qc})})
    >>> parse_range('QT+')
    frozenset({frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), ..., frozenset({Jh, Qc})})
    >>> parse_range('QsTs')
    frozenset({frozenset({Qs, Ts})})

    :param pattern: The supplied pattern to be parsed.
    :return: The parsed card sets.
    :raises ValueError: If the pattern cannot be parsed.
    """
    card_sets = set()

    if 2 <= len(pattern) <= 3 and pattern[-1] != '+':
        ranks, flag = tuple(map(Rank, pattern[:2])), pattern[2:]
        cards = set()

        for suit in Suit:
            cards.add(Card(ranks[0], suit))
            cards.add(Card(ranks[1], suit))

        for card_1 in cards:
            for card_2 in cards:
                if card_1.rank == ranks[0] and card_2.rank == ranks[1] and card_1 != card_2:
                    if not flag or (flag == 's' and card_1.suit == card_2.suit) \
                            or (flag == 'o' and card_1.suit != card_2.suit):
                        card_sets.add(frozenset({card_1, card_2}))
    elif 3 <= len(pattern) <= 4 and pattern[-1] == '+':
        ranks, flag = tuple(map(Rank, pattern[:2])), pattern[2:-1]

        if ranks[0] == ranks[1]:
            for rank in islice(Rank, ranks[0].index, None):
                card_sets |= parse_range(rank.value + rank.value + flag)
        else:
            for rank in islice(Rank, ranks[1].index, ranks[0].index):
                card_sets |= parse_range(ranks[0].value + rank.value + flag)
    else:
        card_sets.add(frozenset(parse_cards(pattern)))

    return frozenset(card_sets)
