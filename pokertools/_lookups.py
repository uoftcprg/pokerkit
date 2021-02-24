from abc import ABC
from collections import Iterable
from itertools import chain, combinations

from auxiliary.utils import constant, product, rotate, window

from pokertools.cards import Card, Rank

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def ranks_key(ranks: Iterable[Rank]) -> int:
    return product(PRIMES[rank.index] for rank in ranks) if ranks else 1


def straights(count: int, ranks: set[Rank]) -> Iterable[int]:
    keys = [ranks_key(tuple(rotate(sorted(ranks), -1))[:count])]

    for sub_ranks in window(sorted(ranks), count):
        keys.append(ranks_key(sub_ranks))

    return reversed(keys)


def multiples(frequencies: dict[int, int], ranks: set[Rank]) -> list[int]:
    if frequencies:
        keys = []
        count, frequency = max(frequencies), frequencies.pop(max(frequencies))

        for samples in combinations(sorted(ranks, reverse=True), frequency):
            key_base = ranks_key(samples * count)
            ranks -= set(samples)

            for sub_key in multiples(frequencies, ranks):
                keys.append(key_base * sub_key)

            ranks |= set(samples)

        frequencies[count] = frequency
        return keys
    else:
        return [1]


class Lookup(ABC):
    suited_indices: dict[int, int]
    unsuited_indices: dict[int, int]
    index_count: int

    def index(self, cards: Iterable[Card]) -> int:
        ranks, suits = zip(*((card.rank, card.suit) for card in cards))
        key = ranks_key(ranks)

        try:
            if constant(suits):
                return min(self.suited_indices[key], self.unsuited_indices[key])
            else:
                return self.unsuited_indices[key]
        except KeyError:
            raise ValueError('Cards do not form a valid hand')

    def register(self, indices: dict[int, int], key: int) -> None:
        if key not in indices:
            indices[key] = self.index_count
            self.index_count += 1


class StandardLookup(Lookup):
    def __init__(self) -> None:
        self.suited_indices = {}
        self.unsuited_indices = {}
        self.index_count = 0

        ranks = set(Rank)

        for key in straights(5, ranks):
            self.register(self.suited_indices, key)

        for key in chain(multiples({4: 1, 1: 1}, ranks), multiples({3: 1, 2: 1}, ranks)):
            self.register(self.unsuited_indices, key)

        for key in multiples({1: 5}, ranks):
            self.register(self.suited_indices, key)

        for key in chain(straights(5, ranks), multiples({3: 1, 1: 2}, ranks), multiples({2: 2, 1: 1}, ranks),
                         multiples({2: 1, 1: 3}, ranks), multiples({1: 5}, ranks)):
            self.register(self.unsuited_indices, key)

    def index(self, cards: Iterable[Card]) -> int:
        return min(super(StandardLookup, self).index(samples) for samples in combinations(cards, 5))


class ShortLookup(Lookup):
    def __init__(self) -> None:
        self.suited_indices = {}
        self.unsuited_indices = {}
        self.index_count = 0

        ranks = set(rank for rank in Rank if Rank.FIVE < rank)

        for key in straights(5, ranks):
            self.register(self.suited_indices, key)

        for key in multiples({4: 1, 1: 1}, ranks):
            self.register(self.unsuited_indices, key)

        for key in multiples({1: 5}, ranks):
            self.register(self.suited_indices, key)

        for key in chain(multiples({3: 1, 2: 1}, ranks), straights(5, ranks), multiples({3: 1, 1: 2}, ranks),
                         multiples({2: 2, 1: 1}, ranks), multiples({2: 1, 1: 3}, ranks), multiples({1: 5}, ranks)):
            self.register(self.unsuited_indices, key)

    def index(self, cards: Iterable[Card]) -> int:
        return min(super(ShortLookup, self).index(samples) for samples in combinations(cards, 5))
