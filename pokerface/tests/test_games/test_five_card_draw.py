from unittest import TestCase, main

from pokerface import (
    FixedLimitFiveCardDraw, NoLimitFiveCardDraw, PotLimitFiveCardDraw, Stakes,
)
from pokerface.tests import PokerTestCaseMixin


class FixedLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitFiveCardDraw

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (5, 10)), (1000, 1000, 1000, 1000),
        ).act(
            'dh AsAdAcAhKd', 'dh 4s4d4c5h5d', 'dh 2s2d2c3h3d', 'dh Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1065, 970, 970))


class PotLimitFiveCardDrawTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitFiveCardDraw

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (5, 10)), (1000, 1000, 1000, 1000),
        ).act(
            'dh AsAdAcAhKd', 'dh 4s4d4c5h5d', 'dh 2s2d2c3h3d', 'dh Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br 35', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1095, 955, 955))


class NoLimitFiveCardDrawTestCase(PotLimitFiveCardDrawTestCase, TestCase):
    GAME_TYPE = NoLimitFiveCardDraw

    def test_hands(self):
        super().test_hands()

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (5, 10)), (1000, 1000, 1000, 1000),
        ).act(
            'dh AsAdAcAhKd', 'dh 4s4d4c5h5d', 'dh 2s2d2c3h3d', 'dh Th8h9cJsQd',
            'cc', 'cc', 'f', 'cc',
            'dd 4c4d4s 5c5sKc', 'dd 3h3d 2hQs', 'dd',
            'br 100', 'cc', 'cc',
            's', 's', 's',
        ), (False, True, False, False), (995, 1225, 890, 890))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, ()), (100, 100, 100, 100),
        ).act(
            'dh 8cKdJd2h5d', 'dh JsAd3d4d7c', 'dh 2c5sTsQsAs', 'dh AcAh8s9c3s',
            'br 5', 'f', 'cc', 'cc',
            'dd Jd2h5d Jc6s7d', 'dd 2c Ks', 'dd 8s9c3s KhKcTh',
            'cc', 'cc', 'br 10', 'f', 'br 20', 'cc',
            's', 's',
        ), (False, False, True, False), (94, 99, 133, 74))


if __name__ == '__main__':
    main()
