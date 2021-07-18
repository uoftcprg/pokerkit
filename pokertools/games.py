from functools import partial

from pokertools.definitions import (
    BadugiDefinition, FiveCardDrawDefinition, FiveCardOmahaHoldEmDefinition, GreekHoldEmDefinition, KuhnPokerDefinition,
    OmahaHoldEmDefinition, ShortDeckHoldEmDefinition, SingleDrawLowball27Definition, SixCardOmahaHoldEmDefinition,
    TexasHoldEmDefinition, TripleDrawLowball27Definition,
)
from pokertools.gameframe import PokerGame
from pokertools.limits import FixedLimit, NoLimit, PotLimit
from pokertools.stakes import Stakes

FixedLimitTexasHoldEm = partial(PokerGame, FixedLimit, TexasHoldEmDefinition)
"""Fixed-Limit Texas Hold'em"""
NoLimitTexasHoldEm = partial(PokerGame, NoLimit, TexasHoldEmDefinition)
"""No-Limit Texas Hold'em"""

PotLimitOmahaHoldEm = partial(PokerGame, PotLimit, OmahaHoldEmDefinition)
"""Pot-Limit Omaha Hold'em"""

FixedLimitFiveCardOmahaHoldEm = partial(PokerGame, FixedLimit, FiveCardOmahaHoldEmDefinition)
"""Fixed-Limit 5-Card Omaha Hold'em"""
PotLimitFiveCardOmahaHoldEm = partial(PokerGame, PotLimit, FiveCardOmahaHoldEmDefinition)
"""Pot-Limit 5-Card Omaha Hold'em"""

PotLimitSixCardOmahaHoldEm = partial(PokerGame, PotLimit, SixCardOmahaHoldEmDefinition)
"""Pot-Limit 6-Card Omaha Hold'em"""

FixedLimitGreekHoldEm = partial(PokerGame, FixedLimit, GreekHoldEmDefinition)
"""Fixed-Limit Greek Hold'em"""
PotLimitGreekHoldEm = partial(PokerGame, PotLimit, GreekHoldEmDefinition)
"""Pot-Limit Greek Hold'em"""
NoLimitGreekHoldEm = partial(PokerGame, NoLimit, GreekHoldEmDefinition)
"""No-Limit Greek Hold'em"""

NoLimitShortDeckHoldEm = partial(PokerGame, NoLimit, ShortDeckHoldEmDefinition)
"""No-Limit Short-Deck Hold'em"""

FixedLimitFiveCardDraw = partial(PokerGame, FixedLimit, FiveCardDrawDefinition)
"""Fixed-Limit 5-Card Draw"""
PotLimitFiveCardDraw = partial(PokerGame, PotLimit, FiveCardDrawDefinition)
"""Pot-Limit 5-Card Draw"""
NoLimitFiveCardDraw = partial(PokerGame, NoLimit, FiveCardDrawDefinition)
"""No-Limit 5-Card Draw"""

FixedLimitBadugi = partial(PokerGame, FixedLimit, BadugiDefinition)
"""Fixed-Limit Badugi"""

NoLimitSingleDrawLowball27 = partial(PokerGame, NoLimit, SingleDrawLowball27Definition)
"""No-Limit 2-to-7 Single Draw Lowball"""

FixedLimitTripleDrawLowball27 = partial(PokerGame, FixedLimit, TripleDrawLowball27Definition)
"""Fixed-Limit 2-to-7 Triple Draw Lowball"""
PotLimitTripleDrawLowball27 = partial(PokerGame, PotLimit, TripleDrawLowball27Definition)
"""Pot-Limit 2-to-7 Triple Draw Lowball"""

KuhnPoker = partial(PokerGame, FixedLimit, KuhnPokerDefinition, Stakes(1, ()), (2, 2))
"""Fixed-Limit Kuhn Poker"""
