Hand Evaluation
===============

Not every poker software involves game simulations. Beyond its use of providing a simulated poker environment, PokerKit serves as a valuable resource for evaluating poker hands. It supports the largest selection of hand types in any mainstream open-source poker library. This makes it an invaluable tool for users interested in studying the statistical properties of poker, regardless of their interest in game simulations.

Our `PokerKit paper <https://doi.org/10.1109/TG.2023.3325637>`__ gives a general overview of our library that summarizes the content of this page and the detailed benchmarks.

The following is the list of hand types supported by PokerKit.

- Badugi hands: :class:`pokerkit.hands.BadugiHand`
- 8 or better low hands: :class:`pokerkit.hands.EightOrBetterLowHand`

  - Used in: seven card stud hi/lo 8-or-better

- Greek hold'em hands: :class:`pokerkit.hands.GreekHoldemHand`
- Kuhn poker hands: :class:`pokerkit.hands.KuhnPokerHand`
- Omaha 8 or better low hands: :class:`pokerkit.hands.OmahaEightOrBetterLowHand`

  - Used in: Omaha Hi/Lo 8-or-better

- Omaha hold'em hands: :class:`pokerkit.hands.OmahaHoldemHand`
- Regular low hands: :class:`pokerkit.hands.RegularLowHand`

  - Used in: seven card stud hi/lo regular, razz

- Short-deck hold'em hands: :class:`pokerkit.hands.ShortDeckHoldemHand`
- Standard high hands: :class:`pokerkit.hands.StandardHighHand`

  - Used in: Texas hold'em

- Standard low hands: :class:`pokerkit.hands.StandardLowHand`

  - Used in: deuce-to-seven draw

When a hand name contains the term ``low``, it means it is a low hand. Lots of these types have the same base lookup. They just differ in the way the hands are evaluated. For example, standard high hands and Omaha hold'em hands use the same lookup.

Our hand evaluators are optimized for speed while giving a convenient high-level interface.

Creating Hands
--------------

There are two ways of creating hands. They are both very straightforward.

The first method is simply by giving the cards that make up a hand.

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

The second method is useful in game scenarios where you put in the user's hole cards and the board cards (maybe empty).

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

Let us define what the "strength" of a hand means. The strength decides who wins the pot and who loses the pot. Realize that stronger or weaker hands do not necessarily always mean higher or lower hands. For instance, in some variants, lower hands are considered stronger, and vice versa.

PokerKit's hand comparison interface allows hand strengths to be compared using standard comparison operators.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> h0 = StandardHighHand('7c5d4h3s2c')
   >>> h1 = StandardHighHand('7c6d4h3s2c')
   >>> h2 = StandardHighHand('8c7d6h4s2c')
   >>> h3 = StandardHighHand('AcAsAd2s4s')
   >>> h4 = StandardHighHand('TsJsQsKsAs')
   >>> h0 < h1 < h2 < h3 < h4
   True

.. code-block:: pycon

   >>> from pokerkit import *
   >>> h0 = StandardLowHand('TsJsQsKsAs')
   >>> h1 = StandardLowHand('AcAsAd2s4s')
   >>> h2 = StandardLowHand('8c7d6h4s2c')
   >>> h3 = StandardLowHand('7c6d4h3s2c')
   >>> h4 = StandardLowHand('7c5d4h3s2c')
   >>> h0 < h1 < h2 < h3 < h4
   True

Custom Hands
------------

The library generates a lookup table for each hand type. The hands are generated in the order or reverse order of strength and assigned indices, which are used to compare hands. High-level interfaces allow users to construct hands by passing in the necessary cards and using standard comparison operators to compare the hand strengths. Each hand type in PokerKit handles this distinction internally, making it transparent to the end user.

If the user wishes to define custom hand types, they can leverage existing lookups or create an entirely new lookup table from which hand types are derived. :mod:`pokerkit.lookups` and :mod:`pokerkit.hands` contain plenty of examples of this that the user can take inspiration from.

Algorithm
---------

In the lookup construction process, cards are converted into unique integers that represent their ranks. Each rank corresponds to a unique prime number and the converted integers are multiplied together. The suitedness of the cards is then checked.  Using the product and the suitedness, the library looks for the matching hand entries which are then used to compare hands.

This approach was used by the ``deuces`` and ``treys`` hand evaluation libraries.

Speeds
------

Our library is extremely fast and performs in the same magnitude as ``deuces`` or ``treys``. But, they are a bit faster than our library. This is an inevitable consequence of having a generalized high-level interface for evaluating hands. If speed is paramount, the user is recommended to explore various C++ solutions such as ``OMPEval``.
