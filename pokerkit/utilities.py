""":mod:`pokerkit.utilities` implements classes related to poker
utilities.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from enum import Enum, StrEnum, unique
from functools import partial
from itertools import product, starmap
from numbers import Integral
from operator import is_not
from random import shuffle
from typing import Any, cast, TypeVar

_T = TypeVar('_T')


@unique
class Rank(StrEnum):
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
    UNKNOWN: str = '?'
    """The unknown rank."""


@unique
class RankOrder(tuple[Rank, ...], Enum):
    """The enum class for tuples of ranks.

    Poker variants order the ranks differently between each other. Most
    games use deuce to ace ordering which is defined here as
    :attr:`RankOrder.STANDARD`.

    >>> len(RankOrder.STANDARD)
    13
    >>> RankOrder.STANDARD[0]
    <Rank.DEUCE: '2'>
    >>> RankOrder.STANDARD[-1]
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
    ordering is accessible via :attr:`RankOrder.REGULAR`.

    >>> len(RankOrder.REGULAR)
    13
    >>> RankOrder.REGULAR[0]
    <Rank.ACE: 'A'>
    >>> RankOrder.REGULAR[-1]
    <Rank.KING: 'K'>
    """

    STANDARD: tuple[Rank, ...] = (
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
    """The standard ranks (from deuce to ace)."""
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
    REGULAR: tuple[Rank, ...] = (
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
    """The regular ranks (from ace to king)."""
    EIGHT_OR_BETTER_LOW: tuple[Rank, ...] = (
        Rank.ACE,
        Rank.DEUCE,
        Rank.TREY,
        Rank.FOUR,
        Rank.FIVE,
        Rank.SIX,
        Rank.SEVEN,
        Rank.EIGHT,
    )
    """The eight or better low ranks (from ace to eight)."""
    KUHN_POKER: tuple[Rank, ...] = Rank.JACK, Rank.QUEEN, Rank.KING
    """The Kuhn poker ranks (from jack to king)."""


@unique
class Suit(StrEnum):
    """The enum class for suits.

    As in the case of every poker games, the suit's ordering is clubs,
    diamonds, hearts, and spades, which is also alphabetical.

    In most poker variants, suits are completely irrelevant and are
    never used to break ties or to decide the winner.

    In stud games, suits are used to break ties when deciding the
    opener when there are multiple up cards with the same rank.

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
    UNKNOWN: str = '?'
    """The unknown suit."""


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
    def get_ranks(cls, cards: CardsLike) -> Iterator[Rank]:
        """Return an iterator of the ranks of each card.

        >>> Card.get_ranks('2sKh')  # doctest: +ELLIPSIS
        <generator object Card.get_ranks at 0x...>
        >>> list(Card.get_ranks('2sKh'))
        [<Rank.DEUCE: '2'>, <Rank.KING: 'K'>]

        :param cards: The cards to get ranks from.
        :return: The iterator of the ranks of each card.
        """
        for card in cls.clean(cards):
            yield card.rank

    @classmethod
    def get_suits(cls, cards: CardsLike) -> Iterator[Suit]:
        """Return an iterator of the suits of each card.

        >>> Card.get_suits('2sKh')  # doctest: +ELLIPSIS
        <generator object Card.get_suits at 0x...>
        >>> list(Card.get_suits('2sKh'))
        [<Suit.SPADE: 's'>, <Suit.HEART: 'h'>]

        :param cards: The cards to get suits from.
        :return: The iterator of the suits of each card.
        """
        for card in cls.clean(cards):
            yield card.suit

    @classmethod
    def are_paired(cls, cards: CardsLike) -> bool:
        """Return the pairedness of the given cards.

        The cards are paired if at least two of the cards share a
        common rank.

        >>> Card.are_paired(())
        False
        >>> Card.are_paired('2sKh')
        False
        >>> Card.are_paired('2sKh2h')
        True
        >>> Card.are_paired('2s2c2h')
        True

        :param cards: The cards to determine the pairedness from.
        :return: The pairedness of the cards.
        """
        ranks = tuple(cls.get_ranks(cards))

        return len(set(ranks)) != len(ranks)

    @classmethod
    def are_suited(cls, cards: CardsLike) -> bool:
        """Return the suitedness of the given cards.

        The cards are suited if all of the cards share a common suit.

        >>> Card.are_suited(())
        True
        >>> Card.are_suited('2s')
        True
        >>> Card.are_suited('2sKh3s')
        False
        >>> Card.are_suited('2hKh3h')
        True

        :param cards: The cards to determine the suitedness from.
        :return: The suitedness of the cards.
        """
        return len(set(cls.get_suits(cards))) <= 1

    @classmethod
    def are_rainbow(cls, cards: CardsLike) -> bool:
        """Return whether the cards are rainbow.

        The cards are rainbow if no two cards share a common suit.

        >>> Card.are_rainbow(())
        True
        >>> Card.are_rainbow('2s')
        True
        >>> Card.are_rainbow('2sKh3c')
        True
        >>> Card.are_rainbow('2hKh3c')
        False

        :param cards: The cards to determine whether they are rainbow.
        :return: ``True`` if the cards are rainbow, otherwise ``False``.
        """
        suits = tuple(cls.get_suits(cards))

        return len(set(suits)) == len(suits)

    @classmethod
    def clean(cls, values: CardsLike) -> tuple[Card, ...]:
        """Clean the cards.

        >>> Card.clean('AsKs')
        (As, Ks)
        >>> Card.clean('AsKs')
        (As, Ks)
        >>> Card.clean(Card(Rank.ACE, Suit.SPADE))
        (As,)
        >>> Card.clean(None)
        Traceback (most recent call last):
            ...
        ValueError: The card values None are invalid.

        :param values: The cards.
        :return: The cleaned cards.
        """
        if isinstance(values, Card):
            values = (values,)
        elif isinstance(values, str):
            values = tuple(Card.parse(values))
        elif isinstance(values, Iterable):
            assert not isinstance(values, str)

            values = tuple(values)
        else:
            raise ValueError(f'The card values {repr(values)} are invalid.')

        return values

    @classmethod
    def parse(cls, *raw_cards: str) -> Iterator[Card]:
        """Parse the string of the card representations.

        >>> Card.parse('AsKsQsJsTs')  # doctest: +ELLIPSIS
        <generator object Card.parse at 0x...>
        >>> list(Card.parse('2c8d5sKh'))
        [2c, 8d, 5s, Kh]
        >>> next(Card.parse('AcAh'))
        Ac
        >>> next(Card.parse('AcA'))  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: The lengths of valid card representations must be multip...
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
                    raise ValueError(
                        (
                            'The lengths of valid card representations must be'
                            f' multiples of 2, unlike {repr(content)}'
                        ),
                    )

                for i in range(0, len(content), 2):
                    rank = Rank(content[i])
                    suit = Suit(content[i + 1])

                    yield cls(rank, suit)

    def __repr__(self) -> str:
        return f'{self.rank}{self.suit}'

    def __str__(self) -> str:
        return f'{self.rank.name} OF {self.suit.name}S ({repr(self)})'

    @property
    def unknown_status(self) -> bool:
        return self.rank == Rank.UNKNOWN or self.suit == Suit.UNKNOWN


CardsLike = Iterable[Card] | Card | str


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

    The members of :class:`Deck` are tuples and cannot be modified. To
    use it effectively, you must make a copy with a different data type
    like ``list`` or ``deque``.

    >>> Deck.STANDARD[3] = Card(Rank.ACE, Suit.SPADE)
    Traceback (most recent call last):
        ...
    TypeError: 'Deck' object does not support item assignment
    >>> deck = list(Deck.STANDARD)
    >>> deck[3] = Card(Rank.ACE, Suit.SPADE)
    >>> deck[:6]
    [2c, 2d, 2h, As, 3c, 3d]

    The standard and regular decks have identical contents. The ordering
    of the cards are different, however.

    >>> len(Deck.STANDARD)
    52
    >>> len(Deck.REGULAR)
    52
    >>> Deck.STANDARD[:6]
    (2c, 2d, 2h, 2s, 3c, 3d)
    >>> Deck.REGULAR[:6]
    (Ac, Ad, Ah, As, 2c, 2d)
    """

    STANDARD: tuple[Card, ...] = tuple(
        starmap(
            Card,
            product(
                RankOrder.STANDARD,
                (Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE),
            ),
        ),
    )
    """The 52-card standard deck cards.

    The ranks are ordered from deuces to aces.
    """
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
    REGULAR: tuple[Card, ...] = tuple(
        starmap(
            Card,
            product(
                RankOrder.REGULAR,
                (Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE),
            ),
        ),
    )
    """The 52-card regular deck cards.

    The ranks are ordered from aces to kings.
    """
    KUHN_POKER: tuple[Card, ...] = tuple(
        starmap(Card, product(RankOrder.KUHN_POKER, (Suit.SPADE,))),
    )
    """The 3-card Kuhn poker deck cards.

    The cards in it are jack of spades, queen of spades, and king of
    spades.
    """


def filter_none(values: Iterable[Any]) -> Any:
    """Filter ``None`` from values.

    >>> filter_none([1, 2, None, 3])  # doctest: +ELLIPSIS
    <filter object at 0x...>
    >>> list(filter_none([1, 2, None, 3]))
    [1, 2, 3]

    :param values: The optional values.
    :return: The filtered values.
    """
    return filter(partial(is_not, None), values)


def min_or_none(values: Iterable[Any], key: Any = None) -> Any:
    """Get the minimum value while ignoring ``None`` values.

    >>> min_or_none([1, 2, 3, -2, -1])
    -2
    >>> min_or_none([1, None, 2, None, 3, -2, -1, None])
    -2
    >>> min_or_none([]) is None
    True

    :param values: The optional values.
    :param key: The optional key function.
    :return: The minimum value if any, otherwise ``None``.
    """
    try:
        return min(filter_none(values), key=key)
    except ValueError:
        return None


def max_or_none(values: Iterable[Any], key: Any = None) -> Any:
    """Get the maximum value while ignoring ``None`` values.

    >>> max_or_none([1, 2, 3, -2, -1])
    3
    >>> max_or_none([1, None, 2, None, 3, -2, -1, None])
    3
    >>> max_or_none([]) is None
    True

    :param values: The optional values.
    :param key: The optional key function.
    :return: The maximum value if any, otherwise ``None``.
    """
    try:
        return max(filter_none(values), key=key)
    except ValueError:
        return None


ValuesLike = Iterable[int] | Mapping[int, int] | int


def clean_values(values: ValuesLike, count: int) -> tuple[int, ...]:
    """Clean the integers.

    >>> clean_values([1, 2, 3, 4], 4)
    (1, 2, 3, 4)
    >>> clean_values([1, 2, 3, 4], 6)
    (1, 2, 3, 4, 0, 0)
    >>> clean_values({0: 1, -1: 2}, 4)
    (1, 0, 0, 2)
    >>> clean_values(4, 4)
    (4, 4, 4, 4)
    >>> clean_values((1, 2, 3), 2)
    (1, 2)
    >>> clean_values(None, 2)
    Traceback (most recent call last):
        ...
    ValueError: The values None are invalid.

    :param values: The values.
    :param count: The number of values.
    :return: The cleaned integers.
    """
    if isinstance(values, int | float):
        values = (values,) * count
    elif isinstance(values, Mapping):
        parsed_values = [0] * count

        for key, value in values.items():
            parsed_values[key] += value

        values = tuple(parsed_values)
    elif isinstance(values, Iterable):
        parsed_values = list(values)[:count]

        while len(parsed_values) < count:
            parsed_values.append(0)

        values = tuple(parsed_values)
    else:
        raise ValueError(f'The values {repr(values)} are invalid.')

    return values


def shuffled(values: Iterable[_T]) -> list[_T]:
    """Return the shuffled values.

    The shuffling is not done in-place.

    >>> cards = shuffled(Card.parse('AcAdAhAs'))
    >>> cards  # doctest: +ELLIPSIS
    [A..., A..., A..., A...]

    :param values: The values to shuffle.
    :return: The shuffled values.
    """
    values = list(values)

    shuffle(values)

    return values


_divmod = divmod


def divmod(dividend: int, divisor: int) -> tuple[int, int]:
    """Divide the amount.

    >>> divmod(11, 3)
    (3, 2)
    >>> divmod(11.0, 3)  # doctest: +ELLIPSIS
    (3.666666666666666..., 0.0)

    :param dividend: The pot amount.
    :param divisor: The number of players.
    :return: The quotient and the remainder.
    """
    if isinstance(dividend, Integral):
        return _divmod(dividend, divisor)

    quotient = dividend / divisor
    remainder = dividend - quotient * divisor

    return cast(tuple[int, int], (quotient, remainder))


def rake(amount: int, rake: float) -> tuple[int, int]:
    """Rake the amount.

    >>> rake(100, 0)
    (0, 100)
    >>> rake(1000, 0.1)
    (100, 900)
    >>> rake(10, 0.11)
    (1, 9)
    >>> rake(10.0, 0.11)
    (1.1, 8.9)

    :param amount: The pot amount.
    :param rake: The rake.
    :return: The raked amount and the remaining amount.
    """
    raked_amount = amount * rake

    if isinstance(amount, Integral):
        raked_amount = round(raked_amount)

    remaining_amount = amount - raked_amount

    return cast(tuple[int, int], (raked_amount, remaining_amount))


def parse_value(raw_value: str) -> int:
    """Convert ``str`` to a number.

    >>> parse_value('3')
    3
    >>> parse_value('3.0')
    3.0
    >>> parse_value('3.5')
    3.5

    :param raw_value: The raw value.
    :return: The converted value.
    """
    value: int | float

    try:
        value = int(raw_value)
    except ValueError:
        value = float(raw_value)

    return cast(int, value)
