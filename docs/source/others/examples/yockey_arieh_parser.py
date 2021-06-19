"""This shows the pot between Yockey and Arieh during which an insanely bad beat occurred.

Video: https://www.youtube.com/watch?v=pChCqb2FNxY
"""
from gameframe.poker import FixedLimitTripleDrawLowball27, parse_poker

game = FixedLimitTripleDrawLowball27(0, (75000, 150000), (1180000, 4340000, 5910000, 10765000))

parse_poker(game, (
    'dh 0 7h6c4c3d2c', 'dh 1 JsJcJdJhTs', 'dh 2 KsKcKdKhTh', 'dh 3 AsQs6s5c3c',
    'f', 'br 300000', 'br 450000', 'f', 'cc',

    'dd', 'dd AsQs 2hQh',
    'br 150000', 'cc',

    'dd', 'dd Qh 4d',
    'br 300000', 'cc',

    'dd', 'dd 6s 7c',
    'br 280000', 'cc',
))

# Pot: 2510000
print(f'Pot: {game.pot}')

parse_poker(game, (
    # Showdown
    's', 's'
))
