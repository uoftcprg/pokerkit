from itertools import product
from random import randint
from unittest import TestCase, main

from auxiliary import const, next_or_none

from krieg.rockpaperscissors import (
    RockPaperScissorsGame, RockPaperScissorsHand, RockPaperScissorsPlayer,
)
from krieg.tests import KriegTestCaseMixin


class RockPaperScissorsTestCase(KriegTestCaseMixin, TestCase):
    def test_heads_up(self):
        game = RockPaperScissorsGame().throw(
            RockPaperScissorsHand.ROCK, RockPaperScissorsHand.SCISSORS,
        )
        self.assertIs(next(game.winners), game.players[0])
        self.assertIs(next(game.losers), game.players[1])

        game = RockPaperScissorsGame().throw(
            RockPaperScissorsHand.PAPER, RockPaperScissorsHand.SCISSORS,
        )
        self.assertIs(next(game.winners), game.players[1])
        self.assertIs(next(game.losers), game.players[0])

        game = RockPaperScissorsGame().throw(
            RockPaperScissorsHand.PAPER, RockPaperScissorsHand.PAPER,
        )
        self.assertIs(next_or_none(game.winners), None)
        self.assertIs(next_or_none(game.losers), None)

    def test_non_heads_up(self):
        game = RockPaperScissorsGame(3).throw(*map(RockPaperScissorsHand, (
            'Rock', 'Paper', 'Scissors',
        )))
        self.assertSequenceEqual(tuple(game.winners), ())
        self.assertSequenceEqual(tuple(game.losers), ())

        game = RockPaperScissorsGame(4).throw(*map(RockPaperScissorsHand, (
            'Rock', 'Paper', 'Rock', 'Rock',
        )))
        self.assertSequenceEqual(tuple(game.winners), (game.players[1],))
        self.assertSequenceEqual(tuple(game.losers), (
            game.players[0], *game.players[2:],
        ))

        game = RockPaperScissorsGame(5).throw(*map(RockPaperScissorsHand, (
            'Rock', 'Paper', 'Scissors', 'Rock', 'Paper',
        )))
        self.assertSequenceEqual(tuple(game.winners), ())
        self.assertSequenceEqual(tuple(game.losers), ())

        game = RockPaperScissorsGame(6).throw(*map(RockPaperScissorsHand, (
            'Paper', 'Paper', 'Rock', 'Rock', 'Paper', 'Paper',
        )))
        self.assertSequenceEqual(
            tuple(game.winners),
            tuple(game.players[:2]) + tuple(game.players[4:]),
        )
        self.assertSequenceEqual(tuple(game.losers), game.players[2:4])

    def create_game(self):
        return RockPaperScissorsGame(randint(2, 5))

    def act(self, game):
        next(filter(RockPaperScissorsPlayer.can_throw, game.players)).throw()

    def verify(self, game):
        hands = tuple(map(RockPaperScissorsPlayer.hand.fget, game.players))

        if game.is_terminal():
            self.assertTrue(all(hands))
            self.assertEqual(game.action_count, len(game.players))

            winner = next_or_none(game.winners)
            loser = next_or_none(game.losers)

            if winner is None:
                self.assertTrue(const(hands) or len(set(hands)) == 3)
            else:
                for player in game.players:
                    self.assertLessEqual(player.hand, winner.hand)

            self.assertEqual(winner is None, loser is None)

            for winner, loser in product(game.winners, game.losers):
                self.assertGreater(winner.hand, loser.hand)
        else:
            self.assertFalse(all(hands))
            self.assertLess(game.action_count, len(game.players))

        for player in game.players:
            if player.hand is None:
                self.assertTrue(player.can_throw())
            else:
                self.assertFalse(player.can_throw())

            for hand in RockPaperScissorsHand:
                if player.hand is None:
                    self.assertTrue(player.can_throw(hand))
                else:
                    self.assertFalse(player.can_throw(hand))


if __name__ == '__main__':
    main()
