from unittest import TestCase, main

from pokertools import PotLimitSixCardOmahaHoldEm
from pokertools.tests import PokerTestCaseMixin


class PotLimitSixCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitSixCardOmahaHoldEm

    def test_hands(self):
        ...  # TODO


if __name__ == '__main__':
    main()
