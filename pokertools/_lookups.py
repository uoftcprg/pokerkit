from abc import ABC
from collections import Iterable
from itertools import chain, combinations, islice

from auxiliary import const, rotate, window
from math2.misc import product

from pokertools.cards import Card, Rank

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def ranks_key(ranks: Iterable[Rank]) -> int:
    return product(PRIMES[rank.index] for rank in ranks) if ranks else 1


def straights(count: int, ranks: set[Rank]) -> Iterable[int]:
    keys = [ranks_key(islice(rotate(sorted(ranks), -1), 0, count))]

    for sub_ranks in window(sorted(ranks), count):
        keys.append(ranks_key(sub_ranks))

    return reversed(keys)


def multiples(frequencies: dict[int, int], ranks: set[Rank]) -> Iterable[int]:
    if frequencies:
        keys = []
        count = max(frequencies)
        frequency = frequencies.pop(count)

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
    def __init__(self) -> None:
        self.suited_indices: dict[int, int] = {}
        self.unsuited_indices: dict[int, int] = {}
        self.index_count: int = 0

    def index(self, cards: Iterable[Card]) -> int:
        ranks, suits = zip(*((card.rank, card.suit) for card in cards))
        key = ranks_key(ranks)

        try:
            if const(suits):
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
        super().__init__()

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
        return min(super(StandardLookup, self).index(combination) for combination in combinations(cards, 5))


class ShortLookup(Lookup):
    def __init__(self) -> None:
        super().__init__()

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
        return min(super(ShortLookup, self).index(combination) for combination in combinations(cards, 5))
