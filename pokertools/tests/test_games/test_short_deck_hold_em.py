from unittest import TestCase, main

from pokertools import NoLimitShortDeckHoldEm
from pokertools.tests import PokerTestCaseMixin


class NoLimitShortDeckHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitShortDeckHoldEm

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(3, {5: 3}, (495, 232, 362, 403, 301, 204)).parse(
            'dh 0 Th8h', 'dh 1 QsJd', 'dh 2 QhQd', 'dh 3 8d7c', 'dh 4 KhKs', 'dh 5 8c7h',
            'cc', 'cc', 'br 35', 'f', 'br 298', 'f', 'f', 'f', 'cc',
            'db 9h6cKc',
            'db Jh',
            'db Ts',
        ), (False, False, True, False, True, False), (489, 226, 684, 400, 0, 198))


if __name__ == '__main__':
    main()
