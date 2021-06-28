from unittest import TestCase, main

from pokertools import FixedLimitSixCardOmahaHoldEm, NoLimitSixCardOmahaHoldEm, PotLimitSixCardOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitSixCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitSixCardOmahaHoldEm

    def test_hands(self):
        ...


class PotLimitSixCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitSixCardOmahaHoldEm

    def test_hands(self):
        ...


class NoLimitSixCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitSixCardOmahaHoldEm

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
