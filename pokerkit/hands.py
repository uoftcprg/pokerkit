""":mod:`pokerkit.hands` implements classes related to poker hands."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable
from functools import total_ordering
from itertools import chain, combinations
from typing import Any, ClassVar

from pokerkit.lookups import (
    BadugiLookup,
    EightOrBetterLookup,
    Entry,
    KuhnPokerLookup,
    Lookup,
    RegularLookup,
    ShortDeckHoldemLookup,
    StandardBadugiLookup,
    StandardLookup,
)
from pokerkit.utilities import Card, CardsLike


@total_ordering
class Hand(Hashable, ABC):
    """The abstract base class for poker hands.

    Stronger hands are considered greater than weaker hands.

    >>> h0 = ShortDeckHoldemHand('6s7s8s9sTs')
    >>> h1 = ShortDeckHoldemHand('7c8c9cTcJc')
    >>> h2 = ShortDeckHoldemHand('2c2d2h2s3h')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards '2c2d2h2s3h' form an invalid ShortDeckHoldemHand h...
    >>> h0
    6s7s8s9sTs
    >>> h1
    7c8c9cTcJc
    >>> print(h0)
    Straight flush (6s7s8s9sTs)
    >>> h0 < h1
    True

    It does not make sense to compare hands of different types.

    >>> h = BadugiHand('6d7s8h9c')
    >>> h < 500
    Traceback (most recent call last):
        ...
    TypeError: '<' not supported between instances of 'BadugiHand' and 'int'

    The hands are hashable.

    >>> h0 = ShortDeckHoldemHand('6s7s8s9sTs')
    >>> h1 = ShortDeckHoldemHand('7c8c9cTcJc')
    >>> hands = {h0, h1}

    :param cards: The cards that form the hand.
    :raises ValueError: If the cards form an invalid hand.
    """

    lookup: ClassVar[Lookup]
    """The hand lookup."""
    low: ClassVar[bool]
    """The low status."""

    @classmethod
    @abstractmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        pass  # pragma: no cover

    def __init__(self, cards: CardsLike) -> None:
        self.__cards = Card.clean(cards)

        if not self.lookup.has_entry(self.cards):
            raise ValueError(
                (
                    f'The cards {repr(cards)} form an invalid'
                    f' {type(self).__qualname__} hand.'
                ),
            )

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):  # noqa: E721
            return NotImplemented

        assert isinstance(other, Hand)

        return self.entry == other.entry

    def __hash__(self) -> int:
        return hash(self.entry)

    def __lt__(self, other: Hand) -> bool:
        if type(self) != type(other):  # noqa: E721
            return NotImplemented

        assert isinstance(other, Hand)

        if self.low:
            ordering = self.entry > other.entry
        else:
            ordering = self.entry < other.entry

        return ordering

    def __repr__(self) -> str:
        return ''.join(map(repr, self.cards))

    def __str__(self) -> str:
        return f'{self.entry.label.value} ({repr(self)})'

    @property
    def cards(self) -> tuple[Card, ...]:
        """Return the cards that form this hand.

        >>> hole = 'AsAc'
        >>> board = 'Kh3sAdAh'
        >>> hand = StandardHighHand.from_game(hole, board)
        >>> hand.cards
        (As, Ac, Kh, Ad, Ah)

        :return: The cards that form this hand.
        """
        return self.__cards

    @property
    def entry(self) -> Entry:
        """Return the hand entry.

        >>> hole = 'AsAc'
        >>> board = 'Kh3sAdAh'
        >>> hand = StandardHighHand.from_game(hole, board)
        >>> hand.entry.label
        <Label.FOUR_OF_A_KIND: 'Four of a kind'>

        :return: The hand entry.
        """
        return self.lookup.get_entry(self.cards)


class CombinationHand(Hand, ABC):
    """The abstract base class for combination hands."""

    card_count: ClassVar[int]
    """The number of cards."""

    @classmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = StandardHighHand.from_game('AcAdAhAsKc')
        >>> h1 = StandardHighHand('AcAdAhAsKc')
        >>> h0 == h1
        True
        >>> h0 = StandardHighHand.from_game('Ac9c', 'AhKhQhJhTh')
        >>> h1 = StandardHighHand('AhKhQhJhTh')
        >>> h0 == h1
        True

        >>> h0 = StandardLowHand.from_game('AcAdAhAsKc', '')
        >>> h1 = StandardLowHand('AcAdAhAsKc')
        >>> h0 == h1
        True
        >>> h0 = StandardLowHand.from_game('Ac9c', 'AhKhQhJhTh')
        >>> h1 = StandardLowHand('AcQhJhTh9c')
        >>> h0 == h1
        True

        >>> h0 = ShortDeckHoldemHand.from_game('AcKs', 'AhAsKcJsTs')
        >>> h1 = ShortDeckHoldemHand('AcAhAsKcKs')
        >>> h0 == h1
        True
        >>> h0 = ShortDeckHoldemHand.from_game('AcAd', '6s7cKcKd')
        >>> h1 = ShortDeckHoldemHand('AcAdKcKd7c')
        >>> h0 == h1
        True

        >>> h0 = EightOrBetterLowHand.from_game('As2s', '2c3c4c5c6c')
        >>> h1 = EightOrBetterLowHand('Ad2d3d4d5d')
        >>> h0 == h1
        True

        >>> h0 = RegularLowHand.from_game('AcAd', 'AhAsKcQdQh')
        >>> h1 = RegularLowHand('AcAsQdQhKc')
        >>> h0 == h1
        True
        >>> h0 = RegularLowHand.from_game('AcAd', 'AhAsKcQd')
        >>> h1 = RegularLowHand('AdAhAsKcQd')
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        max_hand = None

        for combination in combinations(
                chain(Card.clean(hole_cards), Card.clean(board_cards)),
                cls.card_count,
        ):
            try:
                hand = cls(combination)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError(
                (
                    f'No valid {type(cls).__qualname__} hand can be formed'
                    ' from the hole and board cards.'
                ),
            )

        return max_hand


class StandardHand(CombinationHand, ABC):
    """The abstract base class for standard hands."""

    lookup = StandardLookup()
    card_count = 5


class StandardHighHand(StandardHand):
    """The class for standard high hands.

    >>> h0 = StandardHighHand('7c5d4h3s2c')
    >>> h1 = StandardHighHand('7c6d4h3s2c')
    >>> h2 = StandardHighHand('8c7d6h4s2c')
    >>> h3 = StandardHighHand('AcAsAd2s4s')
    >>> h4 = StandardHighHand('TsJsQsKsAs')
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = StandardHighHand('4c5dThJsAcKh2h')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards '4c5dThJsAcKh2h' form an invalid StandardHighHand ...
    >>> h = StandardHighHand('Ac2c3c4c')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2c3c4c' form an invalid StandardHighHand hand.
    >>> h = StandardHighHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid StandardHighHand hand.
    """

    low = False


class StandardLowHand(StandardHand):
    """The class for standard low hands.

    >>> h0 = StandardLowHand('TsJsQsKsAs')
    >>> h1 = StandardLowHand('AcAsAd2s4s')
    >>> h2 = StandardLowHand('8c7d6h4s2c')
    >>> h3 = StandardLowHand('7c6d4h3s2c')
    >>> h4 = StandardLowHand('7c5d4h3s2c')
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = StandardLowHand('4c5dThJsAcKh2h')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards '4c5dThJsAcKh2h' form an invalid StandardLowHand h...
    >>> h = StandardLowHand('Ac2c3c4c')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2c3c4c' form an invalid StandardLowHand hand.
    >>> h = StandardLowHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid StandardLowHand hand.
    """

    low = True


class ShortDeckHoldemHand(CombinationHand):
    """The class for short-deck hold'em hands.

    Here, flushes beat full houses.

    >>> h0 = ShortDeckHoldemHand('6c7d8h9sJc')
    >>> h1 = ShortDeckHoldemHand('7c7d7hTsQc')
    >>> h2 = ShortDeckHoldemHand('As6c7h8h9h')
    >>> h3 = ShortDeckHoldemHand('AsAhKcKhKd')
    >>> h4 = ShortDeckHoldemHand('6s7s8sTsQs')
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = ShortDeckHoldemHand('4c5dThJsAcKh2h')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards '4c5dThJsAcKh2h' form an invalid ShortDeckHoldemHa...
    >>> h = ShortDeckHoldemHand('Ac2c3c4c5c')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2c3c4c5c' form an invalid ShortDeckHoldemHand ...
    >>> h = ShortDeckHoldemHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid ShortDeckHoldemHand hand.
    """

    lookup = ShortDeckHoldemLookup()
    low = False
    card_count = 5


class EightOrBetterLowHand(CombinationHand):
    """The class for eight or better low hands.

    >>> h0 = EightOrBetterLowHand('8c7d6h4s2c')
    >>> h1 = EightOrBetterLowHand('7c5d4h3s2c')
    >>> h2 = EightOrBetterLowHand('5d4h3s2dAd')
    >>> h0 < h1 < h2
    True

    >>> h = EightOrBetterLowHand('AcAsAd2s4s')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards 'AcAsAd2s4s' form an invalid EightOrBetterLowHand ...
    >>> h = EightOrBetterLowHand('TsJsQsKsAs')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards 'TsJsQsKsAs' form an invalid EightOrBetterLowHand ...
    >>> h = EightOrBetterLowHand('4c5dThJsAcKh2h')  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: The cards '4c5dThJsAcKh2h' form an invalid EightOrBetterLowH...
    >>> h = EightOrBetterLowHand('Ac2c3c4c')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2c3c4c' form an invalid EightOrBetterLowHand hand.
    >>> h = EightOrBetterLowHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid EightOrBetterLowHand hand.
    """

    lookup = EightOrBetterLookup()
    low = True
    card_count = 5


class RegularLowHand(CombinationHand):
    """The class for low regular hands.

    Here, flushes are ignored.

    >>> h0 = RegularLowHand('KhKsKcKdAc')
    >>> h1 = RegularLowHand('2s2c3s3cAh')
    >>> h2 = RegularLowHand('6c4d3h2sAc')
    >>> h3 = RegularLowHand('Ac2c3c4c5c')
    >>> h0 < h1 < h2 < h3
    True

    >>> h = RegularLowHand('4c5dThJsAcKh2h')
    Traceback (most recent call last):
        ...
    ValueError: The cards '4c5dThJsAcKh2h' form an invalid RegularLowHand hand.
    >>> h = RegularLowHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid RegularLowHand hand.
    """

    lookup = RegularLookup()
    low = True
    card_count = 5


class BoardCombinationHand(CombinationHand, ABC):
    """The abstract base class for board-combination hands."""

    board_card_count: ClassVar[int]
    """The number of board cards."""

    @classmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = GreekHoldemHand.from_game('Ac2d', 'QdJdTh2sKs')
        >>> h1 = GreekHoldemHand('2s2dAcKsQd')
        >>> h0 == h1
        True
        >>> h0 = GreekHoldemHand.from_game('AsKs', 'QdJdTh2s2d')
        >>> h1 = GreekHoldemHand('AsKsQdJdTh')
        >>> h0 == h1
        True
        >>> h0 = GreekHoldemHand.from_game('Ac9c', 'AhKhQhJhTh')
        >>> h1 = GreekHoldemHand('AcAhKhQh9c')
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        hole_cards = Card.clean(hole_cards)
        board_cards = Card.clean(board_cards)
        max_hand = None

        for combination in combinations(board_cards, cls.board_card_count):
            try:
                hand = super().from_game(hole_cards, combination)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError(
                (
                    f'No valid {type(cls).__qualname__} hand can be formed'
                    ' from the hole and board cards.'
                ),
            )

        return max_hand


class GreekHoldemHand(BoardCombinationHand):
    """The class for Greek hold'em hands.

    In Greek hold'em, the player must use all of their hole cards to
    make a hand.

    >>> h0 = GreekHoldemHand('7c5d4h3s2c')
    >>> h1 = GreekHoldemHand('7c6d4h3s2c')
    >>> h2 = GreekHoldemHand('8c7d6h4s2c')
    >>> h3 = GreekHoldemHand('AcAsAd2s4s')
    >>> h4 = GreekHoldemHand('TsJsQsKsAs')
    >>> h0 < h1 < h2 < h3 < h4
    True
    """

    lookup = StandardLookup()
    low = False
    card_count = 5
    board_card_count = 3


class HoleBoardCombinationHand(BoardCombinationHand, ABC):
    """The abstract base class for hole-board-combination hands."""

    hole_card_count: ClassVar[int]
    """The number of hole cards."""

    @classmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = OmahaHoldemHand.from_game('6c7c8c9c', '8s9sTc')
        >>> h1 = OmahaHoldemHand('6c7c8s9sTc')
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game('6c7c8s9s', '8c9cTc')
        >>> h1 = OmahaHoldemHand('6c7c8c9cTc')
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game('6c7c8c9c', '8s9sTc9hKs')
        >>> h1 = OmahaHoldemHand('8c8s9c9s9h')
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game('6c7c8sAh', 'As9cTc2sKs')
        >>> h1 = OmahaHoldemHand('AhAsKsTc8s')
        >>> h0 == h1
        True

        >>> h0 = OmahaEightOrBetterLowHand.from_game('As2s3s4s', '2c3c4c5c6c')
        >>> h1 = OmahaEightOrBetterLowHand('Ad2d3d4d5d')
        >>> h0 == h1
        True
        >>> h0 = OmahaEightOrBetterLowHand.from_game('As6s7s8s', '2c3c4c5c6c')
        >>> h1 = OmahaEightOrBetterLowHand('Ad2d3d4d6d')
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        hole_cards = Card.clean(hole_cards)
        board_cards = Card.clean(board_cards)
        max_hand = None

        for combination in combinations(hole_cards, cls.hole_card_count):
            try:
                hand = super().from_game(combination, board_cards)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError(
                (
                    f'No valid {type(cls).__qualname__} hand can be formed'
                    ' from the hole and board cards.'
                ),
            )

        return max_hand


class OmahaHoldemHand(HoleBoardCombinationHand):
    """The class for Omaha hold'em hands.

    In Omaha hold'em, the player must use a fixed number of their hole
    cards to make a hand.

    >>> h0 = OmahaHoldemHand('7c5d4h3s2c')
    >>> h1 = OmahaHoldemHand('7c6d4h3s2c')
    >>> h2 = OmahaHoldemHand('8c7d6h4s2c')
    >>> h3 = OmahaHoldemHand('AcAsAd2s4s')
    >>> h4 = OmahaHoldemHand('TsJsQsKsAs')
    >>> h0 < h1 < h2 < h3 < h4
    True
    """

    lookup = StandardLookup()
    low = False
    card_count = 5
    board_card_count = 3
    hole_card_count = 2


class OmahaEightOrBetterLowHand(HoleBoardCombinationHand):
    """The class for Omaha eight or better low hands.

    >>> h0 = OmahaEightOrBetterLowHand('8c7d6h4s2c')
    >>> h1 = OmahaEightOrBetterLowHand('7c5d4h3s2c')
    >>> h2 = OmahaEightOrBetterLowHand('5d4h3s2dAd')
    >>> h0 < h1 < h2
    True
    """

    lookup = EightOrBetterLookup()
    low = True
    card_count = 5
    board_card_count = 3
    hole_card_count = 2


class BadugiHand(Hand):
    """The class for badugi hands.

    >>> h0 = BadugiHand('Kc')
    >>> h1 = BadugiHand('Ac')
    >>> h2 = BadugiHand('4c8dKh')
    >>> h3 = BadugiHand('Ac2d3h5s')
    >>> h4 = BadugiHand('Ac2d3h4s')
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = BadugiHand('Ac2d3c4s5c')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2d3c4s5c' form an invalid BadugiHand hand.
    >>> h = BadugiHand('Ac2d3c4s')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2d3c4s' form an invalid BadugiHand hand.
    >>> h = BadugiHand('AcAd3h4s')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'AcAd3h4s' form an invalid BadugiHand hand.
    >>> h = BadugiHand('Ac2c')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'Ac2c' form an invalid BadugiHand hand.
    >>> h = BadugiHand(())
    Traceback (most recent call last):
        ...
    ValueError: The cards () form an invalid BadugiHand hand.
    """

    lookup = BadugiLookup()
    low = True

    @classmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = BadugiHand.from_game('2s4c5d6h')
        >>> h1 = BadugiHand('2s4c5d6h')
        >>> h0 == h1
        True
        >>> h0 = BadugiHand.from_game('2s3s4d7h')
        >>> h1 = BadugiHand('2s4d7h')
        >>> h0 == h1
        True
        >>> h0 = BadugiHand.from_game('KcKdKhKs')
        >>> h1 = BadugiHand('Ks')
        >>> h0 == h1
        True
        >>> h0 = BadugiHand.from_game('Ac2c3c4c')
        >>> h1 = BadugiHand('Ac')
        >>> h0 == h1
        True

        >>> h0 = BadugiHand.from_game('AcAdAhAs')
        >>> h1 = BadugiHand('As')
        >>> h0 == h1
        True
        >>> h0 = StandardBadugiHand.from_game('Ac2c3c4c')
        >>> h1 = StandardBadugiHand('2c')
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        ranks = set()
        suits = set()
        cards = set()

        for card in sorted(
                chain(Card.clean(hole_cards), Card.clean(board_cards)),
                key=lambda card: cls.lookup.rank_order.index(card.rank),
        ):
            if card.rank not in ranks and card.suit not in suits:
                ranks.add(card.rank)
                suits.add(card.suit)
                cards.add(card)

        return cls(cards)


class StandardBadugiHand(BadugiHand):
    """The class for standard badugi hands."""

    lookup = StandardBadugiLookup()


class KuhnPokerHand(Hand):
    """The class for Kuhn poker hands.

    >>> h0 = KuhnPokerHand('Js')
    >>> h1 = KuhnPokerHand('Qs')
    >>> h2 = KuhnPokerHand('Ks')
    >>> h0 < h1 < h2
    True

    >>> h = KuhnPokerHand('As')
    Traceback (most recent call last):
        ...
    ValueError: The cards 'As' form an invalid KuhnPokerHand hand.
    """

    lookup = KuhnPokerLookup()
    low = False

    @classmethod
    def from_game(
            cls,
            hole_cards: CardsLike,
            board_cards: CardsLike = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = KuhnPokerHand.from_game('Ks')
        >>> h1 = KuhnPokerHand('Ks')
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        return max(
            map(cls, chain(Card.clean(hole_cards), Card.clean(board_cards))),
        )
