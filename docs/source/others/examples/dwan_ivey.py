"""This shows the 1.1 million dollar pot played between Dwan and Ivey.

Video: https://www.youtube.com/watch?v=GnxFohpljqM
"""
from pokertools import parse_cards

from gameframe.poker import NoLimitTexasHoldEm

game = NoLimitTexasHoldEm(500, (1000, 2000), (1125600, 2000000, 553500))  # Antonius's stack is unknown
ivey, antonius, dwan = game.players

# Pre-flop

game.nature.deal_hole(ivey, parse_cards('Ac2d'))
game.nature.deal_hole(antonius, parse_cards('5h7s'))  # Unknown
game.nature.deal_hole(dwan, parse_cards('7h6h'))

dwan.bet_raise(7000)
ivey.bet_raise(23000)
antonius.fold()
dwan.check_call()

# Flop

game.nature.deal_board(parse_cards('Jc3d5c'))

ivey.bet_raise(35000)
dwan.check_call()

# Turn

game.nature.deal_board(parse_cards('4h'))

ivey.bet_raise(90000)
dwan.bet_raise(232600)
ivey.bet_raise(1067100)
dwan.check_call()

# River

game.nature.deal_board(parse_cards('Jh'))

# Pot: 1109500 (1000 was probably collected as rake in the actual game)
print(f'Pot: {game.pot}')

ivey.showdown()
dwan.showdown()
