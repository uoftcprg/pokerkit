from unittest import TestCase, main

from pokertools import FixedLimitTexasHoldEm, NoLimitTexasHoldEm, Stakes
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTexasHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (2, 4), 5, 10), (100, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'br', 'cc',
            'db Qc',
            'cc', 'cc',
            's', 's',
        ), (True, True), (80, 120))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (2, 4), 5, 10), (100, 100)).parse(
            'dh 0 AhAd', 'dh 1 QdQh',
            'br', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
            's', 's',
        ), (True, False), (110, 90))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (2, 4), 5, 10), (100, 100)).parse(
            'dh 0 AhAd', 'dh 1 QdQh',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'br', 'cc',
            'db Qc',
            'cc', 'cc',
            's', 's 1',
        ), (True, True), (115, 85))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (2, 4), 5, 10), (100, 100)).parse(
            'dh 0 AhAd', 'dh 1 QdQh',
            'br', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
            's 0',
        ), (False, None), (90, 110))


class NoLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitTexasHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'br 199', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (100, 200))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 99', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (100, 200))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
            's', 's',
        ), (True, True), (193, 107))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
            's', 's',
        ), (True, True), (197, 103))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 4', 'cc',
            'db AcAsKc',
            'br 6', 'f',
        ), (None, False), (205, 95))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (0, 0)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (0, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (1, 0)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (1, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (0, 1)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (0, 1))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (2, 1)).parse(
            'dh 0 QdQh',
            'dh 1 AhAd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (1, 2))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (50, 1)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True), (49, 2))

        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(500, (1000, 2000)), (1125600, 2000000, 553500)).parse(
            'dh 0 Ac2d', 'dh 1 5h7s', 'dh 2 7h6h',
            'br 7000', 'br 23000', 'f', 'cc',
            'db Jc3d5c',
            'br 35000', 'cc',
            'db 4h',
            'br 90000', 'br 232600', 'br 1067100', 'cc',
            'db Jh',
        ), (True, False, True), (572100, 1997500, 1109500))

        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 299', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, True, True), (300, 400, 100, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'br 6', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc',
            's', 's', 's',
        ), (True, True, False, False), (193, 115, 299, 193))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'br 6', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'br 10', 'br 20', 'cc', 'f',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 50', 'cc',
            's', 's',
        ), (False, True, False, False), (123, 195, 299, 183))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 6', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'br 10', 'br 20', 'cc', 'br 93', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc',
            's', 's', 's', 's',
        ), (True, True, False, False), (100, 400, 200, 100))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 6', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'br 10', 'br 20', 'cc', 'br 93', 'cc', 'cc', 'cc',
            'db Qs',
            'br 50', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc',
            's', 's', 's', 's',
        ), (True, True, False, False), (200, 400, 150, 50))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'br 199', 'cc', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, False, True), (200, 301, 299, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (100,) * 4).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 99', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, True, True), (0, 400, 0, 0))

        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200, 200, 150)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'dh 4 JcJh', 'dh 5 TsTh',
            'cc', 'cc', 'cc', 'br 149', 'cc', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
            's', 's', 's', 's', 's', 's',
        ), (True, True, False, False, False, False), (300, 600, 150, 50, 50, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200, 200, 150)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'dh 4 JcJh', 'dh 5 TsTh',
            'br 50', 'f', 'f', 'f', 'f', 'f',
        ), (False, False, None, False, False, False), (198, 97, 308, 199, 199, 149))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (200, 100, 300, 200, 200, 150)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'dh 4 TsTh', 'dh 5 JcTc',
            'br 50', 'br 199', 'cc', 'cc', 'cc', 'cc', 'f',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, False, True, True, True), (150, 0, 249, 0, 0, 751))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (0, 0, 0, 0)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, True, True), (0, 0, 0, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (1, 1, 5, 5)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 4', 'cc',
            'db AcAsKc',
            'db Qs',
            'db Qc',
        ), (True, True, True, True), (0, 4, 8, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (7, 0, 9, 7)).parse(
            'dh 0 4h8s', 'dh 1 AsQs', 'dh 2 Ac8d', 'dh 3 AhQh',
            'f', 'f',
            'db Ad3s2h',
            'db 8h',
            'db Ts',
        ), (True, True, False, False), (9, 0, 8, 6))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (1, 17, 0, 1)).parse(
            'dh 0 3d6c', 'dh 1 8sAh', 'dh 2 Ad8c', 'dh 3 KcQs',
            'db 4c7h5s',
            'db Ts',
            'db 3c',
        ), (True, True, True, True), (3, 16, 0, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(1, (1, 2)), (2, 16, 0, 1)).parse(
            'dh 0 AcKs', 'dh 1 8h2c', 'dh 2 6h6c', 'dh 3 2dTd',
            'db 8d5c4d',
            'db Qh',
            'db 5d',
        ), (True, True, True, True), (0, 16, 0, 3))


if __name__ == '__main__':
    main()
