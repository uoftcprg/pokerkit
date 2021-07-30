Evaluating Hands
================

Poker hand evaluations involve two modules in PokerTools:

- Hands module: :mod:`pokertools.hands`
- Evaluators module: :mod:`pokertools.evaluators`

Both can be used to evaluate hands, but each should be used for
different purposes.

The :mod:`pokertools.hands` module contain data types (subclasses of
:class:`pokertools.hands.Hand`) that contain
information about a hand and its rank and order with respect to other
hands. The instances of these are then compared with each other to see
which hand prevails.

The evaluators, defined in :mod:`pokertools.evaluators`, are all of type
:class:`pokertools.evaluators.Evaluator`. Evaluators iterate through all
possible hand combinations from the passed cards and pick out the best
hand by comparing them to other combinations. Thus, the return value is
an instance of :class:`pokertools.hands.Hand`.

Using Hands
-----------

Hands receive information about cards inside the hand during its
construction. Their usage is quite simple.

.. code-block:: python

   from pokertools import *

   # Create some hands.
   x = StandardHand(parse_cards('AcAdAhAsKc'))
   y = StandardHand(parse_cards('QsJsTs9s8s'))

   print(x == y)  # False
   print(x < y)  # True
   print(x <= y)  # True
   print(x > y)  # False
   print(x >= y)  # False

The evaluated hands are ordered so that stronger hands are treated as
being greater, and vice versa.

Only standard hands are shown above, but there are other types of hands:

- Standard Hand: :class:`pokertools.hands.StandardHand`
   - Used in Texas Hold'em, Greek Hold'em, Omaha Hold'em, et cetera
   - Consists of 5 cards
- Short-Deck Hand: :class:`pokertools.hands.ShortDeckHand`
   - Used in Short-deck Hold'em
   - Consists of 5 cards
- Deuce-to-Seven Lowball Hand: :class:`pokertools.hands.Lowball27Hand`
   - Used in Deuce-to-Seven Lowball
   - Consists of 5 cards
- Ace-to-Five Lowball Hand: :class:`pokertools.hands.LowballA5Hand`
   - Used in Ace-to-Five Lowball
   - Consists of 5 cards
- Badugi Hand: :class:`pokertools.hands.BadugiHand`
   - Used in Badugi
   - Consists of 4, 3, 2, or 1 cards

Note that only the cards that form a valid hand can be passed into the
constructor, or else, a ``ValueError`` will be
raised.

But, sometimes, you need to evaluate hands by finding the best hand
combination among 7 cards or by combining hole cards and board cards.
Evaluators are used for the aforesaid purpose not covered by the hands.

Using Evaluators
----------------

Evaluators offer the :meth:`pokertools.evaluators.Evaluator.evaluate`
method for hand evaluations. The method requires 2 arguments to be
passed -- the hole cards of the player and the board cards of the game.

.. code-block:: python

   from pokertools import *

   # Create a standard evaluator which is used for games such as Texas Hold'em, et cetera.
   evaluator = StandardEvaluator()

   # Evaluate hands.
   x = evaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKdKh'))
   y = evaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJsTs'))

   print(x < y)  # True

   # Evaluate hands.
   x = evaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKd'))
   y = evaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJs'))

   print(x < y)  # False

If you just have a group of cards and do not care whether they belong in
the hole or the board, you can just call the method as below.

.. code-block:: python

   from pokertools import *

   hand = StandardEvaluator.evaluate(parse_cards('AcKsAhAsQsJsTs'), ())

The :meth:`pokertools.evaluators.Evaluator.evaluate` method is actually
a class method, so you can directly call the method from the class
itself without creating an evaluator instance.

The above work-around does not work for some types of evaluators like
Greek or Omaha evaluators, as the separation between the hole cards and
the board cards actually matter in their hand evaluations.

All evaluator types are listed below:

- Standard Evaluator: :class:`pokertools.evaluators.StandardEvaluator`
- Greek Evaluator: :class:`pokertools.evaluators.GreekEvaluator`
- Omaha Evaluator: :class:`pokertools.evaluators.OmahaEvaluator`
- Short-Deck Evaluator: :class:`pokertools.evaluators.ShortDeckEvaluator`
- Deuce-to-Seven Lowball Evaluator: :class:`pokertools.evaluators.Lowball27Evaluator`
- Ace-to-Five Lowball Evaluator: :class:`pokertools.evaluators.LowballA5Evaluator`
- Badugi Evaluator: :class:`pokertools.evaluators.BadugiEvaluator`
- Rank Evaluator: :class:`pokertools.evaluators.RankEvaluator`

Custom Hand Evaluations
-----------------------

Customized hand evaluations are explained in the later section.
