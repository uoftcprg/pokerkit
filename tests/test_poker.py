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


class NoLimitTexasHoldEmSimulationTestCase(PokerTestMixin, ExtendedTestCase):
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
