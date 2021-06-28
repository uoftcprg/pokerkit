from unittest import TestCase, main

from pokertools import FixedLimitFiveCardDraw, NoLimitFiveCardDraw, PotLimitFiveCardDraw
from pokertools.tests import PokerTestCaseMixin


class FixedLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitFiveCardDraw

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (5, 10), (1000, 1000, 1000, 1000)).parse(
            'dh 0 AsAdAcAhKd', 'dh 1 4s4d4c5h5d', 'dh 2 2s2d2c3h3d', 'dh 3 Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1065, 970, 970))


class PotLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitFiveCardDraw

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (5, 10), (1000, 1000, 1000, 1000)).parse(
            'dh 0 AsAdAcAhKd', 'dh 1 4s4d4c5h5d', 'dh 2 2s2d2c3h3d', 'dh 3 Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br 35', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1095, 955, 955))


class NoLimitFiveCardDrawTestCase(PotLimitFiveCardDrawTestCase, TestCase):
    GAME_TYPE = NoLimitFiveCardDraw

    def test_hands(self):
        super().test_hands()

        self.assert_terminal_poker_game(self.GAME_TYPE(0, (5, 10), (1000, 1000, 1000, 1000)).parse(
            'dh 0 AsAdAcAhKd', 'dh 1 4s4d4c5h5d', 'dh 2 2s2d2c3h3d', 'dh 3 Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br 100', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1225, 890, 890))


if __name__ == '__main__':
    main()
