from unittest import TestCase, main

from pokertools import FixedLimitFiveCardDraw, NoLimitFiveCardDraw, PotLimitFiveCardDraw
from pokertools.tests import PokerTestCaseMixin


class FixedLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitFiveCardDraw

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitFiveCardDraw

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitFiveCardDraw

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


if __name__ == '__main__':
    main()
