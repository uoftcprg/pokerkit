from functools import partial

from pokertools.definitions import (
    BadugiDefinition, CourchevelDefinition, FiveCardDrawDefinition, FiveCardOmahaHoldEmDefinition,
    GreekHoldEmDefinition, KuhnPokerDefinition, OmahaHoldEmDefinition, ShortDeckHoldEmDefinition,
    SingleDrawLowball27Definition, SixCardOmahaHoldEmDefinition, TexasHoldEmDefinition, TripleDrawLowball27Definition,
)
from pokertools.gameframe import PokerGame
from pokertools.limits import FixedLimit, NoLimit, PotLimit

FixedLimitTexasHoldEm = partial(PokerGame, FixedLimit(), TexasHoldEmDefinition())
PotLimitTexasHoldEm = partial(PokerGame, PotLimit(), TexasHoldEmDefinition())
NoLimitTexasHoldEm = partial(PokerGame, NoLimit(), TexasHoldEmDefinition())

FixedLimitOmahaHoldEm = partial(PokerGame, FixedLimit(), OmahaHoldEmDefinition())
PotLimitOmahaHoldEm = partial(PokerGame, PotLimit(), OmahaHoldEmDefinition())
NoLimitOmahaHoldEm = partial(PokerGame, NoLimit(), OmahaHoldEmDefinition())

FixedLimitFiveCardOmahaHoldEm = partial(PokerGame, FixedLimit(), FiveCardOmahaHoldEmDefinition())
PotLimitFiveCardOmahaHoldEm = partial(PokerGame, PotLimit(), FiveCardOmahaHoldEmDefinition())
NoLimitFiveCardOmahaHoldEm = partial(PokerGame, NoLimit(), FiveCardOmahaHoldEmDefinition())

FixedLimitSixCardOmahaHoldEm = partial(PokerGame, FixedLimit(), SixCardOmahaHoldEmDefinition())
PotLimitSixCardOmahaHoldEm = partial(PokerGame, PotLimit(), SixCardOmahaHoldEmDefinition())
NoLimitSixCardOmahaHoldEm = partial(PokerGame, NoLimit(), SixCardOmahaHoldEmDefinition())

FixedLimitGreekHoldEm = partial(PokerGame, FixedLimit(), GreekHoldEmDefinition())
PotLimitGreekHoldEm = partial(PokerGame, PotLimit(), GreekHoldEmDefinition())
NoLimitGreekHoldEm = partial(PokerGame, NoLimit(), GreekHoldEmDefinition())

FixedLimitShortDeckHoldEm = partial(PokerGame, FixedLimit(), ShortDeckHoldEmDefinition())
PotLimitShortDeckHoldEm = partial(PokerGame, PotLimit(), ShortDeckHoldEmDefinition())
NoLimitShortDeckHoldEm = partial(PokerGame, NoLimit(), ShortDeckHoldEmDefinition())

FixedLimitFiveCardDraw = partial(PokerGame, FixedLimit(), FiveCardDrawDefinition())
PotLimitFiveCardDraw = partial(PokerGame, PotLimit(), FiveCardDrawDefinition())
NoLimitFiveCardDraw = partial(PokerGame, NoLimit(), FiveCardDrawDefinition())

FixedLimitBadugi = partial(PokerGame, FixedLimit(), BadugiDefinition())

NoLimitSingleDrawLowball27 = partial(PokerGame, NoLimit(), SingleDrawLowball27Definition())

FixedLimitTripleDrawLowball27 = partial(PokerGame, FixedLimit(), TripleDrawLowball27Definition())
PotLimitTripleDrawLowball27 = partial(PokerGame, PotLimit(), TripleDrawLowball27Definition())

FixedLimitCourchevel = partial(PokerGame, FixedLimit(), CourchevelDefinition())
PotLimitCourchevel = partial(PokerGame, PotLimit(), CourchevelDefinition())
NoLimitCourchevel = partial(PokerGame, NoLimit(), CourchevelDefinition())

KuhnPoker = partial(PokerGame, FixedLimit(), KuhnPokerDefinition(), 1, (), (2, 2))
