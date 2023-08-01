""":mod:`pokerkit.tests.test_state` implements unit tests for
:mod:`pokerkit.state`.
"""

from hashlib import md5
from itertools import combinations
from unittest import TestCase

from pokerkit.state import _HighHandOpeningLookup, _LowHandOpeningLookup
from pokerkit.tests.test_lookups import LookupTestCaseMixin
from pokerkit.utilities import Deck


class LowHandOpeningLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        combinations_ = []

        for i in range(1, 5):
            for combination in combinations(Deck.STANDARD, i):
                combinations_.append(combination)

        lookup = _LowHandOpeningLookup()
        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '9b19d8c42e4b03661329b424d7b6c8e9',
        )


class HighHandOpeningLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        combinations_ = []

        for i in range(1, 5):
            for combination in combinations(Deck.STANDARD, i):
                combinations_.append(combination)

        lookup = _HighHandOpeningLookup()
        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            'b11a0c444a528e78c5be57c7bb6db06c',
        )
