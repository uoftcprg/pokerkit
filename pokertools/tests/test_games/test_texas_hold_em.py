from unittest import TestCase, main

from pokertools import FixedLimitTexasHoldEm, NoLimitTexasHoldEm, PotLimitTexasHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTexasHoldEm

    def test_hands(self):
        ...


class PotLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitTexasHoldEm

    def test_hands(self):
        ...


class NoLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitTexasHoldEm

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
