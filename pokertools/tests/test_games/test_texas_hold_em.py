from unittest import TestCase, main

from pokertools import FixedLimitTexasHoldEm, NoLimitTexasHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTexasHoldEm

    def test_hands(self):
        ...


class NoLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitTexasHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(500, (1000, 2000), (1125600, 2000000, 553500)).parse(
            'dh 0 Ac2d', 'dh 1 5h7s', 'dh 2 7h6h',
            'br 7000', 'br 23000', 'f', 'cc',
            'db Jc3d5c',
            'br 35000', 'cc',
            'db 4h',
            'br 90000', 'br 232600', 'br 1067100', 'cc',
            'db Jh',
            's', 's',
        ), (True, False, True), (572100, 1997500, 1109500))


if __name__ == '__main__':
    main()
