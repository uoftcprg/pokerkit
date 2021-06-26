from unittest import TestCase, main

from pokertools import FixedLimitOmahaHoldEm, NoLimitOmahaHoldEm, PotLimitOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitOmahaHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitOmahaHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitOmahaHoldEm

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
