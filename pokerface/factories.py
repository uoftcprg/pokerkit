from functools import partial

from pokerface.game import PokerGame
from pokerface.limits import FixedLimit, NoLimit, PotLimit
from pokerface.stakes import Stakes
from pokerface.variants import (
    BadugiVariant, FiveCardDrawVariant, FiveCardOmahaHoldEmVariant,
    GreekHoldEmVariant, KuhnPokerVariant, OmahaHoldEmVariant,
    ShortDeckHoldEmVariant, SingleDrawLowball27Variant,
    SixCardOmahaHoldEmVariant, TexasHoldEmVariant, TripleDrawLowball27Variant,
)

FixedLimitTexasHoldEm = partial(PokerGame, FixedLimit, TexasHoldEmVariant)
"""Fixed-Limit Texas Hold'em"""
NoLimitTexasHoldEm = partial(PokerGame, NoLimit, TexasHoldEmVariant)
"""No-Limit Texas Hold'em"""

PotLimitOmahaHoldEm = partial(PokerGame, PotLimit, OmahaHoldEmVariant)
"""Pot-Limit Omaha Hold'em"""

FixedLimitFiveCardOmahaHoldEm = partial(
    PokerGame, FixedLimit, FiveCardOmahaHoldEmVariant,
)
"""Fixed-Limit 5-Card Omaha Hold'em"""
PotLimitFiveCardOmahaHoldEm = partial(
    PokerGame, PotLimit, FiveCardOmahaHoldEmVariant,
)
"""Pot-Limit 5-Card Omaha Hold'em"""

PotLimitSixCardOmahaHoldEm = partial(
    PokerGame, PotLimit, SixCardOmahaHoldEmVariant,
)
"""Pot-Limit 6-Card Omaha Hold'em"""

FixedLimitGreekHoldEm = partial(PokerGame, FixedLimit, GreekHoldEmVariant)
"""Fixed-Limit Greek Hold'em"""
PotLimitGreekHoldEm = partial(PokerGame, PotLimit, GreekHoldEmVariant)
"""Pot-Limit Greek Hold'em"""
NoLimitGreekHoldEm = partial(PokerGame, NoLimit, GreekHoldEmVariant)
"""No-Limit Greek Hold'em"""

NoLimitShortDeckHoldEm = partial(PokerGame, NoLimit, ShortDeckHoldEmVariant)
"""No-Limit Short-Deck Hold'em"""

FixedLimitFiveCardDraw = partial(PokerGame, FixedLimit, FiveCardDrawVariant)
"""Fixed-Limit 5-Card Draw"""
PotLimitFiveCardDraw = partial(PokerGame, PotLimit, FiveCardDrawVariant)
"""Pot-Limit 5-Card Draw"""
NoLimitFiveCardDraw = partial(PokerGame, NoLimit, FiveCardDrawVariant)
"""No-Limit 5-Card Draw"""

FixedLimitBadugi = partial(PokerGame, FixedLimit, BadugiVariant)
"""Fixed-Limit Badugi"""

NoLimitSingleDrawLowball27 = partial(
    PokerGame, NoLimit, SingleDrawLowball27Variant,
)
"""No-Limit 2-to-7 Single Draw Lowball"""

FixedLimitTripleDrawLowball27 = partial(
    PokerGame, FixedLimit, TripleDrawLowball27Variant,
)
"""Fixed-Limit 2-to-7 Triple Draw Lowball"""
PotLimitTripleDrawLowball27 = partial(
    PokerGame, PotLimit, TripleDrawLowball27Variant,
)
"""Pot-Limit 2-to-7 Triple Draw Lowball"""

KuhnPoker = partial(
    PokerGame, FixedLimit, KuhnPokerVariant, Stakes(1, ()), (2, 2),
)
"""Fixed-Limit Kuhn Poker"""
