from unittest import TestCase, main

from pokertools import FixedLimitTripleDrawLowball27, PotLimitTripleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTripleDrawLowball27

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (75, 150), (1180, 4340, 5910, 10765)).parse(
            'dh 0 7h6c4c3d2c', 'dh 1 JsJcJdJhTs', 'dh 2 KsKcKdKhTh', 'dh 3 AsQs6s5c3c',
            'f', 'br', 'br', 'f', 'cc',
            'dd', 'dd AsQs 2hQh',
            'br', 'cc',
            'dd', 'dd Qh 4d',
            'br', 'cc',
            'dd', 'dd 6s 7c',
            'br', 'cc',
            's', 's',
        ), (True, False, False, True), (0, 4190, 5910, 12095))


class PotLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitTripleDrawLowball27

    def test_hands(self):
        self.assert_terminal_poker_game(self.GAME_TYPE(0, (75, 150), (1180, 4340, 5910, 10765)).parse(
            'dh 0 7h6c4c3d2c', 'dh 1 JsJcJdJhTs', 'dh 2 KsKcKdKhTh', 'dh 3 AsQs6s5c3c',
            'f', 'br 300', 'br 450', 'f', 'cc',
            'dd', 'dd AsQs 2hQh',
            'br 150', 'cc',
            'dd', 'dd Qh 4d',
            'br 300', 'cc',
            'dd', 'dd 6s 7c',
            'br 280', 'cc',
            's', 's',
        ), (True, False, False, True), (0, 4190, 5910, 12095))


if __name__ == '__main__':
    main()