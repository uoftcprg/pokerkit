Interacting with PokerTools
===========================

In order to use the pokertools package in your project, you must first import it.

.. code-block:: python

   from pokertools import *

Creating Cards and Hole Cards
-----------------------------

Creating cards are very simple.

.. code-block:: python

   from pokertools import *

   # Create a card instance
   print(Card(Rank.FOUR, Suit.HEART))  # 4h
   print(Card(Rank('4'), Suit('h')))  # 4h
   print(parse_card('4h'))  # 4h

   # Create multiple card instances
   print(list(parse_cards('4h4s4cAs')))  # [4h, 4s, 4c, As]
   print(tuple(parse_cards('4h4s4cAs')))  # (4h, 4s, 4c, As)
   print(parse_range('AKo'))  # {frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), frozenset({Ks, Ac}), ...}
   print(parse_range('AKs'))  # {frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})}
   print(parse_range('AK'))  # {frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), frozenset({Kh, Ac}), ...}
   print(parse_range('AA'))  # {frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), frozenset({As, Ac}), ...}
   print(parse_range('QQ+'))  # {frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), frozenset({Qd, Qc}), ...}
   print(parse_range('QT+'))  # {frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), frozenset({Jh, Qc}), ...}
   print(parse_range('J5o+'))  # {frozenset({Jc, 5d}), frozenset({Jc, 5d}), frozenset({Jh, 7c}), frozenset({Js, 6d}), ...}
   print(parse_range('J5s+'))  # {frozenset({Jc, 5c}), frozenset({Jd, 5d}), frozenset({Jc, 6c}), frozenset({Jd, 6d}), ...}

   # Create hole cards
   print(HoleCard(True, parse_card('As')))  # As
   print(HoleCard(False, parse_card('As')))  # As
   print(str(HoleCard(False, parse_card('As'))))  # ??

   # Query cards
   print(suited(parse_cards('4h4s4cAs')))  # False
   print(suited(parse_cards('3s4sAs')))  # True
   print(rainbow(parse_cards('4h4s4cAs')))  # False
   print(rainbow(parse_cards('4c4d4hAs')))  # True

Using Decks
-----------

The following code demonstrates interacting with decks.

.. code-block:: python

   from pokertools import *

   deck = StandardDeck()  # Create a shuffled standard deck (52 cards)

   print(len(deck))  # 52
   print(parse_card('4h') in deck)  # True

   deck.draw(parse_cards('4h4s4cAs'))  # Draw the following cards from the deck

   print(len(deck))  # 48
   print(parse_card('4h') in deck)  # False

   deck.draw(5)  # Draw 5 cards from the deck (from the beginning of the deck)

   print(len(deck))  # 43
   print(deck)  # [Kd, 3c, Js, 2s, ...]

   deck = StandardDeck()  # Create a standard deck (52 cards)
   deck = ShortDeck()  # Create a short deck (36 cards)
   deck = Deck()  # Create an empty deck
   deck = Deck(parse_cards('AcAdAh'))  # Create a deck containing these three cards.

Only standard decks are used here. For more information, look at the PokerTools API documentations.

Evaluating Hands
----------------

The following code demonstrates interacting with evaluators. The evaluated hands are ordered so that stronger are
treated as being greater, and vice versa.

.. code-block:: python

   from pokertools import *

   evaluator = StandardEvaluator  # Used for Texas Hold'em, et cetera

   print(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKdKh'))
         < StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))  # True
   print(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKd'))
         < StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJs')))  # False

   evaluator = GreekEvaluator  # Used for Greek Hold'em
   evaluator = OmahaEvaluator  # Used for Omaha Hold'em
   evaluator = ShortDeckEvaluator  # Used for Short-Deck Hold'em, a.k.a. 6+ Hold'em
   evaluator = Lowball27Evaluator  # Used for Lowball 2-to-7 Draw
   evaluator = LowballA5Evaluator  # Used for Lowball A-to-5 Draw
   evaluator = BadugiEvaluator  # Used for Badugi
   evaluator = RankEvaluator  # Hands are compared by maximum ranks (used for Kuhn Poker)

Only standard evaluators are used here. For more information, you can look at the PokerTools API documentations.

Creating Pre-configured Poker Games
-----------------------------------

Creating poker games are very simple.

.. code-block:: python

   from pokertools import *

   ante = 1
   blinds = 1, 2
   starting_stacks = 200, 200, 300

   # Create a Fixed-Limit Texas Hold'em game
   flt = FixedLimitTexasHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a No-Limit Texas Hold'em game
   nlt = NoLimitTexasHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit Omaha Hold'em game
   plo = PotLimitOmahaHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Fixed-Limit 5-Card Omaha Hold'em game
   flfco = FixedLimitFiveCardOmahaHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit 5-Card Omaha Hold'em game
   plfco = PotLimitFiveCardOmahaHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit 6-Card Omaha Hold'em game
   plsco = PotLimitSixCardOmahaHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Fixed-Limit Greek Hold'em game
   flg = FixedLimitGreekHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit Greek Hold'em game
   plg = PotLimitGreekHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a No-Limit Greek Hold'em game
   nlg = NoLimitGreekHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a No-Limit Short-Deck Hold'em game
   nls = NoLimitShortDeckHoldEm(Stakes(ante, blinds), starting_stacks)

   # Create a Fixed-Limit 5-Card Draw game
   flfcd = FixedLimitFiveCardDraw(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit 5-Card Draw game
   plfcd = PotLimitFiveCardDraw(Stakes(ante, blinds), starting_stacks)

   # Create a No-Limit 5-Card Draw game
   nlfcd = NoLimitFiveCardDraw(Stakes(ante, blinds), starting_stacks)

   # Create a Fixed-Limit Badugi game
   flb = FixedLimitBadugi(Stakes(ante, blinds), starting_stacks)

   # Create a No-Limit 2-to-7 Single Draw Lowball game
   nlsdlb27 = NoLimitSingleDrawLowball27(Stakes(ante, blinds), starting_stacks)

   # Create a Fixed-Limit 2-to-7 Triple Draw Lowball game
   fltdlb27 = FixedLimitTripleDrawLowball27(Stakes(ante, blinds), starting_stacks)

   # Create a Pot-Limit 2-to-7 Triple Draw Lowball game
   pltdlb27 = PotLimitTripleDrawLowball27(Stakes(ante, blinds), starting_stacks)

   # Create a Kuhn Poker game
   kuhn = KuhnPoker()

Above are games preconfigured in PokerTools. They follow main-stream rules of poker. But if these default rules are not
desired, custom poker games can be created by putting different components together.

Customizing Poker Games
-----------------------

Two things are crucial when defining a poker game variant. The first is limit, which dictates the betting amounts
throughout the game. The second is the definition, which contains various rules throughout the game such as street and
betting structure.

Poker Limits
------------

Limits dictate the betting amounts in the game (min-bets, max-bets, and maximum number of bets and raises in a street).

Three limits are pre-configured in PokerTools. These are:

- Fixed-Limit
- Pot-Limit
- No-Limit

These can be imported as below.

.. code-block:: python

   from pokertools import *

   limit = FixedLimit
   limit = PotLimit
   limit = NoLimit

In PokerTools, Fixed limit caps the number of bets and raises to 4 per street. If this is unsatisfactory, you can
subclass the fixed limit class and override corresponding methods, as shown.

.. code-block:: python

   from pokertools import *

   class CustomFixedLimit(FixedLimit):
       @property
       def _max_count(self):
           return None  # Unlimited if None, otherwise the integral value

If you want to adjust min or max amounts of limit, you can just subclass the abstract base class for all limits.

.. code-block:: python

   from pokertools import *


   class CustomLimit(Limit):
       @property
       def _min_amount(self):
           return ...

       @property
       def _max_amount(self):
           return ...

       @property
       def _max_count(self):
           return ...

Poker Stages
------------

Stages are the most important parameters for poker games in PokerTools. It defines how the game behaves.

There are different types of stages in PokerTools.

- Hole-card dealing stage
- Board-card dealing stage
- Betting stage
- Discard-Draw stage
- Showdown stage

By creating stages in good order, you can define pretty much any game in Poker. Below are some examples of stages.

.. code-block:: python

   from pokertools import *


   def create_texas_hold_em_stages(game):  # Create Texas hold'em stages
       return (
           HoleDealingStage(False, 2, game), BettingStage(False, game),
           BoardDealingStage(3, game), BettingStage(False, game),
           BoardDealingStage(1, game), BettingStage(True, game),
           BoardDealingStage(1, game), BettingStage(True, game),
           ShowdownStage(game),
       )


   def create_triple_draw_stages(game):  # Create triple-draw stages
       return (
           HoleDealingStage(False, 5, game), BettingStage(False, game),
           DiscardDrawStage(game), BettingStage(False, game),
           DiscardDrawStage(game), BettingStage(True, game),
           DiscardDrawStage(game), BettingStage(True, game),
           ShowdownStage(game),
       )

You might see a catch-22 here. Note that constructing stages require games. But, game also needs stages to be defined.
The solution to this problem brings poker definition classes into the picture.

Poker Definitions
-----------------

You can think of definitions as the class that contains everything about poker rules. You supply an instance of this to
the constructor of the poker game. The game then will call definition's methods to create decks, evaluators, and, of
course, stages.

.. code-block:: python

   from pokertools import *


   class TexasHoldEmDefinition(Definition):
       def create_stages(self):
           return (
               HoleDealingStage(False, 2, self.game), BettingStage(False, self.game),
               BoardDealingStage(3, self.game), BettingStage(False, self.game),
               BoardDealingStage(1, self.game), BettingStage(True, self.game),
               BoardDealingStage(1, self.game), BettingStage(True, self.game),
               ShowdownStage(self.game),
           )

       def create_evaluators(self):
           return StandardEvaluator(),

       def create_deck(self):
           return StandardDeck()

Definition is just one variable of the constructor of poker games. Let's look at others.

Poker Stakes
------------

Stakes contain information about antes, blinds, small bets, and big bets. It is a very simple class.

.. code-block:: python

   from pokertools import *

   stakes = (  # Examples of stakes
       Stakes(0, (1, 2)),  # Ante: 0, Small blind: 1, Big Blind: 2
       Stakes(0, (1, 2, 4)),  # Same as above with straddle of 4
       Stakes(0, {5: 2}),  # Button blind of 2 in a 6-Max game
       Stakes(1, (2, 4)),  # Ante: 1, Small blind: 2, Big Blind: 4
       Stakes(1, (2, 4), small_bet=5),  # Same as above but with custom small-bet
       Stakes(1, (2, 4), small_bet=5, big_bet=15),  # Same as above but with custom big-bet
   )

Popular games only care about antes and blinds, so rest are not as relevant. Other forced bets such as straddles and
button blinds can be added to blinds. Small bets are min-bets in small-betting stages and big-betting stages (except
in Fixed-Limit games). Big-bets are only used as min-bets in big-betting stages in Fixed-limit games.

Constructing Custom Poker Games
-------------------------------

The above is more than enough to create custom poker games of your own. You just need to supply the game's limit,
definition, stakes, and starting stacks of the players.

.. code-block:: python

   from pokertools import *

   # 6-Max No-Limit Texas Hold'em
   nlt = PokerGame(NoLimit, TexasHoldEmDefinition, Stakes(1, (1, 2)), (200,) * 6)

   # Heads-Up Pot-Limit Omaha Hold'em
   plo = PokerGame(PotLimit, OmahaHoldEmDefinition, Stakes(0, (10, 20)), (2000, 3000))

Of course, PokerTools provide pre-configured poker games that allow simpler approach than the ones taken in the above
code.

Player Poker Games
------------------

The current game information can be queried by calling methods or accessing attributes.

Note that accessing or calling the below attributes or methods will not change the game state.

.. code-block:: python

   from pokertools import *

   game = NoLimitTexasHoldEm(Stakes(0, (1, 2)), (200, 200, 200))

   nature = game.nature
   player = game.players[0]

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

   # Parse game actions (explained later).
   game.parse('dh', 'dh')

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
   # True if the player can showdown while showing if necessary (same as above), else False.
   player.can_showdown(False)
   # True if the player can showdown while force showing, else False.
   player.can_showdown(True)
   # True if the player can stand pat, else False.
   player.can_discard_draw()
   # True if the player can discard the specified cards and draw random cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'))
   # True if the player can discard the specified cards and draw the specified cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))

The below demonstrates all possible actions that can be taken in PokerTools. Calling these methods will change the game
state.

.. code-block:: python

   from pokertools import *

   # Create a no-limit Texas Hold'em game
   game = NoLimitTexasHoldEm(0, (1, 2), (200, 200, 200))

   # Get the nature.
   nature = game.nature
   # Get the player
   player = game.players[0]

   # Deal random hole cards to the next player to be dealt
   nature.deal_hole()
   # Deal specified hole cards to the next player to be dealt
   nature.deal_hole(parse_cards('Ac2d'))
   # Deal random cards to the board
   nature.deal_board()
   # Deal specified cards to the board
   nature.deal_board(parse_cards('KsKcKh'))

   # Fold
   player.fold()
   # Check/call
   player.check_call()
   # Min-bet/raise
   player.bet_raise()
   # Bet/raise 30
   player.bet_raise(30)
   # Show hand if necessary to win the pot
   player.showdown()
   # Force muck cards and do not contend
   player.showdown(False)
   # Show hand even if the player loses anyway
   player.showdown(True)
   # Stand pat
   player.discard_draw()
   # Discard the specified cards and draw random cards
   player.discard_draw(parse_cards('KsKcKh'))
   # Discard the specified cards and draw the specified cards
   player.discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))
