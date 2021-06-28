from unittest import TestCase, main

from pokertools import FixedLimitOmahaHoldEm, NoLimitOmahaHoldEm, PotLimitOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitOmahaHoldEm

    def test_hands(self):
        ...


class PotLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitOmahaHoldEm

    def test_hands(self):
        ...


class NoLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitOmahaHoldEm

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
