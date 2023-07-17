""":mod:`pokerkit.utilities` implements classes related to poker
utilities.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from enum import Enum, unique
from functools import partial
from itertools import product, starmap
from operator import is_not
from typing import Any


@unique
class Rank(str, Enum):
    """The enum class for ranks.

    A card of lower rank is said to be less than that of a higher rank.
    The ordering of the ranks is decided in accordance to the rules of
    the poker variant being played.

    >>> Rank.DEUCE
    <Rank.DEUCE: '2'>
    >>> Rank('2')
    <Rank.DEUCE: '2'>
    >>> Rank.DEUCE.value
    '2'
    >>> Rank.DEUCE.name
    'DEUCE'
    """

    ACE: str = 'A'
    """The rank of aces."""
    DEUCE: str = '2'
    """The rank of deuces."""
    TREY: str = '3'
    """The rank of treys."""
    FOUR: str = '4'
    """The rank of fours."""
    FIVE: str = '5'
    """The rank of fives."""
    SIX: str = '6'
    """The rank of sixes."""
    SEVEN: str = '7'
    """The rank of sevens."""
    EIGHT: str = '8'
    """The rank of eights."""
    NINE: str = '9'
    """The rank of nines."""
    TEN: str = 'T'
    """The rank of tens."""
    JACK: str = 'J'
    """The rank of Jacks."""
    QUEEN: str = 'Q'
    """The rank of Queens."""
    KING: str = 'K'
    """The rank of Kings."""


@unique
class RankOrder(tuple[Rank], Enum):
    """The enum class for tuples of ranks.

    Poker variants order the ranks differently between each other. Most
    games use deuce to ace ordering which is defined here as
    :attr:`RankOrder.ROTATED`.

    >>> len(RankOrder.ROTATED)
    13
    >>> RankOrder.ROTATED[0]
    <Rank.DEUCE: '2'>
    >>> RankOrder.ROTATED[-1]
    <Rank.ACE: 'A'>

    Short-deck hold'em uses its own ranking which eliminates deuces,
    treys, fours, and fives, defined here as
    :attr:`RankOrder.SHORT_DECK_HOLDEM`.

    >>> len(RankOrder.SHORT_DECK_HOLDEM)
    9
    >>> RankOrder.SHORT_DECK_HOLDEM[0]
    <Rank.SIX: '6'>
    >>> RankOrder.SHORT_DECK_HOLDEM[-1]
    <Rank.ACE: 'A'>

    In some draw games, Ace is considered to be the lowest rank. This
    ordering is accessible via :attr:`RankOrder.STANDARD`.

    >>> len(RankOrder.STANDARD)
    13
    >>> RankOrder.STANDARD[0]
    <Rank.ACE: 'A'>
    >>> RankOrder.STANDARD[-1]
    <Rank.KING: 'K'>
    """

    ROTATED: tuple[Rank, ...] = (
        Rank.DEUCE,
        Rank.TREY,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
        Rank.NINE,
        Rank.TEN,
        Rank.JACK,
        Rank.QUEEN,
        Rank.KING,
        Rank.ACE,
    )
    """The rotated ranks (from deuce to ace).

    This is used in:
    - "Big O"
    - "Big O" hi-low eight or better
    - deuce to seven single draw lowball
    - deuce to seven triple draw lowball
    - Omaha hi-low eight or better
    - Omaha hold'em
    - seven card stud
    - seven card stud hi-low eight or better
    - seven card stud hi-low regular
    - Texas hold'em
    - et cetera
    """
    SHORT_DECK_HOLDEM: tuple[Rank, ...] = (
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
        Rank.NINE,
        Rank.TEN,
        Rank.JACK,
        Rank.QUEEN,
        Rank.KING,
        Rank.ACE,
    )
    """The short-deck hold'em ranks (from six to ace)."""
    STANDARD: tuple[Rank, ...] = (
        Rank.ACE,
        Rank.DEUCE,
        Rank.TREY,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
        Rank.NINE,
        Rank.TEN,
        Rank.JACK,
        Rank.QUEEN,
        Rank.KING,
    )
    """The standard ranks (from ace to king).

    This is used in:
    - ace to five single draw lowball
    - ace to five triple draw lowball
    - badugi
    - razz
    - seven card stud hi-low regular
    - et cetera
    """
    LOW_EIGHT_OR_BETTER: tuple[Rank, ...] = (
        Rank.ACE,
        Rank.DEUCE,
        Rank.TREY,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
    )
    """The low eight or better ranks (from ace to eight).

    This is used in:
    - "Big O" hi-low eight or better
    - Omaha hi-low eight or better
    - seven card stud hi-low eight or better
    - et cetera
    """


@unique
class Suit(str, Enum):
    """The enum class for suits.

    As in the case of every poker games, the suit's ordering is clubs,
    diamonds, hearts, and spades, which is also alphabetical.

    In most poker variants, suits are completely irrelevant and are
    never used to break ties or to decide the winner.

    >>> Suit.CLUB
    <Suit.CLUB: 'c'>
    >>> Suit('c')
    <Suit.CLUB: 'c'>
    >>> Suit.CLUB.name
    'CLUB'
    >>> Suit.CLUB.value
    'c'
    """

    CLUB: str = 'c'
    """The suit of clubs."""
    DIAMOND: str = 'd'
    """The suit of diamonds."""
    HEART: str = 'h'
    """The suit of hearts."""
    SPADE: str = 's'
    """The suit of spades."""


@dataclass(frozen=True)
class Card:
    """The class for cards.

    Cards are described by their ranks and their suits.

    Cards with higher ranks are considered stronger than those with
    lower ranks. Of course, the rank ordering is variant-dependant.
    Ties are broken by suits in some rare variants.

    >>> card = Card(Rank.ACE, Suit.SPADE)
    >>> card
    As
    >>> str(card)
    'ACE OF SPADES (As)'
    >>> card.rank
    <Rank.ACE: 'A'>
    >>> card.suit
    <Suit.SPADE: 's'>

    Note that the card attributes are read-only.

    >>> card.rank = Rank.KING
    Traceback (most recent call last):
        ...
    dataclasses.FrozenInstanceError: cannot assign to field 'rank'

    The card is also hashable.

    >>> from collections.abc import Hashable
    >>> isinstance(card, Hashable)
    True
    """

    rank: Rank
    """The rank."""
    suit: Suit
    """The suit."""

    @classmethod
    def get_ranks(cls, cards: Iterable[Card]) -> Iterator[Rank]:
        """Return an iterator of the ranks of each card.

        >>> Card.get_ranks(Card.parse('2sKh'))  # doctest: +ELLIPSIS
        <generator object Card.get_ranks at 0x...>
        >>> list(Card.get_ranks(Card.parse('2sKh')))
        [<Rank.DEUCE: '2'>, <Rank.KING: 'K'>]

        :param cards: The cards to get ranks from.
        :return: The iterator of the ranks of each card.
        """
        for card in cards:
            yield card.rank

    @classmethod
    def get_suits(cls, cards: Iterable[Card]) -> Iterator[Suit]:
        """Return an iterator of the suits of each card.

        >>> Card.get_suits(Card.parse('2sKh'))  # doctest: +ELLIPSIS
        <generator object Card.get_suits at 0x...>
        >>> list(Card.get_suits(Card.parse('2sKh')))
        [<Suit.SPADE: 's'>, <Suit.HEART: 'h'>]

        :param cards: The cards to get suits from.
        :return: The iterator of the suits of each card.
        """
        for card in cards:
            yield card.suit

    @classmethod
    def are_paired(cls, cards: Iterable[Card]) -> bool:
        """Return the pairedness of the given cards.

        The cards are paired if at least two of the cards share a
        common rank.

        >>> Card.are_paired(())
        False
        >>> Card.are_paired(Card.parse('2sKh'))
        False
        >>> Card.are_paired(Card.parse('2sKh2h'))
        True
        >>> Card.are_paired(Card.parse('2s2c2h'))
        True

        :param cards: The cards to determine the pairedness from.
        :return: The pairedness of the cards.
        """
        ranks = tuple(cls.get_ranks(cards))

        return len(set(ranks)) != len(ranks)

    @classmethod
    def are_suited(cls, cards: Iterable[Card]) -> bool:
        """Return the suitedness of the given cards.

        The cards are suited if all of the cards share a common suit.

        >>> Card.are_suited(())
        True
        >>> Card.are_suited(Card.parse('2s'))
        True
        >>> Card.are_suited(Card.parse('2sKh3s'))
        False
        >>> Card.are_suited(Card.parse('2hKh3h'))
        True

        :param cards: The cards to determine the suitedness from.
        :return: The suitedness of the cards.
        """
        return len(set(cls.get_suits(cards))) <= 1

    @classmethod
    def are_rainbow(cls, cards: Iterable[Card]) -> bool:
        """Return whether the cards are rainbow.

        The cards are rainbow if no two cards share a common suit.

        >>> Card.are_rainbow(())
        True
        >>> Card.are_rainbow(Card.parse('2s'))
        True
        >>> Card.are_rainbow(Card.parse('2sKh3c'))
        True
        >>> Card.are_rainbow(Card.parse('2hKh3c'))
        False

        :param cards: The cards to determine whether they are rainbow.
        :return: ``True`` if the cards are rainbow, otherwise ``False``.
        """
        suits = tuple(cls.get_suits(cards))

        return len(set(suits)) == len(suits)

    @classmethod
    def parse(cls, *raw_cards: str) -> Iterator[Card]:
        """Parse the string of the card representations.

        >>> Card.parse('AsKsQsJsTs')  # doctest: +ELLIPSIS
        <generator object Card.parse at 0x...>
        >>> list(Card.parse('2c8d5sKh'))
        [2c, 8d, 5s, Kh]
        >>> next(Card.parse('AcAh'))
        Ac
        >>> next(Card.parse('AcA'))
        Traceback (most recent call last):
            ...
        ValueError: content length not a multiple of 2
        >>> next(Card.parse('1d'))
        Traceback (most recent call last):
            ...
        ValueError: '1' is not a valid Rank
        >>> next(Card.parse('Ax'))
        Traceback (most recent call last):
            ...
        ValueError: 'x' is not a valid Suit

        :param raw_cards: The string of the card representations.
        :return: The generator yielding the parsed cards.
        :raises ValueError: If any card representation is invalid.
        """
        for contents in raw_cards:
            for content in contents.split():
                if len(content) % 2 != 0:
                    raise ValueError('content length not a multiple of 2')

                for i in range(0, len(content), 2):
                    rank = Rank(content[i])
                    suit = Suit(content[i + 1])

                    yield cls(rank, suit)

    def __repr__(self) -> str:
        return f'{self.rank}{self.suit}'

    def __str__(self) -> str:
        return f'{self.rank.name} OF {self.suit.name}S ({repr(self)})'


@unique
class Deck(tuple[Card, ...], Enum):
    """The enum class for a tuple of cards representing decks.

    Most poker games use the 52-card standard deck, denoted as
    :attr:`Deck.STANDARD`.

    >>> len(Deck.STANDARD)
    52
    >>> Deck.STANDARD[:6]
    (2c, 2d, 2h, 2s, 3c, 3d)

    However, short-deck hold'em uses a 36-card short deck where cards
    with ranks from 2 to 5 (inclusive) are missing. This particular deck
    is accessible via :attr:`Deck.SHORT_DECK_HOLDEM`.

    >>> len(Deck.SHORT_DECK_HOLDEM)
    36
    >>> Deck.SHORT_DECK_HOLDEM[:6]
    (6c, 6d, 6h, 6s, 7c, 7d)

    The members of :cls:`Deck` are tuples and cannot be modified. To use
    it effectively, you must make a copy with a different data type like
    ``list`` or ``deque``.

    >>> Deck.STANDARD[3] = Card(Rank.ACE, Suit.SPADE)
    Traceback (most recent call last):
        ...
    TypeError: 'Deck' object does not support item assignment
    >>> deck = list(Deck.STANDARD)
    >>> deck[3] = Card(Rank.ACE, Suit.SPADE)
    >>> deck[:6]
    [2c, 2d, 2h, As, 3c, 3d]
    """

    STANDARD: tuple[Card, ...] = tuple(
        starmap(
            Card,
            product(
                RankOrder.ROTATED,
                (Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE),
            ),
        ),
    )
    """The 52-card standard deck cards."""
    SHORT_DECK_HOLDEM: tuple[Card, ...] = tuple(
        starmap(
            Card,
            product(
                RankOrder.SHORT_DECK_HOLDEM,
                (Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE),
            ),
        ),
    )
    """The 36-card short-deck hold'em cards.

    In this deck, deuces to fives are stripped away.
    """


def filter_none(values: Iterable[Any]) -> Any:
    """Filter ``None`` from values.

    >>> filter_none([1, 2, None, 3])  # doctest: +ELLIPSIS
    <filter object at 0x...>
    >>> list(filter_none([1, 2, None, 3]))
    [1, 2, 3]

    :return: The filtered values.
    """
    return filter(partial(is_not, None), values)


def max_or_none(values: Iterable[Any], key: Any = None) -> Any:
    """Get the maximum value while ignoring ``None`` values.

    >>> max_or_none([1, 2, 3, -2, -1])
    3
    >>> max_or_none([1, None, 2, None, 3, -2, -1, None])
    3
    >>> max_or_none([]) is None
    True

    :return: The maximum value if any, otherwise ``None``.
    """
    try:
        return max(filter_none(values), key=key)
    except ValueError:
        return None


def min_or_none(values: Iterable[Any], key: Any = None) -> Any:
    """Get the minimum value while ignoring ``None`` values.

    >>> min_or_none([1, 2, 3, -2, -1])
    -2
    >>> min_or_none([1, None, 2, None, 3, -2, -1, None])
    -2
    >>> min_or_none([]) is None
    True

    :return: The minimum value if any, otherwise ``None``.
    """
    try:
        return min(filter_none(values), key=key)
    except ValueError:
        return None
