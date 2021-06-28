from unittest import TestCase, main

from pokertools import FixedLimitFiveCardOmahaHoldEm, NoLimitFiveCardOmahaHoldEm, PotLimitFiveCardOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitFiveCardOmahaHoldEm

    def test_hands(self):
        ...


class PotLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitFiveCardOmahaHoldEm

    def test_hands(self):
        ...


class NoLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitFiveCardOmahaHoldEm

    def test_hands(self):
        super().test_hands()


if __name__ == '__main__':
    main()
