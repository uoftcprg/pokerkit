from unittest import TestCase, main

from pokertools import FixedLimitTexasHoldEm, NoLimitTexasHoldEm, PotLimitTexasHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitTexasHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitTexasHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitTexasHoldEm

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
