from unittest import TestCase, main

from pokertools import (
    FixedLimitTexasHoldEm, NoLimitTexasHoldEm, PotLimitOmahaHoldEm,
    PotLimitTripleDrawLowball27, Stakes, parse_cards,
)


class GameTestCase(TestCase):
    def test_betting_action_when_not_betting_stage(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'cc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).act, 'cc')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'br 4', 'cc'
        ).act, 'br 100')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'cc', 'cc', 'cc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).act, 'cc')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'br 4', 'br 6', 'cc', 'cc', 'cc',
        ).act, 'br 8')

    def test_fold_when_redundant(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'br 6', 'f', 'f', 'cc',
            'db AcAsKc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc',
        ).act, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc',
        ).act, 'f')

    def test_bet_raise_when_covered(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'br 199',
        ).act, 'br 100')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 50', 'br 193',
        ).act, 'br 93')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'br 195',
        ).act, 'br 95')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 93',
        ).act, 'br 93')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'br 299', 'cc', 'cc',
        ).act, 'br 99')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'f', 'f', 'cc', 'cc',
            'db AcAsKc', 'br 197',
        ).act, 'br 50')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'br 197', 'cc', 'cc',
        ).act, 'br 197')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'br 6', 'cc', 'cc',
            'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'cc', 'cc', 'cc',
            'db Qc', 'cc', 'cc', 'br 293',
        ).act, 'br 193')

    def test_bet_raise_when_irrelevant(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 99',
        ).act, 'br 197')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 93',
        ).act, 'br 193')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'br 95',
        ).act, 'br 195')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 93',
        ).act, 'br 193')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'br 99', 'cc',
            'br 199',
            'cc',
        ).act, 'br 299')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'br 6', 'f', 'cc',
            'db AcAsKc',
            'br 93',
        ).act, 'br 193')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc',
            'db Qs',
            'br 197', 'cc',
        ).act, 'br 297')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'f', 'f', 'cc',
            'db AcAsKc',
            'br 10', 'cc',
            'db Qs',
            'br 10', 'br 20', 'cc',
            'db Qc',
            'br 67',
        ).act, 'br 267')

    def test_bet_raise_with_invalid_amount(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6',
        ).act, 'br 9')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6',
        ).act, 'br 1000')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'br 12', 'br 24',
        ).act, 'br 30')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'br 4', 'cc',
            'db Qs',
            'br 4', 'br 8',
        ).act, 'br 10')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).act, 'br 1')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'cc', 'br 98', 'br 99',
        ).act, 'br 100')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'br 2', 'br 4', 'br 6', 'br 8', 'cc',
        ).act, 'br 9')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'br 96', 'br 97',
        ).act, 'br 98')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 50',
        ).act, 'br 55')

    def test_showdown_opener(self):
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'br 4', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).act(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 6', 'br 12', 'cc',
        ).actor.index, 0)

        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'br 2', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).act(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'br 6', 'br 12', 'br 150', 'cc', 'cc', 'cc',
        ).actor.index, 2)

    def test_bet_raise_when_max_count(self):
        game = NoLimitTexasHoldEm(Stakes(1, ()), (101, 101)).act('dh', 'dh')

        for _ in range(100):
            game.actor.bet_raise()

        self.assertRaises(ValueError, game.actor.bet_raise)

        game = PotLimitOmahaHoldEm(Stakes(1, ()), (101, 101)).act('dh', 'dh')

        for _ in range(100):
            game.actor.bet_raise()

        self.assertRaises(ValueError, game.actor.bet_raise)

        game = FixedLimitTexasHoldEm(Stakes(1, (1, 2)), (101, 101)).act(
            'dh', 'dh',
        )

        for _ in range(3):
            game.actor.bet_raise()

        self.assertRaises(ValueError, game.actor.bet_raise)
        game.actor.check_call()

        for _ in range(3):
            game.actor.deal_board()

            for _ in range(4):
                game.actor.bet_raise()

            self.assertRaises(ValueError, game.actor.bet_raise)
            game.actor.check_call()

    def test_bet_raise_amounts(self):
        game = NoLimitTexasHoldEm(Stakes(0, (5, 10)), (1000, 1000)).act(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 1000)
        self.assertEqual(game.actor.bet_raise_pot_amount, 30)
        game.act('cc', 'cc')

        for _ in range(3):
            game.act('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 10)
            self.assertEqual(game.actor.bet_raise_max_amount, 990)
            self.assertEqual(game.actor.bet_raise_pot_amount, 20)
            game.act('cc', 'cc')

        game = PotLimitOmahaHoldEm(Stakes(0, (5, 10)), (1000, 1000)).act(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 30)
        self.assertEqual(game.actor.bet_raise_pot_amount, 30)
        game.act('br 25')
        self.assertEqual(game.actor.bet_raise_min_amount, 40)
        self.assertEqual(game.actor.bet_raise_max_amount, 75)
        self.assertEqual(game.actor.bet_raise_pot_amount, 75)
        game.act('cc')

        for _ in range(3):
            game.act('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 10)
            self.assertEqual(game.actor.bet_raise_max_amount, 50)
            self.assertEqual(game.actor.bet_raise_pot_amount, 50)
            game.act('cc', 'cc')

        game = FixedLimitTexasHoldEm(Stakes(0, (5, 10)), (1000, 1000)).act(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 20)
        self.assertEqual(game.actor.bet_raise_pot_amount, 20)
        game.act('cc', 'cc', 'db')

        self.assertEqual(game.actor.bet_raise_min_amount, 10)
        self.assertEqual(game.actor.bet_raise_max_amount, 10)
        self.assertEqual(game.actor.bet_raise_pot_amount, 10)
        game.act('br')
        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 20)
        self.assertEqual(game.actor.bet_raise_pot_amount, 20)
        game.act('cc')

        for _ in range(2):
            game.act('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 20)
            self.assertEqual(game.actor.bet_raise_max_amount, 20)
            self.assertEqual(game.actor.bet_raise_pot_amount, 20)
            game.act('br')
            self.assertEqual(game.actor.bet_raise_min_amount, 40)
            self.assertEqual(game.actor.bet_raise_max_amount, 40)
            self.assertEqual(game.actor.bet_raise_pot_amount, 40)
            game.act('br')
            self.assertEqual(game.actor.bet_raise_min_amount, 60)
            self.assertEqual(game.actor.bet_raise_max_amount, 60)
            self.assertEqual(game.actor.bet_raise_pot_amount, 60)
            game.act('cc')

    def test_verify(self):
        self.assertRaises(
            ValueError, NoLimitTexasHoldEm, Stakes(1, (1, 2)), (),
        )
        self.assertRaises(
            ValueError, NoLimitTexasHoldEm, Stakes(1, (1, 2)), (1,),
        )
        self.assertRaises(
            ValueError, NoLimitTexasHoldEm, Stakes(1, (1, 2, 4, 8)), (
                100, 100, 100,
            ),
        )
        self.assertRaises(ValueError, NoLimitTexasHoldEm, Stakes(1, (1, 2)), (
            100, -100, -100,
        ))

    def test_draw_muck(self):
        game = PotLimitTripleDrawLowball27(
            Stakes(0, (1, 2)), (100,) * 4,
        ).act(
            'dh AcKcQcJcTc', 'dh AdKdQdJdTd', 'dh AhKhQhJhTh', 'dh AsKsQsJsTs',
            'cc', 'cc', 'cc', 'cc',
            'dd AcKcQcJcTc 9c8c7c6c5c', 'dd AdKdQdJdTd 9d8d7d6d5d',
            'dd AhKhQhJhTh 9h8h7h6h5h', 'dd AsKsQsJsTs 9s8s7s6s5s',
            'cc', 'cc', 'cc', 'cc',
            'dd 9c8c7c6c5c 4c4d4h4s2c',
        )

        self.assertTrue(game.actor.can_discard_draw())
        self.assertTrue(game.actor.can_discard_draw(()))
        self.assertTrue(game.actor.can_discard_draw((), ()))

        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9d'), parse_cards('3c'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9d8d7d'), parse_cards('3c3d3h'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9d8d7d6d5d'), parse_cards('3c3d3h3s2d'),
        ))

        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9d'), parse_cards('9c'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9d8d7d'), parse_cards('9c8c7c'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9d8d7d6d5d'), parse_cards('9c8c7c6c5c'),
        ))

        game.actor.discard_draw(
            parse_cards('9d8d7d6d5d'), parse_cards('3c3d3h3s2d'),
        )

        self.assertTrue(game.actor.can_discard_draw())
        self.assertTrue(game.actor.can_discard_draw(()))
        self.assertTrue(game.actor.can_discard_draw((), ()))

        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h'), parse_cards('2s'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h8h'), parse_cards('2s2h'),
        ))

        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h'), parse_cards('Ac'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h'), parse_cards('AcKc'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h8h7h'), parse_cards('AcKcQc'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h8h7h6h5h'), parse_cards('AcKcQcJcTc'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h8h7h'), parse_cards('2s2hQc'),
        ))
        self.assertTrue(game.actor.can_discard_draw(
            parse_cards('9h8h7h6h5h'), parse_cards('2s2hQcJcTc'),
        ))

        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h'), parse_cards('Ah'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h'), parse_cards('AhKh'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h7h'), parse_cards('AhKhQh'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h7h6h5h'), parse_cards('AhKhQhJhTh'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h7h'), parse_cards('2s2hQh'),
        ))
        self.assertFalse(game.actor.can_discard_draw(
            parse_cards('9h8h7h6h5h'), parse_cards('2s2hQhJhTh'),
        ))

        game.actor.discard_draw(
            parse_cards('9h8h7h6h5h'), parse_cards('AcKcQcJcTc'),
        )


if __name__ == '__main__':
    main()
