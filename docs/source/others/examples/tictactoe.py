"""This is a sample tic tac toe game resulting in a tie."""
from gameframe.tictactoe import TicTacToe

game = TicTacToe()
x, y = game.players

x.mark(1, 1)
y.mark(0, 0)
x.mark(2, 0)
y.mark(0, 2)
x.mark(0, 1)
y.mark(2, 1)
x.mark(1, 2)
y.mark(1, 0)
x.mark(2, 2)
