from unittest import TestCase, main

from pokerface import KuhnPoker
from pokerface.tests import PokerTestCaseMixin


class KuhnPokerTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = KuhnPoker

    @property
    def game_name(self):
        return 'KuhnPoker'

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE().act(
            'dh Qs', 'dh Ks',
            'cc', 'cc', 's', 's',
        ), (True, True), (1, 3))
        self.assert_terminal_poker_game(self.GAME_TYPE().act(
            'dh', 'dh',
            'cc', 'br', 'f',
        ), (False, None), (1, 3))
        self.assert_terminal_poker_game(self.GAME_TYPE().act(
            'dh Ks', 'dh Js',
            'cc', 'br', 'cc',
        ), (True, True), (4, 0))
        self.assert_terminal_poker_game(self.GAME_TYPE().act(
            'dh', 'dh',
            'br', 'f',
        ), (None, False), (3, 1))
        self.assert_terminal_poker_game(self.GAME_TYPE().act(
            'dh Ks', 'dh Qs',
            'br', 'cc',
        ), (True, True), (4, 0))

    def create_game(self):
        return self.GAME_TYPE()


if __name__ == '__main__':
    main()
