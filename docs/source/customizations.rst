Customizing Poker Games
=======================

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
