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


class PokerTestMixin(GameFrameTestCaseMixin[Poker], ABC):
    def act(self, game: Poker) -> None:
        if isinstance(game.actor, PokerNature):
            if game.actor.can_deal_hole():
                for player in game.players:
                    game.nature.deal_hole(player, sample(game.deck, game.actor.hole_deal_count))
            elif game.actor.can_deal_board():
                game.nature.deal_board(sample(game.deck, game.actor.board_deal_count))
            else:
                raise AssertionError('Poker Nature cannot act')
        elif isinstance(game.actor, PokerPlayer):
            actions = []

            if game.actor.can_fold():
                actions.append('f')
            if game.actor.can_check_call():
                actions.append('cc')
            if game.actor.can_bet_raise():
                actions.extend((f'br {game.actor.min_bet_raise_amount}', f'br {game.actor.max_bet_raise_amount}'))
            if game.actor.can_discard_draw():
                cards = ''.join(map(repr, sample(game.actor.hole, randint(0, len(game.actor.hole)))))
                actions.append(f'dd {cards}')
            if game.actor.can_showdown():
                actions.append('s')

            parse_poker(game, (choice(actions),))
        else:
            raise AssertionError('Unknown player type')

    def verify(self, game: Poker) -> None:
        self.verify_nature(game)

        for player in game.players:
            self.verify_player(player, game)

        assert sum(player.bet + player.stack for player in game.players) + game.pot \
               == sum(player.starting_stack for player in game.players)
        assert sum(game.side_pots) == game.pot, str(list(game.side_pots)) + ' ' + str(game.pot)

        if game.terminal:
            assert game.pot == 0

    @staticmethod
    def verify_nature(game: Poker) -> None:
        if game.nature.can_deal_hole():
            for player in game.players:
                if game.nature.can_deal_hole(player):
                    assert game.nature.can_deal_hole(player, sample(game.deck, game.nature.hole_deal_count))
                    assert not game.nature.can_deal_hole(player, sample(game.deck, game.nature.hole_deal_count + 1))

        if game.nature.can_deal_board():
            assert game.nature.can_deal_board(sample(game.deck, game.nature.board_deal_count))
            assert not game.nature.can_deal_board(sample(game.deck, game.nature.board_deal_count + 1))

    @staticmethod
    def verify_player(player: PokerPlayer, game: Poker) -> None:
        if player.can_fold():
            assert player.bet < max(player.bet for player in game.players)

        if player.can_bet_raise():
            assert player.can_bet_raise(player.min_bet_raise_amount)
            assert player.can_bet_raise(player.max_bet_raise_amount)
            assert not player.can_bet_raise(player.min_bet_raise_amount - 1)
            assert not player.can_bet_raise(player.max_bet_raise_amount + 1)

        if player.can_discard_draw():
            assert player.can_discard_draw(player.hole)
            assert not game.deck or not player.can_discard_draw(game.deck)
            assert player.can_discard_draw(player.hole, sample(game.deck, len(player.hole)))
            assert not player.hole or not player.can_discard_draw(player.hole, player.hole)
        else:
            assert not player.can_discard_draw(player.hole)
            assert not player.can_discard_draw(player.hole, sample(game.deck, len(player.hole)))

        if player.can_showdown():
            assert player.can_showdown(False)
            assert player.can_showdown(True)
        else:
            assert not player.can_showdown(False)
            assert not player.can_showdown(True)


class HeadsUpNoLimitTexasHoldEmSimulationTestCase(PokerTestMixin, ExtendedTestCase):
    MONTE_CARLO_TEST_COUNT = 500
    SPEED_TEST_TIME = 1

    def test_illegal_actions(self) -> None:
        # Betting actions applied not on a betting stage.
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 2', 'cc',
        )), ('f',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'cc',
        )), ('cc',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 2', 'br 4', 'cc'
        )), ('br 100',))
        # Making redundant folds.
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc',
        )), ('f',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc',
        )), ('f',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs',
        )), ('f',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc',
        )), ('f',))
        # Bet/raising when the player's stack is already covered by another bet.
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'br 199',
        )), ('br 100',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'br 50', 'br 193',
        )), ('br 93',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'br 195',
        )), ('br 95',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'br 93',
        )), ('br 93',))
        # Making bet/raises that are meaningless (e.g. other players are all in).
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 99',
        )), ('br 197',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'br 93',
        )), ('br 193',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'br 95',
        )), ('br 195',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 93',
        )), ('br 193',))
        # Making bet/raises with invalid amounts (too low or too high).
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6',
        )), ('br 9',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6',
        )), ('br 1000',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'br 12', 'br 24',
        )), ('br 30',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'br 4', 'cc',
            'db Qs', 'br 4', 'br 8',
        )), ('br 10',))
        self.assertRaises(GameFrameError, parse_poker, parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc',
        )), ('br 1',))

    def test_showdown_order(self) -> None:
        # Showdown is begun by the past aggressor or, if they don't exist, the first player.
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'br 99', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 99', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[1])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'cc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'cc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'br 4', 'cc',
            'db Qc', 'cc', 'cc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 6', 'br 12', 'cc',
        ))).actor, game.players[0])

    def test_low_stacks(self) -> None:
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (0, 0)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (1, 0)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (0, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (2, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))
        self.verify(parse_poker(NoLimitTexasHoldEm(1, (1, 2), (50, 1)), ('dh 0', 'dh 1', 'db', 'db', 'db', 's', 's')))

    def create_game(self) -> NoLimitTexasHoldEm:
        return NoLimitTexasHoldEm(2, (1, 2), (randint(0, 50), randint(0, 50)))


class NoLimitTexasHoldEmSimulationTestCase(PokerTestMixin, ExtendedTestCase):
    MONTE_CARLO_TEST_COUNT = 500
    SPEED_TEST_TIME = 1

    def test_illegal_actions(self) -> None:
        # Betting actions applied not on a betting stage.
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'cc', 'cc', 'cc', 'cc',
                'db Qc', 'cc', 'cc', 'cc', 'br 2', 'cc', 'cc', 'cc',
            )),
            ('f',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'cc', 'cc', 'cc', 'cc',
                'db Qc', 'cc', 'cc', 'cc', 'cc',
            )),
            ('cc',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'cc', 'cc', 'cc', 'cc',
                'db Qc', 'cc', 'cc', 'cc', 'br 2', 'br 4', 'br 6', 'cc', 'cc', 'cc',
            )),
            ('br 8',),
        )
        # Making redundant folds.
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc',
            )),
            ('f',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 6', 'f', 'f', 'cc',
                'db AcAsKc',
            )),
            ('f',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'cc', 'cc', 'cc',
            )),
            ('f',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'f', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc',
                'db Qs', 'cc', 'cc',
                'db Qc', 'cc',
            )),
            ('f',),
        )
        # Bet/raising when the player's stack is already covered by another bet.
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 299', 'cc', 'cc',
            )),
            ('br 99',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'f', 'cc', 'cc',
                'db AcAsKc', 'br 197',
            )),
            ('br 50',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'br 197', 'cc', 'cc',
            )),
            ('br 197',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 6', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'cc', 'cc', 'cc', 'cc',
                'db Qc', 'cc', 'cc', 'br 293',
            )),
            ('br 193',),
        )
        # Making bet/raises that are meaningless (e.g. other players are all in).
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'br 99', 'cc',
                'br 199', 'cc',
            )),
            ('br 299',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'br 6', 'f', 'cc',
                'db AcAsKc', 'br 93',
            )),
            ('br 193',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'f', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc',
                'db Qs', 'br 197', 'cc',
            )),
            ('br 297',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'f', 'f', 'cc',
                'db AcAsKc', 'br 10', 'cc',
                'db Qs', 'br 10', 'br 20', 'cc',
                'db Qc', 'br 67',
            )),
            ('br 267',),
        )
        # Making bet/raises with invalid amounts (too low or too high).
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'cc', 'br 98', 'br 99',
            )),
            ('br 100',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'br 2', 'br 4', 'br 6', 'br 8', 'cc',
            )),
            ('br 9',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
                'db Qs', 'br 96', 'br 97',
            )),
            ('br 98',),
        )
        self.assertRaises(
            GameFrameError,
            parse_poker,
            parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
                'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'f', 'cc', 'cc',
                'db AcAsKc', 'cc', 'cc',
                'db Qs', 'cc', 'cc',
                'db Qc', 'br 50',
            )),
            ('br 55',),
        )

    def test_showdown_order(self) -> None:
        # Showdown is begun by the past aggressor or, if they don't exist, the first player.
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 299', 'cc', 'cc', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[2])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'f', 'br 99', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'cc', 'cc', 'cc',
            'db Qc', 'cc', 'cc', 'cc', 'cc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'br 2', 'cc', 'cc', 'cc',
            'db Qc', 'cc', 'cc', 'cc', 'cc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'cc', 'cc', 'cc',
            'db Qc', 'br 6', 'br 12', 'br 297', 'cc', 'cc', 'cc',
        ))).actor, game.players[2])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (200, 100, 300, 200)), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'br 199', 'cc', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[0])
        self.assertIs((game := parse_poker(NoLimitTexasHoldEm(1, (1, 2), (100,) * 4), (
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 99', 'cc', 'cc', 'cc',
            'db AcAsKc', 'db Qs', 'db Qc',
        ))).actor, game.players[0])

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

    def create_game(self) -> NoLimitTexasHoldEm:
        return NoLimitTexasHoldEm(6, (1, 2, 4), tuple(randint(0, 50) for _ in range(6)))


if __name__ == '__main__':
    main()
