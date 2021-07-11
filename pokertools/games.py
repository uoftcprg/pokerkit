from functools import partial

from pokertools.definitions import (
    BadugiDefinition, FiveCardDrawDefinition, FiveCardOmahaHoldEmDefinition, GreekHoldEmDefinition, KuhnPokerDefinition,
    OmahaHoldEmDefinition, ShortDeckHoldEmDefinition, SingleDrawLowball27Definition, SixCardOmahaHoldEmDefinition,
    TexasHoldEmDefinition, TripleDrawLowball27Definition,
)
from pokertools.gameframe import PokerGame
from pokertools.limits import FixedLimit, NoLimit, PotLimit
from pokertools.stakes import Stakes

# Fixed-Limit Texas Hold'em
FixedLimitTexasHoldEm = partial(PokerGame, FixedLimit, TexasHoldEmDefinition)
# No-Limit Texas Hold'em
NoLimitTexasHoldEm = partial(PokerGame, NoLimit, TexasHoldEmDefinition)

# Pot-Limit Omaha Hold'em
PotLimitOmahaHoldEm = partial(PokerGame, PotLimit, OmahaHoldEmDefinition)

# Fixed-Limit 5-Card Omaha Hold'em
FixedLimitFiveCardOmahaHoldEm = partial(PokerGame, FixedLimit, FiveCardOmahaHoldEmDefinition)
# Pot-Limit 5-Card Omaha Hold'em
PotLimitFiveCardOmahaHoldEm = partial(PokerGame, PotLimit, FiveCardOmahaHoldEmDefinition)

# Pot-Limit 6-Card Omaha Hold'em
PotLimitSixCardOmahaHoldEm = partial(PokerGame, PotLimit, SixCardOmahaHoldEmDefinition)

# Fixed-Limit Greek Hold'em
FixedLimitGreekHoldEm = partial(PokerGame, FixedLimit, GreekHoldEmDefinition)
# Pot-Limit Greek Hold'em
PotLimitGreekHoldEm = partial(PokerGame, PotLimit, GreekHoldEmDefinition)
# No-Limit Greek Hold'em
NoLimitGreekHoldEm = partial(PokerGame, NoLimit, GreekHoldEmDefinition)

# No-Limit Short-Deck Hold'em
NoLimitShortDeckHoldEm = partial(PokerGame, NoLimit, ShortDeckHoldEmDefinition)

# Fixed-Limit 5-Card Draw
FixedLimitFiveCardDraw = partial(PokerGame, FixedLimit, FiveCardDrawDefinition)
# Pot-Limit 5-Card Draw
PotLimitFiveCardDraw = partial(PokerGame, PotLimit, FiveCardDrawDefinition)
# No-Limit 5-Card Draw
NoLimitFiveCardDraw = partial(PokerGame, NoLimit, FiveCardDrawDefinition)

# Fixed-Limit Badugi
FixedLimitBadugi = partial(PokerGame, FixedLimit, BadugiDefinition)

# No-Limit 2-to-7 Single Draw Lowball
NoLimitSingleDrawLowball27 = partial(PokerGame, NoLimit, SingleDrawLowball27Definition)

# Fixed-Limit 2-to-7 Triple Draw Lowball
FixedLimitTripleDrawLowball27 = partial(PokerGame, FixedLimit, TripleDrawLowball27Definition)
# Pot-Limit 2-to-7 Triple Draw Lowball
PotLimitTripleDrawLowball27 = partial(PokerGame, PotLimit, TripleDrawLowball27Definition)

# Fixed-Limit Kuhn Poker
KuhnPoker = partial(PokerGame, FixedLimit, KuhnPokerDefinition, Stakes(1, ()), (2, 2))
