"""This is a sample rock paper scissors game."""
from gameframe.rockpaperscissors import RockPaperScissors, RockPaperScissorsHand

game = RockPaperScissors()
x, y = game.players

x.throw(RockPaperScissorsHand.ROCK)
y.throw(RockPaperScissorsHand.PAPER)
