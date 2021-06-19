"""This is a sample tic tac toe game resulting in the first player winning."""
from gameframe.tictactoe import TicTacToe, parse_tic_tac_toe

game = TicTacToe()

parse_tic_tac_toe(game, (
    (0, 0),
    (1, 0),
    (0, 1),
    (1, 1),
    (0, 2),
))
