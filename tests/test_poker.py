from abc import ABC
from itertools import repeat
from random import choice, randint, sample
from typing import cast
from unittest import TestCase, main

from auxiliary import ExtendedTestCase
from pokertools import parse_cards

from gameframe.exceptions import GameFrameError
from gameframe.poker import (
    FixedLimitBadugi, FixedLimitGreekHoldEm, KuhnPoker, NoLimitFiveCardDraw, NoLimitShortDeckHoldEm, NoLimitTexasHoldEm,
    Poker, PokerNature, PokerPlayer, PotLimitOmahaHoldEm, parse_poker,
)
from gameframe.tests import GameFrameTestCaseMixin


class HeadsUpNoLimitTexasHoldEmSimulationTestCase(PokerTestMixin, ExtendedTestCase):
    def test_low_stacks(self) -> None:
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (0, 0)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (1, 0)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (0, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (2, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (50, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))

    def create_game(self) -> NoLimitTexasHoldEm:
        return NoLimitTexasHoldEm(2, (1, 2), (randint(0, 50), randint(0, 50)))


class NoLimitTexasHoldEmSimulationTestCase(PokerTestMixin, ExtendedTestCase):
    def test_low_stacks(self) -> None:
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (0, 0, 0, 0)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'db', 'db', 'db', 's', 's', 's', 's',
        )))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (1, 17, 0, 1)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'db', 'db', 'db', 's', 's', 's', 's',
        )))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (2, 16, 0, 1)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'db', 'db', 'db', 's', 's', 's', 's',
        )))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (2, 16, 0, 1)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'db', 'db', 'db', 's', 's', 's', 's',
        )))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (1, 1, 5, 5)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'br 4', 'cc', 'db', 'db', 'db', 's', 's', 's', 's',
        )))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (7, 0, 9, 7)), (
            'dh 0', 'dh 1', 'dh 2', 'dh 3', 'f', 'f', 'db', 'db', 'db', 's', 's',
        )))

    def test_min_bet_raise(self) -> None:
        game = parse_poker(NoLimitTexasHoldEm(0, (5, 10), (1000, 1000)), ('dh 0', 'dh 1'))
        self.assertEqual(cast(PokerPlayer, game.actor).min_bet_raise_amount, 20)
        parse_poker(game, ('cc', 'cc', 'db'))
        self.assertEqual(cast(PokerPlayer, game.actor).min_bet_raise_amount, 10)
        parse_poker(game, ('cc', 'cc', 'db'))
        self.assertEqual(cast(PokerPlayer, game.actor).min_bet_raise_amount, 10)
        parse_poker(game, ('cc', 'cc', 'db'))
        self.assertEqual(cast(PokerPlayer, game.actor).min_bet_raise_amount, 10)

    def test_cans(self) -> None:
        game = NoLimitTexasHoldEm(1, (1, 2), (100, 100, 100))
        commands = (
            'dh 0 AhTh', 'dh 1 AsTs', 'dh 2 AcTc', 'br 6', 'f', 'cc',
            'db 2h3h4h', 'cc', 'cc',
            'db 4s', 'br 93', 'cc',
            'db 5s', 's 1', 's 1',
        )

        for command in commands:
            parse_poker(game, (command,))
            self.verify(game)
