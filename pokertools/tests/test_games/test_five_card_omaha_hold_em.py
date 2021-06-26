from unittest import TestCase, main

from pokertools import FixedLimitFiveCardOmahaHoldEm, NoLimitFiveCardOmahaHoldEm, PotLimitFiveCardOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitFiveCardOmahaHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitFiveCardOmahaHoldEm

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitFiveCardOmahaHoldEm

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
