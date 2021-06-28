from unittest import TestCase, main

from pokertools import FixedLimitFiveCardDraw, NoLimitFiveCardDraw, PotLimitFiveCardDraw
from pokertools.tests import PokerTestCaseMixin


class FixedLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitFiveCardDraw

    def test_hands(self):
        ...


class PotLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitFiveCardDraw

    def test_hands(self):
        ...


class NoLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitFiveCardDraw

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
