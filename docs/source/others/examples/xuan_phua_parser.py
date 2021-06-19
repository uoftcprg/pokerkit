"""This shows the 800K dollar pot played between Xuan and Phua.

Video: https://www.youtube.com/watch?v=QlgCcphLjaQ
"""
from gameframe.poker import NoLimitShortDeckHoldEm, parse_poker

game = NoLimitShortDeckHoldEm(3000, 3000, (495000, 232000, 362000, 403000, 301000, 204000))

parse_poker(game, (
    # Pre-flop
    'dh 0 Th8h', 'dh 1 QsJd', 'dh 2 QhQd', 'dh 3 8d7c', 'dh 4 KhKs', 'dh 5 8c7h',
    'cc', 'cc', 'br 35000', 'f', 'br 298000', 'f', 'f', 'f', 'cc',
    # Flop
    'db 9h6cKc',
    # Turn
    'db Jh',
    # River
    'db Ts',
))

# Pot: 623000
print(f'Pot: {game.pot}')

parse_poker(game, (
    # Showdown
    's', 's'
))
