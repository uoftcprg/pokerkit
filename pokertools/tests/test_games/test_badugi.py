from unittest import TestCase, main

from pokertools import FixedLimitBadugi, NoLimitBadugi, PotLimitBadugi
from pokertools.tests import PokerTestCaseMixin


class FixedLimitBadugiTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitBadugi

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitBadugiTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitBadugi

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitBadugiTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitBadugi

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


if __name__ == '__main__':
    main()
