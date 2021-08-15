from unittest import TestCase, main

from pokertools import (
    FixedLimitTexasHoldEm, NoLimitTexasHoldEm, PotLimitOmahaHoldEm,
    PotLimitTripleDrawLowball27, Stakes, parse_cards,
)


class GameTestCase(TestCase):
    def test_betting_action_when_not_betting_stage(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'cc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).parse, 'cc')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'br 4', 'cc'
        ).parse, 'br 100')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).parse, 'cc')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'br 4', 'br 6', 'cc', 'cc', 'cc',
        ).parse, 'br 8')

    def test_fold_when_redundant(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'cc',
            'db AcAsKc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'br 6', 'f', 'f', 'cc',
            'db AcAsKc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc',
        ).parse, 'f')

    def test_bet_raise_when_covered(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'br 199',
        ).parse, 'br 100')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 50', 'br 193',
        ).parse, 'br 93')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'br 195',
        ).parse, 'br 95')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 93',
        ).parse, 'br 93')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'br 299', 'cc', 'cc',
        ).parse, 'br 99')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'f', 'f', 'cc', 'cc',
            'db AcAsKc', 'br 197',
        ).parse, 'br 50')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'br 197', 'cc', 'cc',
        ).parse, 'br 197')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd', 'br 6', 'cc', 'cc',
            'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'cc', 'cc', 'cc',
            'db Qc', 'cc', 'cc', 'br 293',
        ).parse, 'br 193')

    def test_bet_raise_when_irrelevant(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 99',
        ).parse, 'br 197')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 93',
        ).parse, 'br 193')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'br 95',
        ).parse, 'br 195')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 93',
        ).parse, 'br 193')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'br 99', 'cc',
            'br 199',
            'cc',
        ).parse, 'br 299')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'br 6', 'f', 'cc',
            'db AcAsKc',
            'br 93',
        ).parse, 'br 193')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc',
            'db Qs',
            'br 197', 'cc',
        ).parse, 'br 297')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'f', 'f', 'cc',
            'db AcAsKc',
            'br 10', 'cc',
            'db Qs',
            'br 10', 'br 20', 'cc',
            'db Qc',
            'br 67',
        ).parse, 'br 267')

    def test_bet_raise_with_invalid_amount(self):
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6',
        ).parse, 'br 9')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6',
        ).parse, 'br 1000')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'br 12', 'br 24',
        ).parse, 'br 30')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'br 4', 'cc',
            'db Qs',
            'br 4', 'br 8',
        ).parse, 'br 10')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
            'dh QdQh', 'dh AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).parse, 'br 1')

        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'cc', 'br 98', 'br 99',
        ).parse, 'br 100')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'br 2', 'br 4', 'br 6', 'br 8', 'cc',
        ).parse, 'br 9')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'br 96', 'br 97',
        ).parse, 'br 98')
        self.assertRaises(ValueError, NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100, 300, 200),
        ).parse(
            'dh QdQh', 'dh AhAd', 'dh KsKh', 'dh JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 50',
        ).parse, 'br 55')

    def test_showdown_opener(self):
        self.assertEqual(NoLimitTexasHoldEm(
            Stakes(1, (1, 2)), (200, 100),
        ).parse(
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
        ).parse(
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
        ).parse(
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
        ).parse(
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
        ).parse(
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
        ).parse(
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
        ).parse(
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
        game = NoLimitTexasHoldEm(Stakes(1, ()), (101, 101)).parse('dh', 'dh')

        for _ in range(100):
            game.actor.bet_raise()

        self.assertRaises(ValueError, game.actor.bet_raise)

        game = PotLimitOmahaHoldEm(Stakes(1, ()), (101, 101)).parse('dh', 'dh')

        for _ in range(100):
            game.actor.bet_raise()

        self.assertRaises(ValueError, game.actor.bet_raise)

        game = FixedLimitTexasHoldEm(Stakes(1, (1, 2)), (101, 101)).parse(
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
        game = NoLimitTexasHoldEm(Stakes(0, (5, 10)), (1000, 1000)).parse(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 1000)
        self.assertEqual(game.actor.bet_raise_pot_amount, 30)
        game.parse('cc', 'cc')

        for _ in range(3):
            game.parse('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 10)
            self.assertEqual(game.actor.bet_raise_max_amount, 990)
            self.assertEqual(game.actor.bet_raise_pot_amount, 20)
            game.parse('cc', 'cc')

        game = PotLimitOmahaHoldEm(Stakes(0, (5, 10)), (1000, 1000)).parse(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 30)
        self.assertEqual(game.actor.bet_raise_pot_amount, 30)
        game.parse('br 25')
        self.assertEqual(game.actor.bet_raise_min_amount, 40)
        self.assertEqual(game.actor.bet_raise_max_amount, 75)
        self.assertEqual(game.actor.bet_raise_pot_amount, 75)
        game.parse('cc')

        for _ in range(3):
            game.parse('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 10)
            self.assertEqual(game.actor.bet_raise_max_amount, 50)
            self.assertEqual(game.actor.bet_raise_pot_amount, 50)
            game.parse('cc', 'cc')

        game = FixedLimitTexasHoldEm(Stakes(0, (5, 10)), (1000, 1000)).parse(
            'dh', 'dh',
        )

        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 20)
        self.assertEqual(game.actor.bet_raise_pot_amount, 20)
        game.parse('cc', 'cc', 'db')

        self.assertEqual(game.actor.bet_raise_min_amount, 10)
        self.assertEqual(game.actor.bet_raise_max_amount, 10)
        self.assertEqual(game.actor.bet_raise_pot_amount, 10)
        game.parse('br')
        self.assertEqual(game.actor.bet_raise_min_amount, 20)
        self.assertEqual(game.actor.bet_raise_max_amount, 20)
        self.assertEqual(game.actor.bet_raise_pot_amount, 20)
        game.parse('cc')

        for _ in range(2):
            game.parse('db')
            self.assertEqual(game.actor.bet_raise_min_amount, 20)
            self.assertEqual(game.actor.bet_raise_max_amount, 20)
            self.assertEqual(game.actor.bet_raise_pot_amount, 20)
            game.parse('br')
            self.assertEqual(game.actor.bet_raise_min_amount, 40)
            self.assertEqual(game.actor.bet_raise_max_amount, 40)
            self.assertEqual(game.actor.bet_raise_pot_amount, 40)
            game.parse('br')
            self.assertEqual(game.actor.bet_raise_min_amount, 60)
            self.assertEqual(game.actor.bet_raise_max_amount, 60)
            self.assertEqual(game.actor.bet_raise_pot_amount, 60)
            game.parse('cc')

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
        ).parse(
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
