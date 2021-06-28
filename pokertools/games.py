from functools import partial

from pokertools.definitions import (
    BadugiDefinition, FiveCardDrawDefinition, FiveCardOmahaHoldEmDefinition, GreekHoldEmDefinition, KuhnPokerDefinition,
    OmahaHoldEmDefinition, ShortDeckHoldEmDefinition, SingleDrawLowball27Definition, SixCardOmahaHoldEmDefinition,
    TexasHoldEmDefinition, TripleDrawLowball27Definition,
)
from pokertools.gameframe import PokerGame
from pokertools.limits import FixedLimit, NoLimit, PotLimit

FixedLimitTexasHoldEm = partial(PokerGame, FixedLimit(), TexasHoldEmDefinition())
NoLimitTexasHoldEm = partial(PokerGame, NoLimit(), TexasHoldEmDefinition())

PotLimitOmahaHoldEm = partial(PokerGame, PotLimit(), OmahaHoldEmDefinition())

FixedLimitFiveCardOmahaHoldEm = partial(PokerGame, FixedLimit(), FiveCardOmahaHoldEmDefinition())
PotLimitFiveCardOmahaHoldEm = partial(PokerGame, PotLimit(), FiveCardOmahaHoldEmDefinition())

PotLimitSixCardOmahaHoldEm = partial(PokerGame, PotLimit(), SixCardOmahaHoldEmDefinition())

FixedLimitGreekHoldEm = partial(PokerGame, FixedLimit(), GreekHoldEmDefinition())
PotLimitGreekHoldEm = partial(PokerGame, PotLimit(), GreekHoldEmDefinition())
NoLimitGreekHoldEm = partial(PokerGame, NoLimit(), GreekHoldEmDefinition())

NoLimitShortDeckHoldEm = partial(PokerGame, NoLimit(), ShortDeckHoldEmDefinition())

FixedLimitFiveCardDraw = partial(PokerGame, FixedLimit(), FiveCardDrawDefinition())
PotLimitFiveCardDraw = partial(PokerGame, PotLimit(), FiveCardDrawDefinition())
NoLimitFiveCardDraw = partial(PokerGame, NoLimit(), FiveCardDrawDefinition())

FixedLimitBadugi = partial(PokerGame, FixedLimit(), BadugiDefinition())

NoLimitSingleDrawLowball27 = partial(PokerGame, NoLimit(), SingleDrawLowball27Definition())

FixedLimitTripleDrawLowball27 = partial(PokerGame, FixedLimit(), TripleDrawLowball27Definition())
PotLimitTripleDrawLowball27 = partial(PokerGame, PotLimit(), TripleDrawLowball27Definition())

KuhnPoker = partial(PokerGame, FixedLimit(), KuhnPokerDefinition(), 1, (), (2, 2))
