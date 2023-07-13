""":mod:`pokerkit.hands` implements classes related to poker hands."""

from __future__ import annotations

from abc import ABC
from collections.abc import Hashable, Iterable, Iterator
from functools import total_ordering
from itertools import chain, combinations
from typing import Any
from warnings import warn

from pokerkit.lookups import (
    AceToFiveLowballLookup,
    BadugiLookup,
    Entry,
    Lookup,
    LowEightOrBetterLookup,
    ShortDeckHoldemLookup,
    StandardLookup,
)
from pokerkit.utilities import Card, RankOrder


@total_ordering
class Hand(Hashable, ABC):
    """The abstract base class for poker hands.

    Stronger hands are considered greater than weaker hands.

    >>> h0 = ShortDeckHoldemHand(Card.parse('6s7s8s9sTs'))
    >>> h1 = ShortDeckHoldemHand(Card.parse('7c8c9cTcJc'))
    >>> h2 = ShortDeckHoldemHand(Card.parse('2c2d2h2s3h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '2c2d2h2s3h'
    >>> h0
    6s7s8s9sTs
    >>> h1
    7c8c9cTcJc
    >>> h0 < h1
    True
    """

    _lookup: Lookup
    _low: bool

    @classmethod
    def from_game(
            cls,
            hole_cards: Iterable[Card],
            board_cards: Iterable[Card] = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = StandardHand.from_game(
        ...     Card.parse('AsQs'),
        ...     Card.parse('Ks8s9hTc2s'),
        ... )
        >>> h1 = StandardHand(Card.parse('AsQsKs8s2s'))
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        return cls(chain(hole_cards, board_cards))

    def __init__(self, cards: Iterable[Card]) -> None:
        self.__cards = tuple(cards)

        if not self._lookup.has_entry(self.cards):
            raise ValueError(f'invalid hand \'{repr(self)}\'')

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        elif type(self) != type(other):
            warn('comparing hands of different types')

        return self.entry == other.entry

    def __hash__(self) -> int:
        return hash(self.entry)

    def __lt__(self, other: Hand) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        elif type(self) != type(other):
            warn('comparing hands of different types')

        if self._low:
            return self.entry > other.entry
        else:
            return self.entry < other.entry

    def __repr__(self) -> str:
        return ''.join(map(repr, self.cards))

    def __str__(self) -> str:
        return f'{self.entry.label.value} ({repr(self)})'

    @property
    def cards(self) -> tuple[Card, ...]:
        """Return the cards that form this hand.

        >>> hole = Card.parse('AsAc')
        >>> board = Card.parse('Kh3sAdAh')
        >>> hand = StandardHand.from_game(hole, board)
        >>> hand.cards
        (As, Ac, Kh, Ad, Ah)

        :return: The cards that form this hand.
        """
        return self.__cards

    @property
    def entry(self) -> Entry:
        """Return the hand entry.

        >>> hole = Card.parse('AsAc')
        >>> board = Card.parse('Kh3sAdAh')
        >>> hand = StandardHand.from_game(hole, board)
        >>> hand.entry.label
        <Label.FOUR_OF_A_KIND: 'Four of a kind'>

        :return: The hand entry.
        """
        return self._lookup.get_entry(self.cards)


class StandardHand(Hand):
    """The class for standard hands.

    >>> h0 = StandardHand(Card.parse('7c5d4h3s2c'))
    >>> h1 = StandardHand(Card.parse('7c6d4h3s2c'))
    >>> h2 = StandardHand(Card.parse('8c7d6h4s2c'))
    >>> h3 = StandardHand(Card.parse('AcAsAd2s4s'))
    >>> h4 = StandardHand(Card.parse('TsJsQsKsAs'))
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = StandardHand(Card.parse('4c5dThJsAcKh2h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '4c5dThJsAcKh2h'
    >>> h = StandardHand(Card.parse('Ac2c3c4c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2c3c4c'
    >>> h = StandardHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _lookup: Lookup = StandardLookup()
    _low = False
    _card_count = 5

    @classmethod
    def from_game(
            cls,
            hole_cards: Iterable[Card],
            board_cards: Iterable[Card] = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = StandardHand.from_game(
        ...     Card.parse('AcAdAhAsKc'),
        ...     Card.parse(''),
        ... )
        >>> h1 = StandardHand(Card.parse('AcAdAhAsKc'))
        >>> h0 == h1
        True
        >>> h0 = StandardHand.from_game(
        ...     Card.parse('Ac9c'),
        ...     Card.parse('AhKhQhJhTh'),
        ... )
        >>> h1 = StandardHand(Card.parse('AhKhQhJhTh'))
        >>> h0 == h1
        True

        >>> h0 = DeuceToSevenLowballHand.from_game(
        ...     Card.parse('AcAdAhAsKc'),
        ...     Card.parse(''),
        ... )
        >>> h1 = DeuceToSevenLowballHand(Card.parse('AcAdAhAsKc'))
        >>> h0 == h1
        True
        >>> h0 = DeuceToSevenLowballHand.from_game(
        ...     Card.parse('Ac9c'),
        ...     Card.parse('AhKhQhJhTh'),
        ... )
        >>> h1 = DeuceToSevenLowballHand(Card.parse('AcQhJhTh9c'))
        >>> h0 == h1
        True

        >>> h0 = ShortDeckHoldemHand.from_game(
        ...     Card.parse('AcKs'),
        ...     Card.parse('AhAsKcJsTs'),
        ... )
        >>> h1 = ShortDeckHoldemHand(Card.parse('AcAhAsKcKs'))
        >>> h0 == h1
        True
        >>> h0 = ShortDeckHoldemHand.from_game(
        ...     Card.parse('AcAd'),
        ...     Card.parse('6s7cKcKd'),
        ... )
        >>> h1 = ShortDeckHoldemHand(Card.parse('AcAdKcKd7c'))
        >>> h0 == h1
        True

        >>> h0 = LowEightOrBetterHand.from_game(
        ...     Card.parse('As2s'),
        ...     Card.parse('2c3c4c5c6c'),
        ... )
        >>> h1 = LowEightOrBetterHand(Card.parse('Ad2d3d4d5d'))
        >>> h0 == h1
        True

        >>> h0 = AceToFiveLowballHand.from_game(
        ...     Card.parse('AcAd'),
        ...     Card.parse('AhAsKcQdQh'),
        ... )
        >>> h1 = AceToFiveLowballHand(Card.parse('AcAsQdQhKc'))
        >>> h0 == h1
        True
        >>> h0 = AceToFiveLowballHand.from_game(
        ...     Card.parse('AcAd'),
        ...     Card.parse('AhAsKcQd'),
        ... )
        >>> h1 = AceToFiveLowballHand(Card.parse('AdAhAsKcQd'))
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        max_hand = None

        for combination in combinations(
                chain(hole_cards, board_cards),
                cls._card_count,
        ):
            try:
                hand = cls(combination)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError('no valid hand')

        return max_hand


class DeuceToSevenLowballHand(StandardHand):
    """The class for deuce-to-seven lowball hands.

    >>> h0 = DeuceToSevenLowballHand(Card.parse('TsJsQsKsAs'))
    >>> h1 = DeuceToSevenLowballHand(Card.parse('AcAsAd2s4s'))
    >>> h2 = DeuceToSevenLowballHand(Card.parse('8c7d6h4s2c'))
    >>> h3 = DeuceToSevenLowballHand(Card.parse('7c6d4h3s2c'))
    >>> h4 = DeuceToSevenLowballHand(Card.parse('7c5d4h3s2c'))
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = DeuceToSevenLowballHand(Card.parse('4c5dThJsAcKh2h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '4c5dThJsAcKh2h'
    >>> h = DeuceToSevenLowballHand(Card.parse('Ac2c3c4c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2c3c4c'
    >>> h = DeuceToSevenLowballHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _low = True


class ShortDeckHoldemHand(StandardHand):
    """The class for short-deck hold'em hands.

    Here, flushes beat full houses.

    >>> h0 = ShortDeckHoldemHand(Card.parse('6c7d8h9sJc'))
    >>> h1 = ShortDeckHoldemHand(Card.parse('7c7d7hTsQc'))
    >>> h2 = ShortDeckHoldemHand(Card.parse('As6c7h8h9h'))
    >>> h3 = ShortDeckHoldemHand(Card.parse('AsAhKcKhKd'))
    >>> h4 = ShortDeckHoldemHand(Card.parse('6s7s8sTsQs'))
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = ShortDeckHoldemHand(Card.parse('4c5dThJsAcKh2h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '4c5dThJsAcKh2h'
    >>> h = ShortDeckHoldemHand(Card.parse('Ac2c3c4c5c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2c3c4c5c'
    >>> h = ShortDeckHoldemHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _lookup = ShortDeckHoldemLookup()


class LowEightOrBetterHand(StandardHand):
    """The class for low eight or better hands.

    >>> h0 = LowEightOrBetterHand(Card.parse('8c7d6h4s2c'))
    >>> h1 = LowEightOrBetterHand(Card.parse('7c5d4h3s2c'))
    >>> h2 = LowEightOrBetterHand(Card.parse('5d4h3s2dAd'))
    >>> h0 < h1 < h2
    True

    >>> h = LowEightOrBetterHand(Card.parse('AcAsAd2s4s'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'AcAsAd2s4s'
    >>> h = LowEightOrBetterHand(Card.parse('TsJsQsKsAs'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'TsJsQsKsAs'
    >>> h = LowEightOrBetterHand(Card.parse('4c5dThJsAcKh2h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '4c5dThJsAcKh2h'
    >>> h = LowEightOrBetterHand(Card.parse('Ac2c3c4c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2c3c4c'
    >>> h = LowEightOrBetterHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _lookup = LowEightOrBetterLookup()
    _low = True


class AceToFiveLowballHand(StandardHand):
    """The class for ace-to-five lowball hands.

    Here, flushes are ignored.

    >>> h0 = AceToFiveLowballHand(Card.parse('KhKsKcKdAc'))
    >>> h1 = AceToFiveLowballHand(Card.parse('2s2c3s3cAh'))
    >>> h2 = AceToFiveLowballHand(Card.parse('6c4d3h2sAc'))
    >>> h3 = AceToFiveLowballHand(Card.parse('Ac2c3c4c5c'))
    >>> h0 < h1 < h2 < h3
    True

    >>> h = AceToFiveLowballHand(Card.parse('4c5dThJsAcKh2h'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand '4c5dThJsAcKh2h'
    >>> h = AceToFiveLowballHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _lookup = AceToFiveLowballLookup()
    _low = True


class GreekHoldemHand(Hand):
    """The class for Greek hold'em hands.

    In Greek hold'em, the player must use all of his/her hole cards to
    make a hand.

    >>> h0 = GreekHoldemHand(Card.parse('7c5d4h3s2c'))
    >>> h1 = GreekHoldemHand(Card.parse('7c6d4h3s2c'))
    >>> h2 = GreekHoldemHand(Card.parse('8c7d6h4s2c'))
    >>> h3 = GreekHoldemHand(Card.parse('AcAsAd2s4s'))
    >>> h4 = GreekHoldemHand(Card.parse('TsJsQsKsAs'))
    >>> h0 < h1 < h2 < h3 < h4
    True
    """

    _lookup: Lookup = StandardLookup()
    _low = False
    _board_card_count = 3

    @classmethod
    def from_game(
            cls,
            hole_cards: Iterable[Card],
            board_cards: Iterable[Card] = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = GreekHoldemHand.from_game(
        ...     Card.parse('Ac2d'),
        ...     Card.parse('QdJdTh2sKs'),
        ... )
        >>> h1 = GreekHoldemHand(Card.parse('2s2dAcKsQd'))
        >>> h0 == h1
        True
        >>> h0 = GreekHoldemHand.from_game(
        ...     Card.parse('AsKs'),
        ...     Card.parse('QdJdTh2s2d'),
        ... )
        >>> h1 = GreekHoldemHand(Card.parse('AsKsQdJdTh'))
        >>> h0 == h1
        True
        >>> h0 = GreekHoldemHand.from_game(
        ...     Card.parse('Ac9c'),
        ...     Card.parse('AhKhQhJhTh'),
        ... )
        >>> h1 = GreekHoldemHand(Card.parse('AcAhKhQh9c'))
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        if isinstance(hole_cards, Iterator):
            hole_cards = tuple(hole_cards)

        max_hand = None

        for combination in combinations(board_cards, cls._board_card_count):
            try:
                hand = super().from_game(hole_cards, combination)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError('no valid hand')

        return max_hand


class OmahaHoldemHand(GreekHoldemHand):
    """The class for Omaha hold'em hands.

    In Omaha hold'em, the player must use a fixed number of his/her hole
    cards to make a hand.

    >>> h0 = OmahaHoldemHand(Card.parse('7c5d4h3s2c'))
    >>> h1 = OmahaHoldemHand(Card.parse('7c6d4h3s2c'))
    >>> h2 = OmahaHoldemHand(Card.parse('8c7d6h4s2c'))
    >>> h3 = OmahaHoldemHand(Card.parse('AcAsAd2s4s'))
    >>> h4 = OmahaHoldemHand(Card.parse('TsJsQsKsAs'))
    >>> h0 < h1 < h2 < h3 < h4
    True
    """

    _hole_card_count = 2

    @classmethod
    def from_game(
            cls,
            hole_cards: Iterable[Card],
            board_cards: Iterable[Card] = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = OmahaHoldemHand.from_game(
        ...     Card.parse('6c7c8c9c'),
        ...     Card.parse('8s9sTc'),
        ... )
        >>> h1 = OmahaHoldemHand(Card.parse('6c7c8s9sTc'))
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game(
        ...     Card.parse('6c7c8s9s'),
        ...     Card.parse('8c9cTc'),
        ... )
        >>> h1 = OmahaHoldemHand(Card.parse('6c7c8c9cTc'))
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game(
        ...     Card.parse('6c7c8c9c'),
        ...     Card.parse('8s9sTc9hKs'),
        ... )
        >>> h1 = OmahaHoldemHand(Card.parse('8c8s9c9s9h'))
        >>> h0 == h1
        True
        >>> h0 = OmahaHoldemHand.from_game(
        ...     Card.parse('6c7c8sAh'),
        ...     Card.parse('As9cTc2sKs'),
        ... )
        >>> h1 = OmahaHoldemHand(Card.parse('AhAsKsTc8s'))
        >>> h0 == h1
        True

        >>> h0 = OmahaLowEightOrBetterHand.from_game(
        ...     Card.parse('As2s3s4s'),
        ...     Card.parse('2c3c4c5c6c'),
        ... )
        >>> h1 = OmahaLowEightOrBetterHand(Card.parse('Ad2d3d4d5d'))
        >>> h0 == h1
        True
        >>> h0 = OmahaLowEightOrBetterHand.from_game(
        ...     Card.parse('As6s7s8s'),
        ...     Card.parse('2c3c4c5c6c'),
        ... )
        >>> h1 = OmahaLowEightOrBetterHand(Card.parse('Ad2d3d4d6d'))
        >>> h0 == h1
        True

        :param hole_cards: The hole cards.
        :param board_cards: The optional board cards.
        :return: The strongest hand from possible card combinations.
        """
        if isinstance(board_cards, Iterator):
            board_cards = tuple(board_cards)

        max_hand = None

        for combination in combinations(hole_cards, cls._hole_card_count):
            try:
                hand = super().from_game(combination, board_cards)
            except ValueError:
                pass
            else:
                if max_hand is None or hand > max_hand:
                    max_hand = hand

        if max_hand is None:
            raise ValueError('no valid hand')

        return max_hand


class OmahaLowEightOrBetterHand(OmahaHoldemHand):
    """The class for Omaha low eight or better hands.

    >>> h0 = OmahaLowEightOrBetterHand(Card.parse('8c7d6h4s2c'))
    >>> h1 = OmahaLowEightOrBetterHand(Card.parse('7c5d4h3s2c'))
    >>> h2 = OmahaLowEightOrBetterHand(Card.parse('5d4h3s2dAd'))
    >>> h0 < h1 < h2
    True
    """

    _lookup = LowEightOrBetterLookup()
    _low = True


class BadugiHand(Hand):
    """The class for badugi hands.

    >>> h0 = BadugiHand(Card.parse('Kc'))
    >>> h1 = BadugiHand(Card.parse('Ac'))
    >>> h2 = BadugiHand(Card.parse('4c8dKh'))
    >>> h3 = BadugiHand(Card.parse('Ac2d3h5s'))
    >>> h4 = BadugiHand(Card.parse('Ac2d3h4s'))
    >>> h0 < h1 < h2 < h3 < h4
    True

    >>> h = BadugiHand(Card.parse('Ac2d3c4s5c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2d3c4s5c'
    >>> h = BadugiHand(Card.parse('AcAd3h4s'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'AcAd3h4s'
    >>> h = BadugiHand(Card.parse('Ac2c'))
    Traceback (most recent call last):
        ...
    ValueError: invalid hand 'Ac2c'
    >>> h = BadugiHand(())
    Traceback (most recent call last):
        ...
    ValueError: invalid hand ''
    """

    _lookup = BadugiLookup()
    _low = True

    @classmethod
    def from_game(
            cls,
            hole_cards: Iterable[Card],
            board_cards: Iterable[Card] = (),
    ) -> Hand:
        """Create a poker hand from a game setting.

        In a game setting, a player uses private cards from their hole
        and the public cards from the board to make their hand.

        >>> h0 = BadugiHand.from_game(Card.parse('2s4c5d6h'))
        >>> h1 = BadugiHand(Card.parse('2s4c5d6h'))
        >>> h0 == h1
        True
        >>> h0 = BadugiHand.from_game(Card.parse('2s3s4d7h'))
        >>> h1 = BadugiHand(Card.parse('2s4d7h'))
        >>> h0 == h1
        True
        >>> h0 = BadugiHand.from_game(Card.parse('KcKdKhKs'))
        >>> h1 = BadugiHand(Card.parse('Ks'))
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
                chain(hole_cards, board_cards),
                key=lambda card: RankOrder.STANDARD.index(card.rank),
        ):
            if card.rank not in ranks and card.suit not in suits:
                ranks.add(card.rank)
                suits.add(card.suit)
                cards.add(card)

        return cls(cards)

    def __init__(self, cards: Iterable[Card]) -> None:
        super().__init__(cards)

        if not Card.are_rainbow(self.cards):
            raise ValueError('cards are not rainbow')
