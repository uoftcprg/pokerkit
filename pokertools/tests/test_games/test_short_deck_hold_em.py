from unittest import TestCase, main

from pokertools import FixedLimitShortDeckHoldEm, NoLimitShortDeckHoldEm, PotLimitShortDeckHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitShortDeckHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitShortDeckHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitShortDeckHoldEm

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
