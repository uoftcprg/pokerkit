from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, MutableMapping, Sequence
from itertools import chain, combinations
from math import prod

from auxiliary import unique, windowed

from pokertools.cards import ACE_LOW_RANKS, Card, Rank, SHORT_DECK_RANKS, STANDARD_RANKS
from pokertools.utils import suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def mask(ranks: Iterable[Rank]) -> int:
    return prod(PRIMES[rank.index] for rank in ranks)


def straights(ranks: Sequence[Rank], count: int) -> Iterator[int]:
    keys = [PRIMES[ranks[-1].index] * mask(ranks[:count - 1])]

    for sub_ranks in windowed(ranks, count):
        keys.append(mask(sub_ranks))

    return reversed(keys)


def multiples(ranks: Sequence[Rank], frequencies: MutableMapping[int, int]) -> Iterator[int]:
    if frequencies:
        keys = []
        count = max(frequencies)
        freq = frequencies.pop(count)

        for samples in combinations(reversed(ranks), freq):
            key = mask(samples) ** count

            for sub_key in multiples(tuple(rank for rank in ranks if rank not in samples), frequencies):
                keys.append(key * sub_key)

        frequencies[count] = freq
        return iter(keys)
    else:
        return iter((1,))


class Lookup(ABC):
    def __init__(self) -> None:
        self.populate()

    @property
    @abstractmethod
    def index_count(self) -> int: ...

    @abstractmethod
    def populate(self) -> None: ...

    @abstractmethod
    def index(self, cards: Iterable[Card]) -> int: ...


class UnsuitedLookup(Lookup, ABC):
    def __init__(self) -> None:
        self.unsuited = dict[int, int]()

        super().__init__()

    @property
    def index_count(self) -> int:
        return len(self.unsuited)

    def index(self, cards: Iterable[Card]) -> int:
        try:
            return self.unsuited[mask(card.rank for card in cards)]
        except KeyError:
            raise ValueError('Invalid card combination')


class SuitedLookup(UnsuitedLookup, ABC):
    def __init__(self) -> None:
        self.suited = dict[int, int]()

        super().__init__()

    @property
    def index_count(self) -> int:
        return super().index_count + len(self.suited)

    def index(self, cards: Iterable[Card]) -> int:
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        try:
            key = mask(card.rank for card in cards)

            return min(self.suited[key], self.unsuited[key]) if suited(cards) else self.unsuited[key]
        except KeyError:
            raise ValueError('Invalid card combination')


class StandardLookup(SuitedLookup):
    def populate(self) -> None:
        for key in straights(STANDARD_RANKS, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(STANDARD_RANKS, {4: 1, 1: 1}), multiples(STANDARD_RANKS, {3: 1, 2: 1})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(STANDARD_RANKS, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(straights(STANDARD_RANKS, 5), multiples(STANDARD_RANKS, {3: 1, 1: 2}),
                         multiples(STANDARD_RANKS, {2: 2, 1: 1}), multiples(STANDARD_RANKS, {2: 1, 1: 3}),
                         multiples(STANDARD_RANKS, {1: 5})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

    def index(self, cards: Iterable[Card]) -> int:
        return min(super(StandardLookup, self).index(combination) for combination in combinations(cards, 5))


class ShortLookup(SuitedLookup):
    def populate(self) -> None:
        for key in straights(SHORT_DECK_RANKS, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in multiples(SHORT_DECK_RANKS, {4: 1, 1: 1}):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(SHORT_DECK_RANKS, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(SHORT_DECK_RANKS, {3: 1, 2: 1}), straights(SHORT_DECK_RANKS, 5),
                         multiples(SHORT_DECK_RANKS, {3: 1, 1: 2}), multiples(SHORT_DECK_RANKS, {2: 2, 1: 1}),
                         multiples(SHORT_DECK_RANKS, {2: 1, 1: 3}), multiples(SHORT_DECK_RANKS, {1: 5})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

    def index(self, cards: Iterable[Card]) -> int:
        return min(super(ShortLookup, self).index(combination) for combination in combinations(cards, 5))


class BadugiLookup(UnsuitedLookup):
    def populate(self) -> None:
        for n in range(5):
            for key in multiples(ACE_LOW_RANKS, {1: n}):
                self.unsuited[key] = self.index_count

    def index(self, cards: Iterable[Card]) -> int:
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        return -max(super(BadugiLookup, self).index(sub_cards) for n in range(5) for sub_cards in combinations(
            cards, n) if unique(card.rank for card in sub_cards) and unique(card.suit for card in sub_cards))


class LowballA5Lookup(UnsuitedLookup):
    def populate(self) -> None:
        for key in chain(multiples(ACE_LOW_RANKS, {4: 1, 1: 1}), multiples(ACE_LOW_RANKS, {3: 1, 2: 1}),
                         multiples(ACE_LOW_RANKS, {3: 1, 1: 2}), multiples(ACE_LOW_RANKS, {2: 2, 1: 1}),
                         multiples(ACE_LOW_RANKS, {2: 1, 1: 3}), multiples(ACE_LOW_RANKS, {1: 5})):
            self.unsuited[key] = self.index_count

    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(LowballA5Lookup, self).index(combination) for combination in combinations(cards, 5))


class Lowball27Lookup(StandardLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(StandardLookup, self).index(combination) for combination in combinations(cards, 5))
