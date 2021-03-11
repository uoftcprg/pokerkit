from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, MutableMapping
from itertools import chain, combinations, islice

from auxiliary import retain_iter, rotated, unique, windowed
from math2.misc import prod

from pokertools.cards import Card, Rank
from pokertools.utils import suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def mask(ranks: Iterable[Rank]) -> int:
    return prod((PRIMES[rank.index] for rank in ranks), 1)


@retain_iter
def straights(ranks: Iterable[Rank], count: int) -> Iterator[int]:
    keys = [mask(islice(rotated(sorted(ranks), -1), 0, count))]

    for sub_ranks in windowed(sorted(ranks), count):
        keys.append(mask(sub_ranks))

    return reversed(keys)


def multiples(ranks: Iterable[Rank], frequencies: MutableMapping[int, int]) -> Iterator[int]:
    if frequencies:
        ranks = frozenset(ranks)
        keys = []
        count = max(frequencies)
        frequency = frequencies.pop(count)

        for samples in combinations(sorted(ranks, reverse=True), frequency):
            key = mask(samples * count)
            ranks -= frozenset(samples)

            for sub_key in multiples(ranks, frequencies):
                keys.append(key * sub_key)

            ranks |= frozenset(samples)

        frequencies[count] = frequency
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
        return self.unsuited[mask(card.rank for card in cards)]

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
        key = mask(card.rank for card in cards)

        if suited(cards):
            return min(self.suited[key], self.unsuited[key])
        else:
            return self.unsuited[key]


class StdLookup(SuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return min(super(StdLookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        for key in straights(Rank, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(Rank, {4: 1, 1: 1}), multiples(Rank, {3: 1, 2: 1})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(Rank, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(straights(Rank, 5), multiples(Rank, {3: 1, 1: 2}), multiples(Rank, {2: 2, 1: 1}),
                         multiples(Rank, {2: 1, 1: 3}), multiples(Rank, {1: 5})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count


class ShortLookup(SuitedLookup):
    def index(self, cards: Iterable[Card]) -> int:
        return min(super(ShortLookup, self).index(combination) for combination in combinations(cards, 5))

    def populate(self) -> None:
        ranks = tuple(rank for rank in Rank if Rank.FIVE < rank)

        for key in straights(ranks, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in multiples(ranks, {4: 1, 1: 1}):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(ranks, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(multiples(ranks, {3: 1, 2: 1}), straights(ranks, 5), multiples(ranks, {3: 1, 1: 2}),
                         multiples(ranks, {2: 2, 1: 1}), multiples(ranks, {2: 1, 1: 3}), multiples(ranks, {1: 5})):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count


class BadugiLookup(UnsuitedLookup):
    @retain_iter
    def index(self, cards: Iterable[Card]) -> int:
        for n in range(4, -1, -1):
            try:
                return min(super(BadugiLookup, self).index(sub_cards) for sub_cards in combinations(cards, n)
                           if unique(card.rank for card in sub_cards) and unique(card.suit for card in sub_cards))
            except ValueError:
                pass

        return self.index_count

    def populate(self) -> None:
        ranks = (Rank.ACE,) + tuple(Rank)[:-1]

        for a in ranks:
            for b in ranks[:ranks.index(a)]:
                for c in ranks[:ranks.index(b)]:
                    for d in ranks[:ranks.index(c)]:
                        self.unsuited[mask((a, b, c, d))] = self.index_count
        for a in ranks:
            for b in ranks[:ranks.index(a)]:
                for c in ranks[:ranks.index(b)]:
                    self.unsuited[mask((a, b, c))] = self.index_count
        for a in ranks:
            for b in ranks[:ranks.index(a)]:
                self.unsuited[mask((a, b))] = self.index_count
        for a in ranks:
            self.unsuited[mask((a,))] = self.index_count
        self.unsuited[1] = self.index_count
