from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import partial
from itertools import chain, combinations, filterfalse
from operator import contains, getitem

from auxiliary import prod, windowed

from pokerface.cards import Card, Rank, Ranks, suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


class Lookup(ABC):
    @property
    @abstractmethod
    def index_count(self): ...

    @abstractmethod
    def get_index(self, cards): ...


class UnsuitedLookup(Lookup, ABC):
    def __init__(self):
        super().__init__()

        self.unsuited = {}

    @property
    def index_count(self):
        return len(self.unsuited)

    def get_index(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        try:
            return self.unsuited[mask(map(Card.rank.fget, cards))]
        except KeyError:
            raise ValueError('invalid card combination')


class SuitedLookup(UnsuitedLookup, ABC):
    def __init__(self):
        super().__init__()

        self.suited = {}

    @property
    def index_count(self):
        return super().index_count + len(self.suited)

    def get_index(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        try:
            key = mask(map(Card.rank.fget, cards))

            if suited(cards):
                return min(self.suited[key], self.unsuited[key])
            else:
                return self.unsuited[key]
        except KeyError:
            raise ValueError('invalid card combination')


class LowballA5Lookup(UnsuitedLookup):
    def __init__(self):
        super().__init__()

        for key in chain(
                multiples(Ranks.ACE_LOW.value, {4: 1, 1: 1}),
                multiples(Ranks.ACE_LOW.value, {3: 1, 2: 1}),
                multiples(Ranks.ACE_LOW.value, {3: 1, 1: 2}),
                multiples(Ranks.ACE_LOW.value, {2: 2, 1: 1}),
                multiples(Ranks.ACE_LOW.value, {2: 1, 1: 3}),
                multiples(Ranks.ACE_LOW.value, {1: 5}),
        ):
            self.unsuited[key] = self.index_count


class BadugiLookup(UnsuitedLookup):
    def __init__(self):
        super().__init__()

        for n in range(1, 5):
            for key in multiples(Ranks.ACE_LOW.value, {1: n}):
                self.unsuited[key] = self.index_count


class StandardLookup(SuitedLookup):
    def __init__(self):
        super().__init__()

        for key in straights(Ranks.STANDARD.value, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                multiples(Ranks.STANDARD.value, {4: 1, 1: 1}),
                multiples(Ranks.STANDARD.value, {3: 1, 2: 1}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(Ranks.STANDARD.value, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                straights(Ranks.STANDARD.value, 5),
                multiples(Ranks.STANDARD.value, {3: 1, 1: 2}),
                multiples(Ranks.STANDARD.value, {2: 2, 1: 1}),
                multiples(Ranks.STANDARD.value, {2: 1, 1: 3}),
                multiples(Ranks.STANDARD.value, {1: 5}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count


class ShortDeckLookup(SuitedLookup):
    def __init__(self):
        super().__init__()

        for key in straights(Ranks.SHORT_DECK.value, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in multiples(Ranks.SHORT_DECK.value, {4: 1, 1: 1}):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples(Ranks.SHORT_DECK.value, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                multiples(Ranks.SHORT_DECK.value, {3: 1, 2: 1}),
                straights(Ranks.SHORT_DECK.value, 5),
                multiples(Ranks.SHORT_DECK.value, {3: 1, 1: 2}),
                multiples(Ranks.SHORT_DECK.value, {2: 2, 1: 1}),
                multiples(Ranks.SHORT_DECK.value, {2: 1, 1: 3}),
                multiples(Ranks.SHORT_DECK.value, {1: 5}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count


def straights(ranks, count):
    keys = [PRIMES[ranks[-1].index] * mask(ranks[:count - 1])]

    for straight in windowed(ranks, count):
        keys.append(mask(straight))

    return reversed(keys)


def multiples(ranks, frequencies):
    if not frequencies:
        return 1,

    keys = []
    count = max(frequencies)
    freq = frequencies.pop(count)

    for samples in combinations(reversed(ranks), freq):
        key = mask(samples) ** count

        for sub_key in multiples(
                tuple(filterfalse(partial(contains, samples), ranks)),
                frequencies,
        ):
            keys.append(key * sub_key)

    frequencies[count] = freq

    return keys


def mask(ranks):
    return prod(map(partial(getitem, PRIMES), map(Rank.index.fget, ranks)))
