from unittest import TestCase, main

from pokerface import PotLimitSixCardOmahaHoldEm, Stakes
from pokerface.tests import PokerTestCaseMixin


class PotLimitSixCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitSixCardOmahaHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (200, 200),
        ).act(
            'dh AcKcQcJcTc2c', 'dh AsKsQsJsTs2s',
            'br 6', 'br 18', 'cc',
            'db 9s8s7s',
            'cc', 'cc',
            'db 6s',
            'br 30', 'cc',
            'db 6c',
            'cc', 'br 50', 'cc',
            's 1', 's',
        ), (False, True), (102, 298))

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2, 4, 8)), (500,) * 6,
        ).act(
            'dh', 'dh', 'dh', 'dh', 'dh', 'dh',
            'br 25', 'f', 'f', 'cc', 'cc', 'cc',
            'db',
            'cc', 'cc', 'cc', 'br 80', 'cc', 'cc', 'f',
            'db',
            'br 225', 'cc', 'f',
            'db',
            'cc', 'br 170', 'f',
        ), (False, False, None, False, False, False), (
            499, 170, 961, 475, 395, 500,
        ))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2, 0, 2)), (200,) * 6,
        ).act(
            'dh', 'dh', 'dh', 'dh', 'dh', 'dh',
            'br 9', 'f', 'f', 'br 25', 'cc', 'cc', 'cc',
            'db',
            'cc', 'cc', 'cc', 'br 75', 'cc', 'cc', 'f',
            'db',
            'br 100', 'f', 'f',
        ), (None, False, False, False, False, False), (
            427, 100, 175, 198, 200, 100,
        ))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2, 2, 0, 2)), (200,) * 6,
        ).act(
            'dh', 'dh', 'dh', 'dh', 'dh', 'dh',
            'cc', 'cc', 'cc', 'br 9', 'br 25', 'f', 'f', 'cc', 'cc', 'cc',
            'db',
            'cc', 'cc', 'cc', 'br 75', 'cc', 'cc', 'f',
            'db',
            'br 100', 'f', 'f',
        ), (None, False, False, False, False, False), (
            429, 198, 198, 100, 175, 100,
        ))


if __name__ == '__main__':
    main()
