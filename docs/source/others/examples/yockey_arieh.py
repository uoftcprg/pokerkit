"""This shows the pot between Yockey and Arieh during which an insanely bad beat occurred.

Video: https://www.youtube.com/watch?v=pChCqb2FNxY
"""
from pokertools import parse_card, parse_cards

from gameframe.poker import FixedLimitTripleDrawLowball27

game = FixedLimitTripleDrawLowball27(0, (75000, 150000), (1180000, 4340000, 5910000, 10765000))
yockey, hui, esposito, arieh = game.players

game.nature.deal_hole(yockey, parse_cards('7h6c4c3d2c'))
game.nature.deal_hole(hui, parse_cards('JsJcJdJhTs'))  # Cards unknown
game.nature.deal_hole(esposito, parse_cards('KsKcKdKhTh'))  # Cards unknown
game.nature.deal_hole(arieh, parse_cards('AsQs6s5c3c'))

esposito.fold()
arieh.bet_raise(300000)
yockey.bet_raise(450000)
hui.fold()
arieh.check_call()

yockey.discard_draw()
arieh.discard_draw(parse_cards('AsQs'), parse_cards('2hQh'))

yockey.bet_raise(150000)
arieh.check_call()

yockey.discard_draw()
arieh.discard_draw((parse_card('Qh'),), (parse_card('4d'),))

yockey.bet_raise(300000)
arieh.check_call()

yockey.discard_draw()
arieh.discard_draw((parse_card('6s'),), (parse_card('7c'),))

yockey.bet_raise(280000)
arieh.check_call()

# Pot: 2510000
print(f'Pot: {game.pot}')

yockey.showdown()
arieh.showdown()
