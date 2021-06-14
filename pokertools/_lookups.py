from abc import ABC, abstractmethod
from collections.abc import Iterator
from itertools import chain, combinations
from math import prod

from pokertools.cards import Rank, Ranks
from pokertools.utils import rainbow, suited

PRIMES = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41


def mask_of(ranks):
    return prod(map(PRIMES.__getitem__, map(Rank._index.__get__, ranks)))


def straights_of(ranks, count):
    keys = [PRIMES[ranks[-1]._index] * mask_of(ranks[:count - 1])]

    for sub_ranks in (ranks[i:i + count] for i in range(len(ranks) - count + 1)):
        keys.append(mask_of(sub_ranks))

    return reversed(keys)


def multiples_of(ranks, frequencies):
    if frequencies:
        keys = []
        count = max(frequencies)
        freq = frequencies.pop(count)

        for samples in combinations(reversed(ranks), freq):
            key = mask_of(samples) ** count

            for sub_key in multiples_of(tuple(rank for rank in ranks if rank not in samples), frequencies):
                keys.append(key * sub_key)

        frequencies[count] = freq
        return keys
    else:
        return 1,


class Lookup(ABC):
    def __init__(self):
        self.populate()

    @property
    @abstractmethod
    def index_count(self): ...

    @abstractmethod
    def populate(self): ...

    @abstractmethod
    def get_index(self, cards): ...


class UnsuitedLookup(Lookup, ABC):
    def __init__(self):
        self.unsuited = {}

        super().__init__()

    @property
    def index_count(self):
        return len(self.unsuited)

    def get_index(self, cards):
        try:
            return self.unsuited[mask_of(card.rank for card in cards)]
        except KeyError:
            raise ValueError('Invalid card combination')


class SuitedLookup(UnsuitedLookup, ABC):
    def __init__(self):
        self.suited = {}

        super().__init__()

    @property
    def index_count(self):
        return super().index_count + len(self.suited)

    def get_index(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        try:
            key = mask_of(card.rank for card in cards)

            return min(self.suited[key], self.unsuited[key]) if suited(cards) else self.unsuited[key]
        except KeyError:
            raise ValueError('Invalid card combination')


class StandardLookup(SuitedLookup):
    def populate(self):
        for key in straights_of(Ranks.STANDARD_RANKS.value, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                multiples_of(Ranks.STANDARD_RANKS.value, {4: 1, 1: 1}),
                multiples_of(Ranks.STANDARD_RANKS.value, {3: 1, 2: 1}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples_of(Ranks.STANDARD_RANKS.value, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                straights_of(Ranks.STANDARD_RANKS.value, 5),
                multiples_of(Ranks.STANDARD_RANKS.value, {3: 1, 1: 2}),
                multiples_of(Ranks.STANDARD_RANKS.value, {2: 2, 1: 1}),
                multiples_of(Ranks.STANDARD_RANKS.value, {2: 1, 1: 3}),
                multiples_of(Ranks.STANDARD_RANKS.value, {1: 5}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

    def get_index(self, cards):
        return min(super(StandardLookup, self).get_index(combination) for combination in combinations(cards, 5))


class ShortLookup(SuitedLookup):
    def populate(self):
        for key in straights_of(Ranks.SHORT_DECK_RANKS.value, 5):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in multiples_of(Ranks.SHORT_DECK_RANKS.value, {4: 1, 1: 1}):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

        for key in multiples_of(Ranks.SHORT_DECK_RANKS.value, {1: 5}):
            if key not in self.suited:
                self.suited[key] = self.index_count

        for key in chain(
                multiples_of(Ranks.SHORT_DECK_RANKS.value, {3: 1, 2: 1}),
                straights_of(Ranks.SHORT_DECK_RANKS.value, 5),
                multiples_of(Ranks.SHORT_DECK_RANKS.value, {3: 1, 1: 2}),
                multiples_of(Ranks.SHORT_DECK_RANKS.value, {2: 2, 1: 1}),
                multiples_of(Ranks.SHORT_DECK_RANKS.value, {2: 1, 1: 3}),
                multiples_of(Ranks.SHORT_DECK_RANKS.value, {1: 5}),
        ):
            if key not in self.unsuited:
                self.unsuited[key] = self.index_count

    def get_index(self, cards):
        return min(super(ShortLookup, self).get_index(combination) for combination in combinations(cards, 5))


class BadugiLookup(UnsuitedLookup):
    def populate(self):
        for n in range(5):
            for key in multiples_of(Ranks.ACE_LOW_RANKS.value, {1: n}):
                self.unsuited[key] = self.index_count

    def get_index(self, cards):
        if isinstance(cards, Iterator):
            cards = tuple(cards)

        return -max(
            super(BadugiLookup, self).get_index(sub_cards) for n in range(5) for sub_cards in combinations(cards, n)
            if rainbow(card.rank for card in sub_cards) and rainbow(card.suit for card in sub_cards)
        )


class LowballA5Lookup(UnsuitedLookup):
    def populate(self):
        for key in chain(
                multiples_of(Ranks.ACE_LOW_RANKS.value, {4: 1, 1: 1}),
                multiples_of(Ranks.ACE_LOW_RANKS.value, {3: 1, 2: 1}),
                multiples_of(Ranks.ACE_LOW_RANKS.value, {3: 1, 1: 2}),
                multiples_of(Ranks.ACE_LOW_RANKS.value, {2: 2, 1: 1}),
                multiples_of(Ranks.ACE_LOW_RANKS.value, {2: 1, 1: 3}),
                multiples_of(Ranks.ACE_LOW_RANKS.value, {1: 5}),
        ):
            self.unsuited[key] = self.index_count

    def get_index(self, cards):
        return -max(super(LowballA5Lookup, self).get_index(combination) for combination in combinations(cards, 5))


class Lowball27Lookup(StandardLookup):
    def get_index(self, cards):
        return -max(super(StandardLookup, self).get_index(combination) for combination in combinations(cards, 5))
