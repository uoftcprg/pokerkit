from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, MutableMapping
from itertools import chain, combinations, islice

from auxiliary import retain_iter, rotated, unique, windowed
from math2.misc import prod

from pokertools.cards import AL_RANKS, Card, Rank, SHORT_RANKS, STD_RANKS
from pokertools.utils import suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def mask(ranks: Iterable[Rank]) -> int:
    return prod((PRIMES[rank.index] for rank in ranks), 1)


@retain_iter
def straights(ranks: Iterable[Rank], count: int) -> Iterator[int]:
    keys = [mask(islice(rotated(ranks, -1), 0, count))]

    for sub_ranks in windowed(ranks, count):
        keys.append(mask(sub_ranks))

    return reversed(keys)


@retain_iter
def multiples(ranks: Iterable[Rank], freqs: MutableMapping[int, int]) -> Iterator[int]:
    if sum(freqs.values()):
        keys = []
        count = max(freqs)
        freq = freqs.pop(count)

        for samples in combinations(tuple(ranks)[::-1], freq):
            key = mask(samples * count)

            for sub_key in multiples((rank for rank in ranks if rank not in samples), freqs):
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

    @retain_iter
    def index(self, cards: Iterable[Card]) -> int:
        try:
            key = mask(card.rank for card in cards)

            return min(self.suited[key], self.unsuited[key]) if suited(cards) else self.unsuited[key]
        except KeyError:
            raise ValueError('Invalid card combination')


class StdLookup(SuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return min(super(StdLookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        for key in straights(STD_RANKS, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(STD_RANKS, {4: 1, 1: 1}), multiples(STD_RANKS, {3: 1, 2: 1})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(STD_RANKS, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(straights(STD_RANKS, 5), multiples(STD_RANKS, {3: 1, 1: 2}),
                         multiples(STD_RANKS, {2: 2, 1: 1}), multiples(STD_RANKS, {2: 1, 1: 3}),
                         multiples(STD_RANKS, {1: 5})):
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
    @retain_iter
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(BadugiLookup, self).index(sub_cards) for n in range(5) for sub_cards in combinations(cards, n)
                    if unique(card.rank for card in sub_cards) and unique(card.suit for card in sub_cards))

    def populate(self) -> None:
        for n in range(5):
            for key in multiples(AL_RANKS, {1: n}):
                self.unsuited[key] = self.index_count


class LBA5Lookup(UnsuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(LBA5Lookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        for key in chain(multiples(AL_RANKS, {4: 1, 1: 1}), multiples(AL_RANKS, {3: 1, 2: 1}),
                         multiples(AL_RANKS, {3: 1, 1: 2}), multiples(AL_RANKS, {2: 2, 1: 1}),
                         multiples(AL_RANKS, {2: 1, 1: 3}), multiples(AL_RANKS, {1: 5})):
            self.unsuited[key] = self.index_count


class LB27Lookup(StdLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return -max(super(StdLookup, self).index(combination) for combination in combinations(cards, 5))
