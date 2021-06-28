from unittest import TestCase, main

from pokertools import KuhnPoker
from pokertools.tests import PokerTestCaseMixin


class KuhnPokerTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = KuhnPoker

    def test_heads_up(self):
        self.assert_terminal_poker_game(self.GAME_TYPE().parse(
            'dh 0 Qs', 'dh 1 Ks', 'cc', 'cc', 's', 's',
        ), (True, True), (1, 3))
        self.assert_terminal_poker_game(self.GAME_TYPE().parse(
            'dh 0', 'dh 1', 'cc', 'br', 'f',
        ), (False, None), (1, 3))
        self.assert_terminal_poker_game(self.GAME_TYPE().parse(
            'dh 0 Ks', 'dh 1 Js', 'cc', 'br', 'cc', 's', 's',
        ), (True, True), (4, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE().parse(
            'dh 0', 'dh 1', 'br', 'f',
        ), (None, False), (3, 1))
        self.assert_terminal_poker_game(self.GAME_TYPE().parse(
            'dh 0 Ks', 'dh 1 Qs', 'br', 'cc', 's', 's',
        ), (True, False), (4, 0))

    def test_3_max(self): ...

    def test_4_max(self): ...

    def test_6_max(self): ...

    def test_9_max(self): ...

    def create_game(self):
        return self.GAME_TYPE()


if __name__ == '__main__':
    main()
