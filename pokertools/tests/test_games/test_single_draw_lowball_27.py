from unittest import TestCase, main

from pokertools import NoLimitSingleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class NoLimitSingleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitSingleDrawLowball27

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2), (200, 200)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d',
            'br 6', 'br 12', 'br 18', 'br 36', 'br 72', 'cc',
            'dd', 'dd 8d 5c',
            'br 128', 'cc',
        ), (True, True), (0, 400))

        self.assert_terminal_poker_game(self.GAME_TYPE(1, (1, 2), (200, 200, 100)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h',
            'br 6', 'br 18', 'br 54', 'br 99', 'br 199', 'cc',
            'dd', 'dd', 'dd',
        ), (True, True, True), (200, 0, 300))
        self.assert_terminal_poker_game(self.GAME_TYPE(15, (15, 30), (1015, 2530, 1955)).parse(
            'dh 0 AsTc9c6h3s', 'dh 1 9dThJsQsKs', 'dh 2 4s4d4c3h3c',
            'br 100', 'br 300', 'f', 'cc',
            'dd As 5h', 'dd',
            'cc', 'br 700', 'f',
        ), (False, False, None), (700, 2485, 2315))

        self.assert_terminal_poker_game(self.GAME_TYPE(1, (1, 2), (200, 200, 100, 150)).parse(
            'dh 0 2s3h4s6d7d', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsQc',
            'br 6', 'f', 'cc', 'cc',
            'dd 6d 9c', 'dd 8d 8c', 'dd',
            'cc', 'cc', 'br 30', 'cc', 'cc',
            's', 's', 's',
        ), (False, False, True, False), (163, 163, 175, 149))
        self.assert_terminal_poker_game(self.GAME_TYPE(8750, (10000, 25000), (1180000, 1065000, 870000, 2345000)).parse(
            'dh 0 As6h6d2h2d', 'dh 1 KhTs6c5d4c', 'dh 2 AhKsQhJhTh', 'dh 3 AdKcQcJcTc',
            'f', 'f', 'br 100000', 'cc',
            'dd', 'dd Kh 4h',
            'br 150000', 'cc',
            's', 's',
        ), (True, True, False, False), (921250, 1341250, 861250, 2336250))

        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2, 4), (50, 2, 100, 150, 100, 100)).parse(
            'dh 0 AcAdAhAsJc', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsJd', 'dh 4 QcQdQhQsJh',
            'dh 5 7s8c9cTcJs',
            'f', 'f', 'f', 'f',
            'dd 8d 6s', 'dd',
        ), (False, True, True, False, False, False), (49, 0, 103, 150, 100, 100))

        self.assert_terminal_poker_game(self.GAME_TYPE(0, (1, 2, 4), (50, 2, 100, 150, 100, 100, 1, 1, 1)).parse(
            'dh 0 AcAdAhAsJc', 'dh 1 2h3c4d7c8d', 'dh 2 2d3d4c5d7h', 'dh 3 KcKdKhKsJd', 'dh 4 QcQdQhQsJh',
            'dh 5 7s8c9cTcJs', 'dh 6', 'dh 7', 'dh 8',
            'f', 'f', 'f', 'f', 'f', 'f', 'f',
            'dd', 'dd',
        ), (False, True, True, False, False, False, False, False, False), (49, 0, 103, 150, 100, 100, 1, 1, 1))


if __name__ == '__main__':
    main()
