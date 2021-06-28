from unittest import TestCase, main

from pokertools import FixedLimitTexasHoldEm, NoLimitTexasHoldEm, PotLimitTexasHoldEm
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = FixedLimitTexasHoldEm

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


class PotLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = PotLimitTexasHoldEm

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


class NoLimitTexasHoldEmTestCase(PokerTestCaseMixin, TestCase):
    GAME_TYPE = NoLimitTexasHoldEm

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
