from unittest import TestCase, main

from pokertools import KuhnPoker
from pokertools.tests import PokerTestCaseMixin


class FixedLimitKuhnPokerTestCase(PokerTestCaseMixin, TestCase):
    POKER_GAME_TYPE = KuhnPoker

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
