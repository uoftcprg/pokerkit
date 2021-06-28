from unittest import TestCase, main

from pokertools import FixedLimitGreekHoldEm, NoLimitGreekHoldEm, PotLimitGreekHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitGreekHoldEm

    def test_hands(self):
        ...  # TODO


class PotLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitGreekHoldEm

    def test_hands(self):
        ...  # TODO


class NoLimitGreekHoldEmTestCase(PotLimitGreekHoldEmTestCase, TestCase):
    GAME_TYPE = NoLimitGreekHoldEm

    def test_hands(self):
        super().test_hands()  # TODO


if __name__ == '__main__':
    main()
