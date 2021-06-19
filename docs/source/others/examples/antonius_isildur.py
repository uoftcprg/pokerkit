"""This shows the 1.3 million dollar pot played between Antonius and Isildur.

The integral values are multiplied by 100 to represent cents in dollars.

Video: https://www.youtube.com/watch?v=UMBm66Id2AA
"""
from pokertools import parse_cards

from gameframe.poker import PotLimitOmahaHoldEm

game = PotLimitOmahaHoldEm(0, (50000, 100000), (125945025, 67847350))
antonius, isildur = game.players

# Pre-flop

game.nature.deal_hole(antonius, parse_cards('Ah3sKsKh'))
game.nature.deal_hole(isildur, parse_cards('6d9s7d8h'))

isildur.bet_raise(300000)
antonius.bet_raise(900000)
isildur.bet_raise(2700000)
antonius.bet_raise(8100000)
isildur.check_call()

# Flop

game.nature.deal_board(parse_cards('4s5c2h'))

antonius.bet_raise(9100000)
isildur.bet_raise(43500000)
antonius.bet_raise(77900000)
isildur.check_call()

# Turn and River

game.nature.deal_board(parse_cards('5h'))
game.nature.deal_board(parse_cards('9c'))

# Pot: 1356947.00 (0.50 was probably collected as rake in the actual game)
print(f'Pot: {game.pot}')

antonius.showdown()
isildur.showdown()
