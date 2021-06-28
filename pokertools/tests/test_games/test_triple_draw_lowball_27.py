from unittest import TestCase, main

from pokertools import FixedLimitTripleDrawLowball27, NoLimitTripleDrawLowball27, PotLimitTripleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTripleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_4_max(self):
        self.assert_terminal_poker_game(FixedLimitTripleDrawLowball27(0, (75, 150), (1180, 4340, 5910, 10765)).parse(
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

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitTripleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_4_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitTripleDrawLowball27

    def test_heads_up(self):
        super().test_heads_up()

    def test_3_max(self):
        super().test_3_max()

    def test_4_max(self):
        super().test_4_max()

    def test_6_max(self):
        super().test_6_max()

    def test_9_max(self):
        super().test_9_max()


if __name__ == '__main__':
    main()
