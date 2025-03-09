""":mod:`pokerkit.utilities` implements classes related to poker
utilities.

These utilities (helper constants, functions, classes, methods, etc.)
are used throughout the PokerKit project.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from collections import deque
from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from enum import Enum, StrEnum, unique
from functools import partial
from itertools import product, starmap
from math import inf
from numbers import Integral, Number
from operator import is_not
from random import shuffle
from re import compile, Pattern
from typing import Any, cast, ClassVar, TYPE_CHECKING, TypeVar
import builtins

if TYPE_CHECKING:
    from pokerkit.state import State

_T = TypeVar('_T')
UNMATCHABLE_PATTERN: Pattern[str] = compile(r'(?!)')
"""A regular expression pattern that can never be matched."""


@unique
class Rank(StrEnum):
    """The enum class for ranks.

    The ordering of the ranks is decided in accordance to the rules of
    the poker variant being played. A card of lower rank is said to be
    less than that of a higher rank.

    An enum element can be accessed through the following two ways:

    >>> Rank.DEUCE
    <Rank.DEUCE: '2'>
    >>> Rank('2')
    <Rank.DEUCE: '2'>

    A rank's single-character representation and full name can also be
    accessed.

    >>> Rank.DEUCE.name
    'DEUCE'
    >>> Rank.DEUCE.value
    '2'
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
    """The enum class for ordering of ranks.

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

    In some draw or low games, Ace is considered to be the lowest rank.
    This ordering is accessible via :attr:`RankOrder.REGULAR`.

    >>> len(RankOrder.REGULAR)
    13
    >>> RankOrder.REGULAR[0]
    <Rank.ACE: 'A'>
    >>> RankOrder.REGULAR[-1]
    <Rank.KING: 'K'>

    Eight-or-better low ranks are used for some split-pot games.

    >>> len(RankOrder.EIGHT_OR_BETTER_LOW)
    8
    >>> RankOrder.EIGHT_OR_BETTER_LOW[0]
    <Rank.ACE: 'A'>
    >>> RankOrder.EIGHT_OR_BETTER_LOW[-1]
    <Rank.EIGHT: '8'>
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
    ROYAL_POKER: tuple[Rank, ...] = (
        Rank.TEN,
        Rank.JACK,
        Rank.QUEEN,
        Rank.KING,
        Rank.ACE,
    )
    """The royal poker ranks (from ten to king)."""


@unique
class Suit(StrEnum):
    """The enum class for suits.

    As in the case of every poker games, the suit's ordering is clubs,
    diamonds, hearts, and spades, which is also alphabetical.

    In most poker variants, suits are completely irrelevant and are
    never used to break ties or to decide the winner (this is the case
    for PokerKit).

    In stud games, suits are used to break ties when deciding the
    opener when there are multiple up cards with the same rank.

    An enum element can be accessed through the following two ways:

    >>> Suit.CLUB
    <Suit.CLUB: 'c'>
    >>> Suit('c')
    <Suit.CLUB: 'c'>

    A suit's single-character representation and full name can also be
    accessed.

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
    Ties are broken by suits in some rare variants (for more details,
    please see :class:`pokerkit.utilities.Card`.

    >>> card = Card(Rank.ACE, Suit.SPADE)
    >>> card
    As
    >>> str(card)
    'ACE OF SPADES (As)'
    >>> card.rank
    <Rank.ACE: 'A'>
    >>> card.suit
    <Suit.SPADE: 's'>

    In PokerKit, the card attributes are read-only (i.e., immutable)...

    >>> card.rank = Rank.KING
    Traceback (most recent call last):
        ...
    dataclasses.FrozenInstanceError: cannot assign to field 'rank'

    ...and hence hashable.

    >>> from collections.abc import Hashable
    >>> isinstance(card, Hashable)
    True

    :param rank: The rank. For more details, please refer to
                 :attr:`pokerkit.utilities.Card.rank`.
    :param suit: The suit. For more details, please refer to
                 :attr:`pokerkit.utilities.Card.suit`.
    """

    UNKNOWN: ClassVar[Card]
    """An unknown card. This is a class variable."""
    rank: Rank
    """The rank of the card."""
    suit: Suit
    """The suit of the card."""

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

        This method "cleans" any cards-like object (e.g., raw string
        representations, a single card instance, etc.) into a tuple of
        card instances.

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

        This returns a generator of the parsed card instances.

        >>> Card.parse('AsKsQsJsTs')  # doctest: +ELLIPSIS
        <generator object Card.parse at 0x...>

        The generator can be consumed completely to obtain a ``list`` of
        cards.

        >>> list(Card.parse('2c8d5sKh'))
        [2c, 8d, 5s, Kh]
        >>> list(Card.parse('2c, 8d, 5s, Kh'))
        [2c, 8d, 5s, Kh]

        Calling ``next`` will consume a single element from the
        generator.

        >>> next(Card.parse('AcAh'))
        Ac

        Errors are raised when invalid card representations are
        encountered.

        >>> next(Card.parse('AcA'))  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: The sum of the lengths of valid card representations mus...
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
            contents = contents.replace('10', 'T').replace(',', '')

            for content in contents.split():
                if len(content) % 2 != 0:
                    raise ValueError(
                        (
                            'The sum of the lengths of valid card'
                            ' representations must be a multiple of 2, unlike'
                            f' {repr(content)}'
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

    def __bool__(self) -> bool:
        return not self.unknown_status

    @property
    def unknown_status(self) -> bool:
        """Return the unknown-ness of the card.

        A card is "unknown" if both or either one of its rank or suit is
        unknown.

        :return: The unknown-ness of the card.
        """
        return self.rank == Rank.UNKNOWN or self.suit == Suit.UNKNOWN


Card.UNKNOWN = Card(Rank.UNKNOWN, Suit.UNKNOWN)
CardsLike = Iterable[Card] | Card | str
"""A union of cards-like types. Each of these types can be "cleaned" by
the :meth:`pokerkit.utilities.Card.clean` class method.
"""


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

    The standard and regular decks have identical contents; however, the
    ordering of the cards are different.

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
    ROYAL_POKER: tuple[Card, ...] = tuple(
        starmap(
            Card,
            product(
                RankOrder.ROYAL_POKER,
                (Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE),
            ),
        ),
    )
    """The 20-card royal poker deck cards.

    The cards in it are ten, jack, queen, king, and ace of each suit.
    """


def filter_none(values: Iterable[Any]) -> Any:
    """Filter out ``None`` from an iterable of values.

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

    If the iterable of values are empty, ``None`` is returned.

    >>> min_or_none([1, 2, 3, -2, -1])
    -2
    >>> min_or_none([1, None, 2, None, 3, -2, -1, None])
    -2
    >>> min_or_none([]) is None
    True

    :param values: The optional values.
    :param key: The optional key function.
    :return: The minimum value. If the values are empty, ``None``.
    """
    try:
        return min(filter_none(values), key=key)
    except ValueError:
        return None


def max_or_none(values: Iterable[Any], key: Any = None) -> Any:
    """Get the maximum value while ignoring ``None`` values.

    If the iterable of values are empty, ``None`` is returned.

    >>> max_or_none([1, 2, 3, -2, -1])
    3
    >>> max_or_none([1, None, 2, None, 3, -2, -1, None])
    3
    >>> max_or_none([]) is None
    True

    :param values: The optional values.
    :param key: The optional key function.
    :return: The maximum value. If the values are empty, ``None``.
    """
    try:
        return max(filter_none(values), key=key)
    except ValueError:
        return None


ValuesLike = Iterable[int] | Mapping[int, int] | int
"""A union of values-like types. Each of these types can be "cleaned" by
the :func:`pokerkit.utilities.clean_values` function.
"""


def clean_values(values: ValuesLike, count: int) -> tuple[int, ...]:
    """Clean the numerical values.

    This function "cleans" any values-like object (e.g., iterables,
    mappings, an number, etc.) into a tuple of numerical values.

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
    :return: The cleaned numerical values.
    :raises ValueError: If the values are invalid.
    """
    if isinstance(values, Number):
        values = cast(tuple[int, ...], (values,) * count)
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

    The shuffling is performed out-of-place (i.e., not done in-place).

    >>> cards = shuffled(Card.parse('AcAdAhAs'))
    >>> cards  # doctest: +ELLIPSIS
    [A..., A..., A..., A...]

    :param values: The values to shuffle.
    :return: The shuffled values.
    """
    values = list(values)

    shuffle(values)

    return values


def rotated(values: Iterable[_T], count: int) -> deque[_T]:
    """Rotate the values.

    The rotation is performed out-of-place (i.e., not done in-place).

    >>> rotated(['a', 'b', 'c', 'd'], 2)
    deque(['c', 'd', 'a', 'b'])
    >>> rotated(range(5), -3)
    deque([3, 4, 0, 1, 2])

    :param values: The values to rotate.
    :param count: The rotation.
    :return: The rotated values.
    """
    values = deque(values)

    values.rotate(count)

    return values


def divmod(dividend: int, divisor: int) -> tuple[int, int]:
    """Divide the amount and get its quotient and remainder.

    >>> divmod(11, 3)
    (3, 2)
    >>> divmod(11.0, 3)  # doctest: +ELLIPSIS
    (3.666666666666666..., 0.0)

    :param dividend: The pot amount.
    :param divisor: The number of players.
    :return: The quotient and the remainder.
    """
    if isinstance(dividend, Integral):
        return builtins.divmod(dividend, divisor)

    quotient = dividend / divisor
    remainder = dividend - quotient * divisor

    return cast(tuple[int, int], (quotient, remainder))


def rake(
        amount: int,
        state: State | None = None,
        *,
        percentage: float = 0,
        cap: float = inf,
        no_flop_no_drop: bool = False,
) -> tuple[int, int]:
    """Rake the amount.

    This is a default raking function used by PokerKit (which defaults
    to not raking anything). Through methods like ``functools.partial``,
    parameters like the rake percentage, cap, and no-flop-no-drop can be
    overridden.

    Note that the percentage value is expected to be within range
    [``0``, ``1``]. For instance, ``0.1`` represents 10%.

    If ``no_flop_no_drop`` is enabled, this means that a rake will only
    be collected if a flop is dealt. Since PokerKit caters to many
    variants, we interpret this as being that there exists at least one
    card on the board. Some variants do not involve board cards, so if
    this parameter is set to ``True``, no rake will be raked whatsoever.

    >>> rake(100)
    (0, 100)
    >>> rake(1000, percentage=0.1)
    (100, 900)
    >>> rake(10, percentage=0.11)
    (1, 9)
    >>> rake(10.0, percentage=0.11)
    (1.1, 8.9)
    >>> rake(10.0, percentage=0.11, cap=1.0)
    (1.0, 9.0)
    >>> rake(100, percentage=0.1, no_flop_no_drop=True)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: If no-flop-no-drop is enabled, the state must be checked, bu...

    When this function is actually called, the ``state`` parameter will
    not be ``None`` as it is by default. This argument can be used to
    encode a more complicated raking logic.

    During state creation, user can supply their own rake function,
    corresponding with the accepted type signature.

    :param amount: The pot amount.
    :param state: The optional poker state whose pot is being raked.
    :param percentage: The rake percentage, defaults to ``0``. It should
                       be between ``0`` (0%) and ``1`` (100%).
    :param cap: The maximum raked amount, defaults to ``math.inf``
                (unlimited).
    :param no_flop_no_drop: ``True`` to only rake when there are cards
                            on the board, ``False`` otherwise. Defaults
                            to ``False``.
    :return: The raked amount and the unraked amount.
    """
    if not 0 <= percentage <= 1:
        raise ValueError(
            'The rake percentage ({percentage}) should be between 0 and 1.',
        )

    if no_flop_no_drop:
        if state is None:
            raise ValueError(
                (
                    'If no-flop-no-drop is enabled, the state must be checked,'
                    ' but it is unavailable.'
                ),
            )

        if not any(state.board_cards):
            return 0, amount

    raked_amount = amount * percentage

    if isinstance(amount, Integral):
        raked_amount = round(raked_amount)

    raked_amount = min(raked_amount, cap)
    unraked_amount = amount - raked_amount

    return cast(tuple[int, int], (raked_amount, unraked_amount))


def parse_value(raw_value: str) -> int:
    """Convert ``str`` to a numerical value.

    If integral, an ``int`` instance is returned. Otherwise, a
    ``decimal.Decimal`` instance is returned.

    >>> parse_value('3')
    3
    >>> parse_value('3.0')
    Decimal('3.0')
    >>> parse_value('3.5')
    Decimal('3.5')
    >>> parse_value('9,999.99')
    Decimal('9999.99')

    :param raw_value: The raw numerical value.
    :return: The converted numerical value.
    """
    raw_value = raw_value.replace(',', '')
    value: int | Decimal

    try:
        value = int(raw_value)
    except ValueError:
        value = Decimal(raw_value)

    return cast(int, value)


def parse_time(raw_time: str) -> time:
    """Convert ``str`` to a ``datetime.time``.

    >>> parse_time('12:34:56')
    datetime.time(12, 34, 56)

    :param raw_time: The raw time.
    :return: The converted time.
    """
    return datetime.strptime(raw_time, '%H:%M:%S').time()


def parse_month(raw_month: str) -> int:
    """Convert ``str`` to a month (``int``).

    >>> parse_month('July')
    7
    >>> parse_month('december')
    12

    :param raw_month: The raw month.
    :return: The converted month.
    """
    return datetime.strptime(raw_month, '%B').month


def sign(value: int) -> int:
    """Get sign of a numerical value.

    >>> sign(-5)
    -1
    >>> sign(10)
    1
    >>> sign(0)
    0

    :param value: The numerical value to get a sign from.
    :return: The sign of a numerical value.
    """
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0
