from unittest import TestCase, main

from pokertools import PotLimitOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class PotLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitOmahaHoldEm

    def test_hands(self):
        ...


if __name__ == '__main__':
    main()
