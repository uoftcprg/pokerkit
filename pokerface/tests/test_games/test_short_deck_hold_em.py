from unittest import TestCase, main

from pokerface import NoLimitShortDeckHoldEm, Stakes
from pokerface.tests import PokerTestCaseMixin


class NoLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitShortDeckHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(Stakes(3, {-1: 3}), (
            495, 232, 362, 403, 301, 204,
        )).act(
            'dh Th8h', 'dh QsJd', 'dh QhQd', 'dh 8d7c', 'dh KhKs', 'dh 8c7h',
            'cc', 'cc', 'br 35', 'f', 'br 298', 'f', 'f', 'f', 'cc',
            'db 9h6cKc',
            'db Jh',
            'db Ts',
        ), (False, False, True, False, True, False), (
            489, 226, 684, 400, 0, 198,
        ))


if __name__ == '__main__':
    main()
