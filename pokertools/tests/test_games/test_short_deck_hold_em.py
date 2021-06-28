from unittest import TestCase, main

from pokertools import NoLimitShortDeckHoldEm
from pokertools.tests import PokerTestCaseMixin


class NoLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitShortDeckHoldEm

    def test_hands(self):
        ...


if __name__ == '__main__':
    main()
