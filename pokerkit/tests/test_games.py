""":mod:`pokerkit.tests.test_games` implements unit tests for
:mod:`pokerkit.test_games`.
"""

from unittest import TestCase

from pokerkit.games import Poker


class StandardLookupTestCase(TestCase):
    def test_clean_values(self) -> None:
        self.assertEqual(Poker._clean_values(5, 6), (5,) * 6)
        self.assertEqual(Poker._clean_values([1, 2], 6), (1, 2, 0, 0, 0, 0))
        self.assertEqual(
            Poker._clean_values({0: 1, 1: 2}, 6),
            (1, 2, 0, 0, 0, 0),
        )
        self.assertEqual(Poker._clean_values({-1: 2}, 6), (0, 0, 0, 0, 0, 2))
        self.assertEqual(Poker._clean_values(None, 6), (0, 0, 0, 0, 0, 0))
        self.assertRaises(AssertionError, Poker._clean_values, type, 6)
