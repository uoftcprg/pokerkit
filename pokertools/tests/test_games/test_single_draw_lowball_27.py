from unittest import TestCase, main

from pokertools import FixedLimitSingleDrawLowball27, NoLimitSingleDrawLowball27, PotLimitSingleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class FixedLimitSingleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitSingleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitSingleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitSingleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitSingleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitSingleDrawLowball27

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
