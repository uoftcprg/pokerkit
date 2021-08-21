from unittest import TestCase, main

from pokerface import FixedLimitBadugi, Stakes
from pokerface.tests import PokerTestCaseMixin


class FixedLimitBadugiTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitBadugi

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (1, 2)), (100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d',
            'br', 'f',
        ), (False, None), (97, 103))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (50, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d',
            'cc', 'cc',
            'dd KhQs Ac2c', 'dd 8d9d 8h9h',
            'br', 'br', 'f',
        ), (False, None), (46, 104))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (100, 50),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d',
            'cc', 'cc',
            'dd KhQs Ac2c', 'dd 8d9d 8h9h',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'f',
        ), (None, False), (114, 36))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (100, 50),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d',
            'cc', 'cc',
            'dd KhQs Ac2c', 'dd 8d9d 8h9h',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'f',
        ), (None, False), (118, 32))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d',
            'cc', 'cc',
            'dd KhQs Ac2c', 'dd 8d9d 8h9h',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'cc',
            'dd', 'dd',
            'cc', 'cc',
            's', 's',
        ), (True, True), (82, 118))

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (1, 2, 4)), (100, 100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h',
            'f', 'f',
        ), (False, False, None), (98, 97, 105))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (50, 100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h',
            'cc', 'f', 'cc',
            'dd 8d9d 8h9h', 'dd Kc Ac',
            'br', 'br', 'f',
        ), (False, False, None), (49, 96, 105))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 4)), (50, 100, 50),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h',
            'br', 'f', 'cc',
            'dd 8d9d 8h9h', 'dd Kc Ac',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'br', 'f',
        ), (False, False, None), (47, 59, 94))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 4)), (50, 100, 50),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h',
            'br', 'f', 'cc',
            'dd', 'dd',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'br', 'cc',
            'dd 8d9d 8h9h', 'dd Kc Ac',
            'br', 'f',
        ), (False, None, False), (47, 152, 1))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 4)), (50, 100, 50),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h',
            'br', 'f', 'cc',
            'dd', 'dd',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'br', 'cc',
            'dd 8d9d 8h9h', 'dd Kc Ac',
            'br', 'cc',
        ), (False, True, True), (47, 50, 103))

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (1, 2, 4)), (100, 100, 100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h', 'dh 2s4c6dJc',
            'f', 'f', 'f',
        ), (False, False, None, False), (98, 97, 106, 99))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (50, 100, 100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h', 'dh 2s4c6dJc',
            'f', 'f', 'cc', 'cc',
            'dd KhQs As2h', 'dd',
            'br', 'f',
        ), (None, False, False, False), (52, 98, 100, 100))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 4)), (50, 100, 50, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h', 'dh 2s4c6dJc',
            'br', 'cc', 'f', 'f',
            'dd', 'dd',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'br', 'f',
        ), (False, False, False, None), (47, 95, 9, 149))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (2, 4)), (50, 100, 50, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h', 'dh 2s4c6dJc',
            'br', 'cc', 'f', 'f',
            'dd', 'dd',
            'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'f',
        ), (False, False, None, False), (47, 95, 107, 51))
        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(0, (1, 2)), (100, 100, 100, 100),
        ).act(
            'dh KhQs9cTs', 'dh 4s5d8d9d', 'dh KcTc8s3h', 'dh 2s4c6dJc',
            'f', 'cc', 'cc', 'cc',
            'dd Kh9c Qh7s', 'dd 8d9d 7c8h', 'dd Jc Th',
            'cc', 'br', 'cc', 'cc',
            'dd Qs Js', 'dd', 'dd Th 9h',
            'cc', 'br', 'br', 'f', 'cc',
            'dd 4s 3s', 'dd',
            'cc', 'br', 'cc',
            's', 's',
        ), (False, True, False, True), (96, 120, 100, 84))

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (1, 2, 4, 8, 16)), (100, 50, 100, 50, 100, 50),
        ).act(
            'dh', 'dh', 'dh', 'dh', 'dh', 'dh',
            'f', 'f', 'cc', 'cc', 'cc', 'cc',
            'dd', 'dd', 'dd', 'dd',
            'cc', 'br', 'cc', 'f', 'f',
            'dd', 'dd',
            'br', 'f',
        ), (False, False, None, False, False, False), (
            98, 33, 170, 17, 83, 49,
        ))

        self.assert_terminal_poker_game(self.GAME_TYPE(
            Stakes(1, (1, 2)), (50, 50, 50, 50, 50, 50, 50, 50, 50),
        ).act(
            'dh', 'dh', 'dh', 'dh', 'dh', 'dh', 'dh', 'dh', 'dh',
            'f', 'f', 'f', 'br', 'cc', 'f', 'f', 'f', 'cc',
            'dd', 'dd', 'dd',
            'cc', 'br', 'cc', 'f',
            'dd', 'dd',
            'cc', 'br', 'br', 'cc',
            'dd', 'dd',
            'br', 'br', 'br', 'f',
        ), (False, False, False, False, False, None, False, False, False), (
            48, 45, 49, 49, 49, 85, 27, 49, 49,
        ))


if __name__ == '__main__':
    main()
