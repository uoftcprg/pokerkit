from unittest import TestCase, main

from pokertools import FixedLimitTripleDrawLowball27, NoLimitTripleDrawLowball27, PotLimitTripleDrawLowball27
from pokertools.tests import PokerTestCaseMixin


class FixedLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = FixedLimitTripleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class PotLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = PotLimitTripleDrawLowball27

    def test_heads_up(self):
        ...

    def test_3_max(self):
        ...

    def test_6_max(self):
        ...

    def test_9_max(self):
        ...


class NoLimitTripleDrawLowball27TestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = NoLimitTripleDrawLowball27

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
