Interacting with Poker Games
============================

PokerTools offer a wide selection of pre-configured poker game variants. The list of those are as follows:

- Fixed-Limit Texas Hold'em: :const:`pokertools.games.FixedLimitTexasHoldEm`
- No-Limit Texas Hold'em: :const:`pokertools.games.NoLimitTexasHoldEm`
- Pot-Limit Omaha Hold'em: :const:`pokertools.games.PotLimitOmahaHoldEm`
- Fixed-Limit 5-Card Omaha Hold'em: :const:`pokertools.games.FixedLimitFiveCardOmahaHoldEm`
- Pot-Limit 5-Card Omaha Hold'em: :const:`pokertools.games.PotLimitFiveCardOmahaHoldEm`
- Pot-Limit 6-Card Omaha Hold'em: :const:`pokertools.games.PotLimitSixCardOmahaHoldEm`
- Fixed-Limit Greek Hold'em: :const:`pokertools.games.FixedLimitGreekHoldEm`
- Pot-Limit Greek Hold'em: :const:`pokertools.games.PotLimitGreekHoldEm`
- No-Limit Greek Hold'em: :const:`pokertools.games.NoLimitGreekHoldEm`
- No-Limit Short-Deck Hold'em: :const:`pokertools.games.NoLimitShortDeckHoldEm`
- Fixed-Limit 5-Card Draw: :const:`pokertools.games.FixedLimitFiveCardDraw`
- Pot-Limit 5-Card Draw: :const:`pokertools.games.PotLimitFiveCardDraw`
- No-Limit 5-Card Draw: :const:`pokertools.games.NoLimitFiveCardDraw`
- Fixed-Limit Badugi: :const:`pokertools.games.FixedLimitBadugi`
- No-Limit 2-to-7 Single Draw Lowball: :const:`pokertools.games.NoLimitSingleDrawLowball27`
- Fixed-Limit 2-to-7 Triple Draw Lowball: :const:`pokertools.games.FixedLimitTripleDrawLowball27`
- Pot-Limit 2-to-7 Triple Draw Lowball: :const:`pokertools.games.PotLimitTripleDrawLowball27`
- Fixed-Limit Kuhn Poker: :const:`pokertools.games.KuhnPoker`

Creating Pre-configured Poker Games
-----------------------------------

Creating pre-configured poker games are very simple.

.. code-block:: python

   from pokertools import *

   # Stakes with an ante of 1, a small blind of 1, and a big blind of 2.
   stakes = Stakes(1, (1, 2))
   # Example starting stacks of a 6-max poker game.
   starting_stacks = 200, 200, 300, 200, 100, 150

   # Create a Fixed-Limit Texas Hold'em game.
   flt = FixedLimitTexasHoldEm(stakes, starting_stacks)

   # Create a No-Limit Texas Hold'em game.
   nlt = NoLimitTexasHoldEm(stakes, starting_stacks)

   # Create a Pot-Limit Omaha Hold'em game.
   plo = PotLimitOmahaHoldEm(stakes, starting_stacks)

   # Create a Fixed-Limit 5-Card Omaha Hold'em game.
   flfco = FixedLimitFiveCardOmahaHoldEm(stakes, starting_stacks)

   # Create a Pot-Limit 5-Card Omaha Hold'em game.
   plfco = PotLimitFiveCardOmahaHoldEm(stakes, starting_stacks)

   # Create a Pot-Limit 6-Card Omaha Hold'em game.
   plsco = PotLimitSixCardOmahaHoldEm(stakes, starting_stacks)

   # Create a Fixed-Limit Greek Hold'em game.
   flg = FixedLimitGreekHoldEm(stakes, starting_stacks)

   # Create a Pot-Limit Greek Hold'em game.
   plg = PotLimitGreekHoldEm(stakes, starting_stacks)

   # Create a No-Limit Greek Hold'em game.
   nlg = NoLimitGreekHoldEm(stakes, starting_stacks)

   # Create a No-Limit Short-Deck Hold'em game.
   nls = NoLimitShortDeckHoldEm(stakes, starting_stacks)

   # Create a Fixed-Limit 5-Card Draw game.
   flfcd = FixedLimitFiveCardDraw(stakes, starting_stacks)

   # Create a Pot-Limit 5-Card Draw game.
   plfcd = PotLimitFiveCardDraw(stakes, starting_stacks)

   # Create a No-Limit 5-Card Draw game.
   nlfcd = NoLimitFiveCardDraw(stakes, starting_stacks)

   # Create a Fixed-Limit Badugi game.
   flb = FixedLimitBadugi(stakes, starting_stacks)

   # Create a No-Limit 2-to-7 Single Draw Lowball game.
   nlsdlb27 = NoLimitSingleDrawLowball27(stakes, starting_stacks)

   # Create a Fixed-Limit 2-to-7 Triple Draw Lowball game.
   fltdlb27 = FixedLimitTripleDrawLowball27(stakes, starting_stacks)

   # Create a Pot-Limit 2-to-7 Triple Draw Lowball game.
   pltdlb27 = PotLimitTripleDrawLowball27(stakes, starting_stacks)

   # Create a Kuhn Poker game.
   kuhn = KuhnPoker()

Often times, Short-deck hold'ems are played with button blinds. Games with button blinds can be created just with custom
blind structures, as shown below.

.. code-block:: python

   from pokertools import *

   # An ante of 1.
   ante = 1
   # A button blind of 2.
   blinds = 0, 0, 0, 0, 0, 2
   # Example starting stacks of a 6-max poker game.
   starting_stacks = 200, 200, 300, 200, 100, 150

   # Create a No-Limit Short-Deck Hold'em game.
   nls = NoLimitShortDeckHoldEm(Stakes(ante, blinds), starting_stacks)

   # A button blind of 2.
   blinds = {5: 2}

   # Create a No-Limit Short-Deck Hold'em game.
   nls = NoLimitShortDeckHoldEm(Stakes(ante, blinds), starting_stacks)

You can even pass a dictionary as the blinds.

Above games follow the main-stream rules of poker. But if these default rules are not desired, custom poker games can be
created by putting different components together. More about this is explained in a later section.

Querying Game Information
-------------------------

The current game information can be queried by calling methods or accessing attributes.

Note that accessing or calling the below attributes or methods will not change the game state.

.. code-block:: python

   from pokertools import *

   # Create a no-limit Texas hold'em game.
   game = NoLimitTexasHoldEm(Stakes(0, (1, 2)), (200, 200, 200))

   # Get the nature.
   nature = game.nature
   # Get the players.
   game.players
   # Get the first player.
   player = game.players[0]
   # True if the game is terminal, else False.
   game.is_terminal()
   # Get the current actor (either None, the nature or one of the players).
   game.actor

   # The limit of the game.
   game.limit
   # The definition of the game.
   game.definition
   # The stakes of the game.
   game.stakes
   # The starting stacks of the game.
   game.starting_stacks
   # The stages of the game.
   game.stages
   # The evaluators of the game.
   game.evaluators
   # The deck of the game.
   game.deck
   # The ante of the game.
   game.ante
   # The blinds of the game.
   game.blinds
   # The small_bet of the game.
   game.small_bet
   # The big_bet of the game.
   game.big_bet
   # The muck of the game.
   game.muck
   # The pot of the game.
   game.pot
   # The board of the game.
   game.board
   # The current stage of the game.
   game.stage
   # The side pots of the game.
   game.side_pots

   # The game of this actor.
   nature.game
   # None if this actor is the nature, else the index of this player.
   nature.index
   # True if the actor is the nature, else False.
   nature.is_nature()
   # True if the actor is one of the players, else False.
   nature.is_player()
   # True if this actor is in turn to act, else False.
   nature.is_actor()

   # The player to be dealt hole cards.
   nature.deal_hole_player
   # The number of hole cards to be dealt to each player.
   nature.deal_hole_count
   # The number of cards to be dealt to the board.
   nature.deal_board_count

   # True if the nature can deal hole cards, else False.
   nature.can_deal_hole()
   # True if the nature can deal the specified hole cards, else False.
   nature.can_deal_hole(parse_cards('Ac2d'))
   # True if the nature can deal cards to the board, else False.
   nature.can_deal_board()
   # True if the nature can deal the specified cards to the board, else False.
   nature.can_deal_board(parse_cards('KsKcKh'))

   # The game of this actor.
   player.game
   # None if this actor is the nature, else the index of this player.
   player.index
   # True if the actor is the nature, else False.
   player.is_nature()
   # True if the actor is one of the players, else False.
   player.is_player()
   # True if this actor is in turn to act, else False.
   player.is_actor()

   # The bet of the player.
   player.bet
   # The stack of the player.
   player.stack
   # The hole cards of the player.
   player.hole
   # The seen cards of the player.
   player.seen
   # The starting stack of the player.
   player.starting_stack
   # The blind of the player.
   player.blind
   # The total amount the player has in front.
   player.total
   # The effective stack of the player.
   player.effective_stack
   # The payoff of the player.
   player.payoff
   # An iterator of the hands of the player.
   player.hands
   # Most poker games only have one evaluator. Get the first hand.
   next(player.hands)
   # The check/call amount.
   player.check_call_amount
   # The minimum bet/raise amount.
   player.bet_raise_min_amount
   # The maximum bet/raise amount.
   player.bet_raise_max_amount
   # The pot bet/raise amount.
   player.bet_raise_pot_amount

   # True if the player has mucked, else False.
   player.is_mucked()
   # True if the player has shown, else False.
   player.is_shown()
   # True if the player is in the hand, else False.
   player.is_active()
   # True if the player has to showdown to attempt to win the pot.
   player.is_showdown_necessary()

   # True if the player can fold, else False.
   player.can_fold()
   # True if the player can check/call, else False.
   player.can_check_call()
   # True if the player can bet/raise any valid amount, else False.
   player.can_bet_raise()
   # True if the player can bet/raise the specified amount, else False.
   player.can_bet_raise(30)
   # True if the player can showdown, else False.
   player.can_showdown()
   # Returns the same value as above.
   player.can_showdown(False)
   # Returns the same value as above.
   player.can_showdown(True)
   # True if the player can stand pat, else False.
   player.can_discard_draw()
   # True if the player can discard the specified cards and draw random cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'))
   # True if the player can discard the specified cards and draw the specified cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))

Taking Actions in Poker Games
-----------------------------

The below demonstrates all possible actions that can be taken in PokerTools. Calling these methods will change the game
state.

.. code-block:: python

   from pokertools import *

   # Create a no-limit Texas Hold'em game.
   game = NoLimitTexasHoldEm(Stakes(0, (1, 2)), (200, 200, 200))

   # Get the nature.
   nature = game.nature
   # Get the player.
   player = game.players[0]

   # Deal random hole cards to the next player to be dealt.
   nature.deal_hole()
   # Deal specified hole cards to the next player to be dealt.
   nature.deal_hole(parse_cards('Ac2d'))
   # Deal random cards to the board.
   nature.deal_board()
   # Deal specified cards to the board.
   nature.deal_board(parse_cards('KsKcKh'))

   # Fold.
   player.fold()
   # Check/call.
   player.check_call()
   # Min-bet/raise.
   player.bet_raise()
   # Bet/raise 30.
   player.bet_raise(30)
   # Show hand if necessary to win the pot.
   player.showdown()
   # Force muck cards and do not contend.
   player.showdown(False)
   # Show hand even if the player loses anyway.
   player.showdown(True)
   # Stand pat.
   player.discard_draw()
   # Discard the specified cards and draw random cards.
   player.discard_draw(parse_cards('KsKcKh'))
   # Discard the specified cards and draw the specified cards.
   player.discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))

Parsing Poker Actions
---------------------

Interacting with poker games by calling functions are good enough for most, but can be cumbersome and take many lines.
There exists :meth:`pokertools.gameframe.PokerGame.parse` which allow you to parse commands and apply them to the game.
Example usages are shown in the later section.

Custom Games
------------

Creating and interacting with custom games are explained in the later section.
