""":mod:`pokerkit.lookups` implements classes related to poker hand
lookups.
"""

from abc import ABC
from collections import Counter
from collections.abc import Iterable, Reversible, Sequence
from dataclasses import dataclass, field
from enum import StrEnum, unique
from functools import partial
from itertools import combinations, filterfalse
from math import prod
from operator import contains

from pokerkit.utilities import Card, Rank, RankOrder


@unique
class Label(StrEnum):
    """The enum class for all hand classification labels.

    >>> Label.ONE_PAIR
    <Label.ONE_PAIR: 'One pair'>
    >>> Label.FULL_HOUSE
    <Label.FULL_HOUSE: 'Full house'>
    """

    HIGH_CARD: str = 'High card'
    """The label of high cards."""
    ONE_PAIR: str = 'One pair'
    """The label of one pair."""
    TWO_PAIR: str = 'Two pair'
    """The label of two pair."""
    THREE_OF_A_KIND: str = 'Three of a kind'
    """The label of three of a kind."""
    STRAIGHT: str = 'Straight'
    """The label of straight."""
    FLUSH: str = 'Flush'
    """The label of flush."""
    FULL_HOUSE: str = 'Full house'
    """The label of full house."""
    FOUR_OF_A_KIND: str = 'Four of a kind'
    """The label of four of a kind."""
    STRAIGHT_FLUSH: str = 'Straight flush'
    """The label of straight flush."""


@dataclass(order=True, frozen=True)
class Entry:
    """The class for hand lookup entries.

    The :attr:`index` represents the strength of the corresponding
    hand. In this library, a stronger hand is considered greater. In
    other words, stronger hands have a greater index with which
    different entries and hands are compared.

    The attributes are read-only.

    Note that the entries in the example below are meaningless. They
    are only meant to show how entries are used by other poker
    utilities.

    >>> e0 = Entry(0, Label.HIGH_CARD)
    >>> e1 = Entry(1, Label.HIGH_CARD)
    >>> e2 = Entry(1, Label.HIGH_CARD)
    >>> e0 < e1
    True
    >>> e1 < e2
    False
    >>> e0 == e1
    False
    >>> e1 == e2
    True
    >>> e0.index
    0
    >>> e0.label
    <Label.HIGH_CARD: 'High card'>
    """

    index: int
    """The index of the corresponding hand."""
    label: Label = field(compare=False)
    """The label of the corresponding hand."""


@dataclass
class Lookup(ABC):
    """The abstract base class for hand lookups.

    Lookups are used internally by hands. If you want to evaluate poker
    hands, please use one of the hand classes.

    >>> lookup = StandardLookup()
    >>> e0 = lookup.get_entry('As3sQhJsJc')
    >>> e1 = lookup.get_entry('2s4sKhKsKc')
    >>> e0 < e1
    True
    >>> e0.label
    <Label.ONE_PAIR: 'One pair'>
    >>> e1.label
    <Label.THREE_OF_A_KIND: 'Three of a kind'>
    """

    __primes = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41

    assert len(__primes) >= len(tuple(Rank))

    __multipliers = dict(zip(Rank, __primes))
    __entries: dict[tuple[int, bool], Entry] = field(
        default_factory=dict,
        init=False,
    )
    __entry_count: int = field(default=0, init=False)

    @classmethod
    def __hash(cls, ranks: Iterable[Rank]) -> int:
        return prod(map(cls.__multipliers.__getitem__, ranks))

    @classmethod
    def __hash_multisets(
            cls,
            ranks: Reversible[Rank],
            counter: Counter[int],
    ) -> Sequence[int]:
        if not counter:
            return (cls.__hash(()),)

        hashes = []
        multiplicity = max(counter)
        count = counter.pop(multiplicity)

        for samples in combinations(reversed(ranks), count):
            hash_ = cls.__hash(samples) ** multiplicity

            for partial_hash in cls.__hash_multisets(
                    tuple(filterfalse(partial(contains, samples), ranks)),
                    counter,
            ):
                hashes.append(hash_ * partial_hash)

        counter[multiplicity] = count

        return hashes

    def has_entry(self, cards: Iterable[Card] | str | Card | None) -> bool:
        """Return whether the cards can be looked up.

        The cards can be looked up if the lookup contains an entry with
        the given cards.

        >>> lookup = ShortDeckHoldemLookup()
        >>> lookup.has_entry('Ah6h7s8c9s')
        True
        >>> lookup.has_entry('Ah6h7s8c2s')
        False

        :param cards: The cards to look up.
        :return: ``True`` if the cards can looked up, otherwise
                 ``False``.
        """
        return self.__get_key(cards) in self.__entries

    def get_entry(self, cards: Iterable[Card] | str | Card | None) -> Entry:
        """Return the corresponding lookup entry of the hand that the
        cards form.

        >>> lookup = ShortDeckHoldemLookup()
        >>> entry = lookup.get_entry('Ah6h7s8c9s')
        >>> entry.index
        1134
        >>> entry.label
        <Label.STRAIGHT: 'Straight'>
        >>> entry = lookup.get_entry('Ah6h7s8c2s')
        Traceback (most recent call last):
            ...
        ValueError: cards form an invalid hand

        :param cards: The cards to look up.
        :return: The corresponding lookup entry.
        :raises ValueError: If cards do not form a valid hand.
        """
        key = self.__get_key(cards)

        if key not in self.__entries:
            raise ValueError('cards form an invalid hand')

        return self.__entries[key]

    def get_entry_or_none(
            self,
            cards: Iterable[Card] | str | Card | None,
    ) -> Entry | None:
        """Return the corresponding lookup entry of the hand that the
        cards form if it exists. Otherwise, return ``None``.

        >>> lookup = ShortDeckHoldemLookup()
        >>> lookup.get_entry('Ah6h7s8c2s')
        Traceback (most recent call last):
            ...
        ValueError: cards form an invalid hand
        >>> lookup.get_entry_or_none('Ah6h7s8c2s') is None
        True

        :param cards: The cards to look up.
        :return: The optional corresponding lookup entry.
        """
        return self.__entries.get(self.__get_key(cards))

    def __get_key(
            self,
            cards: Iterable[Card] | str | Card | None,
    ) -> tuple[int, bool]:
        cards = Card.clean(cards)
        hash_ = self.__hash(Card.get_ranks(cards))
        suitedness = Card.are_suited(cards)

        return hash_, suitedness

    def _add_multisets(
            self,
            rank_order: RankOrder,
            counter: Counter[int],
            suitednesses: tuple[bool, ...],
            label: Label,
    ) -> None:
        hashes = self.__hash_multisets(rank_order, counter)

        for hash_ in reversed(hashes):
            self.__add(hash_, suitednesses, label)

    def _add_straights(
            self,
            rank_order: RankOrder,
            count: int,
            suitednesses: tuple[bool, ...],
            label: Label,
    ) -> None:
        self.__add(
            self.__hash(rank_order[-1:] + rank_order[: count - 1]),
            suitednesses,
            label,
        )

        for i in range(len(rank_order) - count + 1):
            self.__add(
                self.__hash(rank_order[i:i + count]),
                suitednesses,
                label,
            )

    def __add(
            self,
            hash_: int,
            suitednesses: Iterable[bool],
            label: Label,
    ) -> None:
        entry = Entry(self.__entry_count, label)
        self.__entry_count += 1

        for suitedness in suitednesses:
            self.__entries[hash_, suitedness] = entry


@dataclass
class StandardLookup(Lookup):
    """The class for standard hand lookups.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please subclasses of :class:`pokerkit.hands.Hand` that use this
    lookup.

    >>> lookup = StandardLookup()
    >>> e0 = lookup.get_entry('Ah6h7s8c9s')
    >>> e1 = lookup.get_entry('AhAc6s6hTd')
    >>> e2 = lookup.get_entry('AcAdAhAsAc')
    Traceback (most recent call last):
        ...
    ValueError: cards form an invalid hand
    >>> e0 < e1
    True
    >>> e0.label
    <Label.HIGH_CARD: 'High card'>
    >>> e1.label
    <Label.TWO_PAIR: 'Two pair'>
    """

    def __post_init__(self) -> None:
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({1: 5}),
            (False,),
            Label.HIGH_CARD,
        )
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({2: 1, 1: 3}),
            (False,),
            Label.ONE_PAIR,
        )
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({2: 2, 1: 1}),
            (False,),
            Label.TWO_PAIR,
        )
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({3: 1, 1: 2}),
            (False,),
            Label.THREE_OF_A_KIND,
        )
        self._add_straights(RankOrder.STANDARD, 5, (False,), Label.STRAIGHT)
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({1: 5}),
            (True,),
            Label.FLUSH,
        )
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({3: 1, 2: 1}),
            (False,),
            Label.FULL_HOUSE,
        )
        self._add_multisets(
            RankOrder.STANDARD,
            Counter({4: 1, 1: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )
        self._add_straights(
            RankOrder.STANDARD,
            5,
            (True,),
            Label.STRAIGHT_FLUSH,
        )


@dataclass
class ShortDeckHoldemLookup(Lookup):
    """The class for short-deck hold'em hand lookups.

    Here, flushes beat full houses.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please use :class:`pokerkit.hands.ShortDeckHoldemHand`.

    >>> lookup = ShortDeckHoldemLookup()
    >>> e0 = lookup.get_entry('AhAc6s6hTd')
    >>> e1 = lookup.get_entry('Ah6h7s8c9s')
    >>> e2 = lookup.get_entry('Ah2h3s4c5s')
    Traceback (most recent call last):
        ...
    ValueError: cards form an invalid hand
    >>> e0 < e1
    True
    >>> e0.label
    <Label.TWO_PAIR: 'Two pair'>
    >>> e1.label
    <Label.STRAIGHT: 'Straight'>
    """

    def __post_init__(self) -> None:
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({1: 5}),
            (False,),
            Label.HIGH_CARD,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({2: 1, 1: 3}),
            (False,),
            Label.ONE_PAIR,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({2: 2, 1: 1}),
            (False,),
            Label.TWO_PAIR,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({3: 1, 1: 2}),
            (False,),
            Label.THREE_OF_A_KIND,
        )
        self._add_straights(
            RankOrder.SHORT_DECK_HOLDEM,
            5,
            (False,),
            Label.STRAIGHT,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({3: 1, 2: 1}),
            (False,),
            Label.FULL_HOUSE,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({1: 5}),
            (True,),
            Label.FLUSH,
        )
        self._add_multisets(
            RankOrder.SHORT_DECK_HOLDEM,
            Counter({4: 1, 1: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )
        self._add_straights(
            RankOrder.SHORT_DECK_HOLDEM,
            5,
            (True,),
            Label.STRAIGHT_FLUSH,
        )


@dataclass
class EightOrBetterLookup(Lookup):
    """The class for eight or better hand lookups.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please use :class:`pokerkit.hands.EightOrBetterLowHand`.
    """

    def __post_init__(self) -> None:
        self._add_multisets(
            RankOrder.EIGHT_OR_BETTER_LOW,
            Counter({1: 5}),
            (False, True),
            Label.HIGH_CARD,
        )


@dataclass
class RegularLowLookup(Lookup):
    """The class for regular low hand lookups.

    Here, flushes are ignored.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please use :class:`pokerkit.hands.RegularLowHand`.

    >>> lookup = RegularLowLookup()
    >>> e0 = lookup.get_entry('Ah6h7s8c9s')
    >>> e1 = lookup.get_entry('AhAc6s6hTd')
    >>> e2 = lookup.get_entry('3s4sQhTc')
    Traceback (most recent call last):
        ...
    ValueError: cards form an invalid hand
    >>> e0 < e1
    True
    >>> e0.label
    <Label.HIGH_CARD: 'High card'>
    >>> e1.label
    <Label.TWO_PAIR: 'Two pair'>
    """

    def __post_init__(self) -> None:
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({1: 5}),
            (False, True),
            Label.HIGH_CARD,
        )
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({2: 1, 1: 3}),
            (False,),
            Label.ONE_PAIR,
        )
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({2: 2, 1: 1}),
            (False,),
            Label.TWO_PAIR,
        )
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({3: 1, 1: 2}),
            (False,),
            Label.THREE_OF_A_KIND,
        )
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({3: 1, 2: 1}),
            (False,),
            Label.FULL_HOUSE,
        )
        self._add_multisets(
            RankOrder.REGULAR,
            Counter({4: 1, 1: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )


@dataclass
class BadugiLookup(Lookup):
    """The class for badugi hand lookups.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please use :class:`pokerkit.hands.BadugiHand`.

    >>> lookup = BadugiLookup()
    >>> e0 = lookup.get_entry('2s')
    >>> e1 = lookup.get_entry('KhQc')
    >>> e2 = lookup.get_entry('AcAdAhAs')
    Traceback (most recent call last):
        ...
    ValueError: cards form an invalid hand
    >>> e0 > e1
    True
    >>> e0.label
    <Label.HIGH_CARD: 'High card'>
    >>> e1.label
    <Label.HIGH_CARD: 'High card'>
    """

    def __post_init__(self) -> None:
        for i in range(4, 0, -1):
            self._add_multisets(
                RankOrder.REGULAR,
                Counter({1: i}),
                (i == 1,),
                Label.HIGH_CARD,
            )


@dataclass
class KuhnPokerLookup(Lookup):
    """The class for Kuhn poker hand lookups.

    Lookups are used by evaluators. If you want to evaluate poker hands,
    please use :class:`pokerkit.hands.KuhnPokerHand`.

    >>> lookup = KuhnPokerLookup()
    >>> e0 = lookup.get_entry('Js')
    >>> e1 = lookup.get_entry('Qs')
    >>> e2 = lookup.get_entry('2c')
    Traceback (most recent call last):
        ...
    ValueError: cards form an invalid hand
    >>> e0 < e1
    True
    >>> e0.label
    <Label.HIGH_CARD: 'High card'>
    >>> e1.label
    <Label.HIGH_CARD: 'High card'>
    """

    def __post_init__(self) -> None:
        self._add_multisets(
            RankOrder.KUHN_POKER,
            Counter({1: 1}),
            (True,),
            Label.HIGH_CARD,
        )
