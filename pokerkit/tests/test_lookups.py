""":mod:`pokerkit.tests.test_lookups` implements unit tests for
:mod:`pokerkit.test_lookups`.
"""

from collections.abc import Iterable
from hashlib import md5
from itertools import combinations
from unittest import main, TestCase

from pokerkit.lookups import (
    BadugiLookup,
    EightOrBetterLookup,
    KuhnPokerLookup,
    RegularLookup,
    ShortDeckHoldemLookup,
    StandardBadugiLookup,
    StandardLookup,
)
from pokerkit.utilities import Card, Deck


class LookupTestCaseMixin:
    @classmethod
    def serialize_combinations(
            cls,
            combinations_: Iterable[Iterable[Card]],
    ) -> str:
        return '\n'.join(map(cls.serialize_combination, combinations_))

    @classmethod
    def serialize_combination(cls, combination: Iterable[Card]) -> str:
        return ''.join(map(repr, combination))


class StandardLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = StandardLookup()
        combinations_ = sorted(
            combinations(Deck.STANDARD, 5),
            key=lookup.get_entry,
        )
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '488cdd27873395ba75205cd02fb9d6b2',
        )


class ShortDeckHoldemLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = ShortDeckHoldemLookup()
        combinations_ = sorted(
            combinations(Deck.SHORT_DECK_HOLDEM, 5),
            key=lookup.get_entry,
        )
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '5b46b727ce4526a68d41b0e55939353c',
        )


class EightOrBetterLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = EightOrBetterLookup()
        combinations_ = sorted(
            filter(lookup.has_entry, combinations(Deck.REGULAR, 5)),
            key=lookup.get_entry,
        )
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            'ecf2b6b16031562a6761932b1ce1de91',
        )


class RegularLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = RegularLookup()
        combinations_ = sorted(
            combinations(Deck.REGULAR, 5),
            key=lookup.get_entry,
        )
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '28925b97b06a1e674eaabf241a441e15',
        )


class BadugiLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = BadugiLookup()
        combinations_ = []

        for n in range(1, 5):
            for cards in combinations(Deck.REGULAR, n):
                pairedness = Card.are_paired(cards)
                suitedness = Card.are_suited(cards)
                rainbowness = Card.are_rainbow(cards)

                if not pairedness and rainbowness:
                    combinations_.append(cards)
                elif pairedness or suitedness:
                    self.assertRaises(ValueError, lookup.get_entry, cards)

        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '9d29ddbc3f76d815e166c6faa2af9021',
        )


class StandardBadugiLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = StandardBadugiLookup()
        combinations_ = []

        for n in range(1, 5):
            for cards in combinations(Deck.STANDARD, n):
                pairedness = Card.are_paired(cards)
                suitedness = Card.are_suited(cards)
                rainbowness = Card.are_rainbow(cards)

                if not pairedness and rainbowness:
                    combinations_.append(cards)
                elif pairedness or suitedness:
                    self.assertRaises(ValueError, lookup.get_entry, cards)

        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '06886dd57a4c7b780953f5090c63bcfe',
        )


class KuhnPokerLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        lookup = KuhnPokerLookup()
        combinations_ = sorted(
            combinations(Deck.KUHN_POKER, 1),
            key=lookup.get_entry,
        )
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            'bb7d5e9f8fe4f404fd1551d8995ca1a2',
        )


if __name__ == '__main__':
    main()  # pragma: no cover
