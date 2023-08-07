Hand Evaluation
===============

Not every poker software involve game simulations. If you just want to
evaluate poker hands, we provide facilities to do so. As we support a wide
selection of games, we also support a wide selection of hand types.

- Badugi hands: :class:`pokerkit.hands.BadugiHand`
- 8 or better low hands: :class:`pokerkit.hands.EightOrBetterLowHand`
- Greek hold'em hands: :class:`pokerkit.hands.GreekHoldemHand`
- Kuhn poker hands: :class:`pokerkit.hands.KuhnPokerHand`
- Omaha 8 or better low hands: :class:`pokerkit.hands.OmahaEightOrBetterLowHand`
- Omaha hold'em hands: :class:`pokerkit.hands.OmahaHoldemHand`
- Regular low hands: :class:`pokerkit.hands.RegularLowHand`
- Short-deck hold'em hands: :class:`pokerkit.hands.ShortDeckHoldemHand`
- Standard high hands: :class:`pokerkit.hands.StandardHighHand`
- Standard low hands: :class:`pokerkit.hands.StandardLowHand`

Standard high hands are used for games like Texas hold'em. When something
contains ``low`` it means it is a low hand. Lots of these types have the same
base lookup. They just differ in the way the hands are evaluated.  For example,
Standard high hands and Omaha hold'em hands uses the same lookup.

Our hand evaluators are optimized for speed while giving a convenient high
level interface.

Creating Hands
--------------

There are two ways of creating hands. They are both very straight forward.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> h0 = ShortDeckHoldemHand('6s7s8s9sTs')
   >>> h1 = ShortDeckHoldemHand('7c8c9cTcJc')
   >>> h2 = ShortDeckHoldemHand('2c2d2h2s3h')
   Traceback (most recent call last):
       ...
   ValueError: invalid hand '2c2d2h2s3h'
   >>> h0
   6s7s8s9sTs
   >>> h1
   7c8c9cTcJc

What if you want to evaluate hands from a game setting? No problem.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> h0 = OmahaHoldemHand.from_game('6c7c8c9c', '8s9sTc')
   >>> h1 = OmahaHoldemHand('6c7c8s9sTc')
   >>> h0 == h1
   True
   >>> h0 = OmahaEightOrBetterLowHand.from_game('As2s3s4s', '2c3c4c5c6c')
   >>> h1 = OmahaEightOrBetterLowHand('Ad2d3d4d5d')
   >>> h0 == h1
   True
   >>> hole = 'AsAc'
   >>> board = 'Kh3sAdAh'
   >>> hand = StandardHighHand.from_game(hole, board)
   >>> hand.cards
   (As, Ac, Kh, Ad, Ah)

Comparing Hands
---------------

First, let us realize that stronger or weaker hands do not necessarily always
mean higher or lower hands. In some variants, lower hands are considered
stronger, and vice versa.

Comparing the hand strengths is quite simple... Just compare them!

.. code-block:: pycon

   >>> h0 = StandardHighHand('7c5d4h3s2c')
   >>> h1 = StandardHighHand('7c6d4h3s2c')
   >>> h2 = StandardHighHand('8c7d6h4s2c')
   >>> h3 = StandardHighHand('AcAsAd2s4s')
   >>> h4 = StandardHighHand('TsJsQsKsAs')
   >>> h0 < h1 < h2 < h3 < h4
   True
   >>> h0 = StandardLowHand('TsJsQsKsAs')
   >>> h1 = StandardLowHand('AcAsAd2s4s')
   >>> h2 = StandardLowHand('8c7d6h4s2c')
   >>> h3 = StandardLowHand('7c6d4h3s2c')
   >>> h4 = StandardLowHand('7c5d4h3s2c')
   >>> h0 < h1 < h2 < h3 < h4
   True
