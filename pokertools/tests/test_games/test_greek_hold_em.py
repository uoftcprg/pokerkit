from unittest import TestCase, main

from pokertools import FixedLimitGreekHoldEm, NoLimitGreekHoldEm, PotLimitGreekHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitGreekHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitGreekHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitGreekHoldEm

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
