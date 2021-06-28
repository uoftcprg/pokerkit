from unittest import TestCase, main

from pokertools import NoLimitSingleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class NoLimitSingleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitSingleDrawLowball27

    def test_heads_up(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2), (200, 200)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d',
            'br 6', 'br 12', 'br 18', 'br 36', 'br 72', 'cc',
            'dd', 'dd 8d 5c',
            'br 128', 'cc',
            's', 's',
        ), (True, True), (0, 400))

    def test_3_max(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(1, (1, 2), (200, 200, 100)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h',
            'br 6', 'br 18', 'br 54', 'br 99', 'br 199', 'cc',
            'dd', 'dd', 'dd',
            's', 's', 's',
        ), (True, False, True), (200, 0, 300))

    def test_4_max(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(1, (1, 2), (200, 200, 100, 150)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsQc',
            'br 6', 'f', 'cc', 'cc',
            'dd 6d 9c', 'dd 8d 8c', 'dd',
            'cc', 'cc', 'br 30', 'cc', 'cc',
            's', 's', 's',
        ), (False, False, True, False), (163, 163, 175, 149))

    def test_6_max(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2, 4), (50, 2, 100, 150, 100, 100)).parse(
            'dh 0 AcAdAhAsJc', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsJd', 'dh 4 QcQdQhQsJh',
            'dh 5 7s8c9cTcJs',
            'f', 'f', 'f', 'f',
            'dd 8d 6s', 'dd',
            's', 's',
        ), (False, False, True, False, False, False), (49, 0, 103, 150, 100, 100))

    def test_9_max(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2, 4), (50, 2, 100, 150, 100, 100, 1, 1, 1)).parse(
            'dh 0 AcAdAhAsJc', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsJd', 'dh 4 QcQdQhQsJh',
            'dh 5 7s8c9cTcJs', 'dh 6', 'dh 7', 'dh 8',
            'f', 'f', 'f', 'f', 'f', 'f', 'f',
            'dd', 'dd',
            's', 's',
        ), (False, False, True, False, False, False, False, False, False), (49, 0, 103, 150, 100, 100, 1, 1, 1))


if __name__ == '__main__':
    main()
