from unittest import TestCase, main

from auxiliary import next_or_none

from krieg.tests import KriegTestCaseMixin
from krieg.tictactoe import TicTacToeGame


class TicTacToeTestCase(KriegTestCaseMixin, TestCase):
    def test_draws(self):
        for locations in (
                ('11', '00', '01', '02', '10', '12', '20', '21', '22'),
                ('00', '02', '20', '22', '12', '10', '01', '11', '21'),
                ('00', '01', '02', '10', '12', '11', '20', '22', '21'),
                ('01', '00', '11', '02', '12', '10', '20', '21', '22'),
                ('11', '02', '22', '00', '01', '21', '10', '12', '20'),
        ):
            game = TicTacToeGame().mark(*locations)

            self.assertIsNone(game.winner)
            self.assertIsNone(game.loser)

    def test_losses(self):
        for locations in (
                ('22', '00', '01', '02', '10', '11', '12', '20'),
                ('11', '02', '12', '10', '22', '00', '01', '20'),
                ('11', '01', '20', '22', '21', '02', '00', '12'),
                ('00', '10', '01', '11', '22', '12'),
                ('01', '20', '11', '21', '02', '22'),
        ):
            game = TicTacToeGame().mark(*locations)

            self.assertIs(game.players[1], game.winner)
            self.assertIs(game.players[0], game.loser)

    def test_wins(self):
        for locations in (
                ('00', '01', '02', '10', '11', '12', '20'),
                ('11', '02', '01', '12', '21'),
                ('11', '01', '20', '02', '00', '10', '22'),
                ('11', '01', '20', '22', '02'),
                ('00', '10', '01', '11', '02'),
        ):
            game = TicTacToeGame().mark(*locations)

            self.assertIs(game.players[0], game.winner)
            self.assertIs(game.players[1], game.loser)

    def test_illegal_actions(self):
        self.assertRaises(ValueError, TicTacToeGame().mark('00').mark, '00')
        self.assertRaises(
            ValueError, TicTacToeGame().mark('00', '01').mark, '00',
        )
        self.assertRaises(ValueError, TicTacToeGame().mark, '33')
        self.assertRaises(ValueError, TicTacToeGame().mark, (-1, -1))
        self.assertRaises(
            ValueError, TicTacToeGame().mark('00').players[0].mark, 0, 1,
        )

    def create_game(self):
        return TicTacToeGame()

    def act(self, game):
        game.actor.mark()

    def verify(self, game):
        self.assertEqual(
            9 - len(tuple(game.empty_cell_locations)), game.action_count,
        )

        if game.is_terminal():
            self.assertTrue(
                next_or_none(game.empty_cell_locations) is None
                or game.winner is not None
            )

            self.assertFalse(game.players[0].can_mark())
            self.assertFalse(game.players[1].can_mark())

            for r in range(3):
                for c in range(3):
                    self.assertFalse(game.players[0].can_mark(r, c))
                    self.assertFalse(game.players[1].can_mark(r, c))
        else:
            self.assertFalse(
                next_or_none(game.empty_cell_locations) is None
                or game.winner is not None
            )

            actor = game.actor
            non_actor = next(actor)

            self.assertTrue(actor.can_mark())
            self.assertFalse(non_actor.can_mark())

            for r in range(3):
                for c in range(3):
                    if game.board[r][c] is None:
                        self.assertTrue(actor.can_mark(r, c))
                    else:
                        self.assertFalse(actor.can_mark(r, c))

                    self.assertFalse(non_actor.can_mark(r, c))


if __name__ == '__main__':
    main()
