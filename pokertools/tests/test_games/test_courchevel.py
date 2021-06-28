from unittest import TestCase, main

from pokertools import FixedLimitCourchevel, NoLimitCourchevel, PotLimitCourchevel
from pokertools.tests import PokerTestCaseMixin


class FixedLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitCourchevel

    def test_hands(self):
        ...


class PotLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitCourchevel

    def test_hands(self):
        ...


class NoLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitCourchevel

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
