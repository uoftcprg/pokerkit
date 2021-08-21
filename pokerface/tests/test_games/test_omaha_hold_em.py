from unittest import TestCase, main

from pokerface import PotLimitOmahaHoldEm, Stakes
from pokerface.tests import PokerTestCaseMixin


class PotLimitOmahaHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitOmahaHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (50000, 100000)), (125945025, 67847350),
        ).act(
            'dh Ah3sKsKh', 'dh 6d9s7d8h',
            'br 300000', 'br 900000', 'br 2700000', 'br 8100000', 'cc',
            'db 4s5c2h',
            'br 9100000', 'br 43500000', 'br 77900000', 'cc',
            'db 5h',
            'db 9c',
        ), (True, True), (193792375, 0))


if __name__ == '__main__':
    main()
