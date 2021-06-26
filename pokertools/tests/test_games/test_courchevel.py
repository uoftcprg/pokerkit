from unittest import TestCase, main

from pokertools import FixedLimitCourchevel, NoLimitCourchevel, PotLimitCourchevel
from pokertools.tests import PokerTestCaseMixin


class FixedLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitCourchevel

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitCourchevel

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitCourchevelTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitCourchevel

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
