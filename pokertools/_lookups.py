from abc import ABC, abstractmethod
from collections import Collection
from collections.abc import Iterable, Iterator, MutableMapping, Sequence
from itertools import chain, combinations, islice

from auxiliary import product, rotated, unique, windowed

from pokertools.cards import ACE_LOW_RANKS, Card, Rank, SHORT_RANKS, STANDARD_RANKS
from pokertools.utils import suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def mask(ranks: Iterable[Rank]) -> int:
    return product((PRIMES[rank.index] for rank in ranks), 1)


def straights(ranks: Sequence[Rank], count: int) -> Iterator[int]:
    keys = [mask(islice(rotated(ranks, -1), 0, count))]

    for sub_ranks in windowed(ranks, count):
        keys.append(mask(sub_ranks))

    return reversed(keys)


def multiples(ranks: Sequence[Rank], freqs: MutableMapping[int, int]) -> Iterator[int]:
    if sum(freqs.values()):
        keys = []
        count = max(freqs)
        freq = freqs.pop(count)

        for samples in combinations(reversed(ranks), freq):
            key = mask(samples * count)

            for sub_key in multiples(tuple(rank for rank in ranks if rank not in samples), freqs):
                keys.append(key * sub_key)

        freqs[count] = freq
        return iter(keys)
    else:
        return iter((1,))


class Lookup(ABC):
    @property
    @abstractmethod
    def index_count(self) -> int:
        pass

    @abstractmethod
    def index(self, cards: Iterable[Card]) -> int:
        pass


class UnsuitedLookup(Lookup):
    def __init__(self) -> None:
        self.unsuited = dict[int, int]()

        self.populate()

    @property
    def index_count(self) -> int:
        return len(self.unsuited)

    def index(self, cards: Iterable[Card]) -> int:
        try:
            return self.unsuited[mask(card.rank for card in cards)]
        except KeyError:
            raise ValueError('Invalid card combination')

    @abstractmethod
    def populate(self) -> None:
        pass


class SuitedLookup(UnsuitedLookup, ABC):
    def __init__(self) -> None:
        self.suited = dict[int, int]()

        super().__init__()

    @property
    def index_count(self) -> int:
        return super().index_count + len(self.suited)

    def index(self, cards: Iterable[Card]) -> int:
        if isinstance(cards, Collection):
            try:
                key = mask(card.rank for card in cards)

                return min(self.suited[key], self.unsuited[key]) if suited(cards) else self.unsuited[key]
            except KeyError:
                raise ValueError('Invalid card combination')
        else:
            return self.index(tuple(cards))


class StandardLookup(SuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return min(super(StandardLookup, self).index(combination) for combination in combinations(cards, 5))

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


class ShortLookup(SuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return min(super(ShortLookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        for key in straights(SHORT_RANKS, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in multiples(SHORT_RANKS, {4: 1, 1: 1}):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(SHORT_RANKS, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(SHORT_RANKS, {3: 1, 2: 1}), straights(SHORT_RANKS, 5),
                         multiples(SHORT_RANKS, {3: 1, 1: 2}), multiples(SHORT_RANKS, {2: 2, 1: 1}),
                         multiples(SHORT_RANKS, {2: 1, 1: 3}), multiples(SHORT_RANKS, {1: 5})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count


class BadugiLookup(UnsuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        if isinstance(cards, Collection):
            return -max(super(BadugiLookup, self).index(sub_cards) for n in range(5) for sub_cards in combinations(
                cards, n) if unique(card.rank for card in sub_cards) and unique(card.suit for card in sub_cards))
        else:
            return self.index(tuple(cards))

    def populate(self) -> None:
        for n in range(5):
            for key in multiples(ACE_LOW_RANKS, {1: n}):
                self.unsuited[key] = self.index_count


class LowballA5Lookup(UnsuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(LowballA5Lookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        for key in chain(multiples(ACE_LOW_RANKS, {4: 1, 1: 1}), multiples(ACE_LOW_RANKS, {3: 1, 2: 1}),
                         multiples(ACE_LOW_RANKS, {3: 1, 1: 2}), multiples(ACE_LOW_RANKS, {2: 2, 1: 1}),
                         multiples(ACE_LOW_RANKS, {2: 1, 1: 3}), multiples(ACE_LOW_RANKS, {1: 5})):
            self.unsuited[key] = self.index_count


class Lowball27Lookup(StandardLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(StandardLookup, self).index(combination) for combination in combinations(cards, 5))
