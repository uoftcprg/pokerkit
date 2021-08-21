from unittest import TestCase, main

from pokerface import (
    FixedLimitFiveCardOmahaHoldEm, PotLimitFiveCardOmahaHoldEm, Stakes,
)
from pokerface.tests import PokerTestCaseMixin


class FixedLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitFiveCardOmahaHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (50000, 100000)), (125945025, 67847350),
        ).act(
            'dh Ah3sKsKh2c', 'dh 6d9s7d8h2d',
            'cc', 'cc',
            'db 4s5c2h',
            'cc', 'cc',
            'db 5h',
            'cc', 'cc',
            'db 9c',
            'cc', 'cc',
            's', 's',
        ), (True, False), (126045025, 67747350))


class PotLimitFiveCardOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitFiveCardOmahaHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (50000, 100000)), (125945025, 67847350),
        ).act(
            'dh Ah3sKsKh2c', 'dh 6d9s7d8h2d',
            'br 300000', 'br 900000', 'br 2700000', 'br 8100000', 'cc',
            'db 4s5c2h',
            'br 9100000', 'br 43500000', 'br 77900000', 'cc',
            'db 5h',
            'db 9c',
        ), (True, True), (193792375, 0))


if __name__ == '__main__':
    main()
