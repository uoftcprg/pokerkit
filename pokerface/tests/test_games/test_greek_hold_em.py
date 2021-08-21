from unittest import TestCase, main

from pokerface import (
    FixedLimitGreekHoldEm, NoLimitGreekHoldEm, PotLimitGreekHoldEm, Stakes,
)
from pokerface.tests import PokerTestCaseMixin


class FixedLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitGreekHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 5), small_bet=10), (100, 100),
        ).act(
            'dh AhAc', 'dh AsKs',
            'br', 'cc',
            'db KcQdJh',
            'br', 'cc',
            'db Tc',
            'br', 'cc',
            'db 9d',
            'cc', 'cc',
            's', 's',
        ), (True, True), (54, 146))


class PotLimitGreekHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitGreekHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 5), small_bet=10), (100, 100),
        ).act(
            'dh AhAc', 'dh AsKs',
            'br', 'cc',
            'db KcQdJh',
            'br', 'cc',
            'db Tc',
            'br', 'cc',
            'db 9d',
            'cc', 'cc',
            's', 's',
        ), (True, True), (64, 136))


class NoLimitGreekHoldEmTestCase(PotLimitGreekHoldEmTestCase, TestCase):
    GAME_TYPE = NoLimitGreekHoldEm

    def test_hands(self):
        super().test_hands()

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 5)), (100, 100),
        ).act(
            'dh AhAc', 'dh AsKs',
            'br', 'cc',
            'db KcQdJh',
            'br', 'cc',
            'db Tc',
            'br', 'cc',
            'db 9d',
            'cc', 'cc',
            's', 's',
        ), (True, True), (79, 121))


if __name__ == '__main__':
    main()
