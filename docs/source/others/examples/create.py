from gameframe.poker import (FixedLimitBadugi, FixedLimitCourchevel, FixedLimitFiveCardDraw,
                             FixedLimitFiveCardOmahaHoldEm, FixedLimitGreekHoldEm, FixedLimitOmahaHoldEm,
                             FixedLimitShortDeckHoldEm, FixedLimitSingleDrawLowball27, FixedLimitSixCardOmahaHoldEm,
                             FixedLimitTexasHoldEm, FixedLimitTripleDrawLowball27, KuhnPoker, NoLimitBadugi,
                             NoLimitCourchevel, NoLimitFiveCardDraw, NoLimitFiveCardOmahaHoldEm, NoLimitGreekHoldEm,
                             NoLimitOmahaHoldEm, NoLimitShortDeckHoldEm, NoLimitSingleDrawLowball27,
                             NoLimitSixCardOmahaHoldEm, NoLimitTexasHoldEm, NoLimitTripleDrawLowball27, PotLimitBadugi,
                             PotLimitCourchevel, PotLimitFiveCardDraw, PotLimitFiveCardOmahaHoldEm, PotLimitGreekHoldEm,
                             PotLimitOmahaHoldEm, PotLimitShortDeckHoldEm, PotLimitSingleDrawLowball27,
                             PotLimitSixCardOmahaHoldEm, PotLimitTexasHoldEm, PotLimitTripleDrawLowball27)
from gameframe.rockpaperscissors import RockPaperScissors
from gameframe.tictactoe import TicTacToe

ante = 1
blinds = 1, 2
button_blind = 2
starting_stacks = 200, 200, 300

# Create a Fixed-Limit Texas Hold'em game
flt = FixedLimitTexasHoldEm(ante, blinds, starting_stacks)

# Create a Pot-Limit Texas Hold'em game
plt = PotLimitTexasHoldEm(ante, blinds, starting_stacks)

# Create a No-Limit Texas Hold'em game
nlt = NoLimitTexasHoldEm(ante, blinds, starting_stacks)

# Create a Fixed-Limit Omaha Hold'em game
flo = FixedLimitOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Pot-Limit Omaha Hold'em game
plo = PotLimitOmahaHoldEm(ante, blinds, starting_stacks)

# Create a No-Limit Omaha Hold'em game
nlo = NoLimitOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Fixed-Limit 5-Card Omaha Hold'em game
flfco = FixedLimitFiveCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Pot-Limit 5-Card Omaha Hold'em game
plfco = PotLimitFiveCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a No-Limit 5-Card Omaha Hold'em game
nlfco = NoLimitFiveCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Fixed-Limit 6-Card Omaha Hold'em game
flsco = FixedLimitSixCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Pot-Limit 6-Card Omaha Hold'em game
plsco = PotLimitSixCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a No-Limit 6-Card Omaha Hold'em game
nlsco = NoLimitSixCardOmahaHoldEm(ante, blinds, starting_stacks)

# Create a Fixed-Limit Courchevel game
flc = FixedLimitCourchevel(ante, blinds, starting_stacks)

# Create a Pot-Limit Courchevel game
plc = PotLimitCourchevel(ante, blinds, starting_stacks)

# Create a No-Limit Courchevel game
nlc = NoLimitCourchevel(ante, blinds, starting_stacks)

# Create a Fixed-Limit Greek Hold'em game
flg = FixedLimitGreekHoldEm(ante, blinds, starting_stacks)

# Create a Pot-Limit Greek Hold'em game
plg = PotLimitGreekHoldEm(ante, blinds, starting_stacks)

# Create a No-Limit Greek Hold'em game
nlg = NoLimitGreekHoldEm(ante, blinds, starting_stacks)

# Create a Fixed-Limit Short-Deck Hold'em game
fls = FixedLimitShortDeckHoldEm(ante, button_blind, starting_stacks)

# Create a Pot-Limit Short-Deck Hold'em game
pls = PotLimitShortDeckHoldEm(ante, button_blind, starting_stacks)

# Create a No-Limit Short-Deck Hold'em game
nls = NoLimitShortDeckHoldEm(ante, button_blind, starting_stacks)

# Create a Fixed-Limit 5-Card Draw game
flfcd = FixedLimitFiveCardDraw(ante, blinds, starting_stacks)

# Create a Pot-Limit 5-Card Draw game
plfcd = PotLimitFiveCardDraw(ante, blinds, starting_stacks)

# Create a No-Limit 5-Card Draw game
nlfcd = NoLimitFiveCardDraw(ante, blinds, starting_stacks)

# Create a Fixed-Limit Badugi game
flb = FixedLimitBadugi(ante, blinds, starting_stacks)

# Create a Pot-Limit Badugi game
plb = PotLimitBadugi(ante, blinds, starting_stacks)

# Create a No-Limit Badugi game
nlb = NoLimitBadugi(ante, blinds, starting_stacks)

# Create a Fixed-Limit 2-to-7 Single Draw Lowball game
flsdlb27 = FixedLimitSingleDrawLowball27(ante, blinds, starting_stacks)

# Create a Pot-Limit 2-to-7 Single Draw Lowball game
plsdlb27 = PotLimitSingleDrawLowball27(ante, blinds, starting_stacks)

# Create a No-Limit 2-to-7 Single Draw Lowball game
nlsdlb27 = NoLimitSingleDrawLowball27(ante, blinds, starting_stacks)

# Create a Fixed-Limit 2-to-7 Triple Draw Lowball game
fltdlb27 = FixedLimitTripleDrawLowball27(ante, blinds, starting_stacks)

# Create a Pot-Limit 2-to-7 Triple Draw Lowball game
pltdlb27 = PotLimitTripleDrawLowball27(ante, blinds, starting_stacks)

# Create a No-Limit 2-to-7 Triple Draw Lowball game
nltdlb27 = NoLimitTripleDrawLowball27(ante, blinds, starting_stacks)

# Create a Kuhn Poker game
kuhn = KuhnPoker()

# Create a tic tac toe game
ttt = TicTacToe()

# Create a rock paper scissors game
rps = RockPaperScissors()
