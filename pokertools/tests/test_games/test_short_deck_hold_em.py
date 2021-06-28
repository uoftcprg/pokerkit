from unittest import TestCase, main

from pokertools import FixedLimitShortDeckHoldEm, NoLimitShortDeckHoldEm, PotLimitShortDeckHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitShortDeckHoldEm

    def test_hands(self):
        ...


class PotLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitShortDeckHoldEm

    def test_hands(self):
        ...


class NoLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitShortDeckHoldEm

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
