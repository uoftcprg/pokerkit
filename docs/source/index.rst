.. pokerface documentation master file, created by
   sphinx-quickstart on Sat Mar  6 19:04:55 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PokerFace
=========

PokerFace is a Python package for various poker tools.

The following features are present in PokerFace...

- Types for cards and their components and related helper functions: :mod:`pokerface.cards`
   - Rank: :class:`pokerface.cards.Rank`
   - Suit: :class:`pokerface.cards.Suit`
   - Ranks: :class:`pokerface.cards.Ranks`
   - Card: :class:`pokerface.cards.Card`
   - Hole Card: :class:`pokerface.cards.HoleCard`
- Various types of poker decks: :mod:`pokerface.decks`
   - Standard Deck: :class:`pokerface.decks.StandardDeck`
   - Short Deck: :class:`pokerface.decks.ShortDeck`
- Poker hand evaluations: :mod:`pokerface.hands` and :mod:`pokerface.evaluators`
   - Standard Evaluator: :class:`pokerface.hands.StandardHand` and :class:`pokerface.evaluators.StandardEvaluator`
   - Greek Evaluator: :class:`pokerface.hands.StandardHand` and :class:`pokerface.evaluators.GreekEvaluator`
   - Omaha Evaluator: :class:`pokerface.hands.StandardHand` and :class:`pokerface.evaluators.OmahaEvaluator`
   - Short-Deck Evaluator: :class:`pokerface.hands.ShortDeckHand` and :class:`pokerface.evaluators.ShortDeckEvaluator`
   - Deuce-to-Seven Lowball Evaluator: :class:`pokerface.hands.Lowball27Hand` and :class:`pokerface.evaluators.Lowball27Evaluator`
   - Ace-to-Five Lowball Evaluator: :class:`pokerface.hands.LowballA5Hand` and :class:`pokerface.evaluators.LowballA5Evaluator`
   - Badugi Evaluator: :class:`pokerface.hands.BadugiHand` and :class:`pokerface.evaluators.BadugiEvaluator`
- Poker game variants: :mod:`pokerface.variants` and :mod:`pokerface.factories`
   - Texas Hold'em: :class:`pokerface.variants.TexasHoldEmVariant`
      - Fixed-Limit Texas Hold'em: :const:`pokerface.factories.FixedLimitTexasHoldEm`
      - No-Limit Texas Hold'em: :const:`pokerface.factories.NoLimitTexasHoldEm`
   - Omaha Hold'em: :class:`pokerface.variants.OmahaHoldEmVariant`
      - Pot-Limit Omaha Hold'em: :const:`pokerface.factories.PotLimitOmahaHoldEm`
   - 5-Card Omaha Hold'em: :class:`pokerface.variants.FiveCardOmahaHoldEmVariant`
      - Fixed-Limit 5-Card Omaha Hold'em: :const:`pokerface.factories.FixedLimitFiveCardOmahaHoldEm`
      - Pot-Limit 5-Card Omaha Hold'em: :const:`pokerface.factories.PotLimitFiveCardOmahaHoldEm`
   - 6-Card Omaha Hold'em: :class:`pokerface.variants.SixCardOmahaHoldEmVariant`
      - Pot-Limit 6-Card Omaha Hold'em: :const:`pokerface.factories.PotLimitSixCardOmahaHoldEm`
   - Greek Hold'em: :class:`pokerface.variants.GreekHoldEmVariant`
      - Fixed-Limit Greek Hold'em: :const:`pokerface.factories.FixedLimitGreekHoldEm`
      - Pot-Limit Greek Hold'em: :const:`pokerface.factories.PotLimitGreekHoldEm`
      - No-Limit Greek Hold'em: :const:`pokerface.factories.NoLimitGreekHoldEm`
   - Short-Deck Hold'em: :class:`pokerface.variants.ShortDeckHoldEmVariant`
      - No-Limit Short-Deck Hold'em: :const:`pokerface.factories.NoLimitShortDeckHoldEm`
   - 5-Card Draw: :class:`pokerface.variants.FiveCardDrawVariant`
      - Fixed-Limit 5-Card Draw: :const:`pokerface.factories.FixedLimitFiveCardDraw`
      - Pot-Limit 5-Card Draw: :const:`pokerface.factories.PotLimitFiveCardDraw`
      - No-Limit 5-Card Draw: :const:`pokerface.factories.NoLimitFiveCardDraw`
   - Badugi: :class:`pokerface.variants.BadugiVariant`
      - Fixed-Limit Badugi: :const:`pokerface.factories.FixedLimitBadugi`
   - 2-to-7 Single Draw Lowball: :class:`pokerface.variants.SingleDrawLowball27Variant`
      - No-Limit 2-to-7 Single Draw Lowball: :const:`pokerface.factories.NoLimitSingleDrawLowball27`
   - 2-to-7 Triple Draw Lowball: :class:`pokerface.variants.TripleDrawLowball27Variant`
      - Fixed-Limit 2-to-7 Triple Draw Lowball: :const:`pokerface.factories.FixedLimitTripleDrawLowball27`
      - Pot-Limit 2-to-7 Triple Draw Lowball: :const:`pokerface.factories.PotLimitTripleDrawLowball27`
   - Kuhn Poker: :class:`pokerface.variants.KuhnPokerVariant`
      - Fixed-Limit Kuhn Poker: :const:`pokerface.factories.KuhnPoker`

Speed
-----

Although PokerFace is entirely written in Python, it should be fast
enough for many tasks. Below table show the speeds of PokerFace and
treys (other popular framework) when evaluating all possible 5 card
combinations (2598960) as standard hands.

============  ================  ===================
  Framework    Total Time (s)    Speed (# hands/s)
------------  ----------------  -------------------
 PokerFace         ~40               ~65000
   treys            ~30               ~87000
============  ================  ===================

As seen, treys is a bit faster than PokerFace. However, PokerFace offer
a number of advantages over treys.

- Treys represent card as ints, but PokerFace represent them as an
  instance of Card type (more intuitive)
- PokerFace have more types of evaluators such as Omaha, Short-Deck, et
  cetera
- PokerFace offer range interpretation
- PokerFace provides seamless integration with PokerFace game logic

Contributing
------------

Current focuses of development are the following:

   - improve existing tools' speed
   - implement more types of poker variants
   - improve documentations

You can contribute on
`Github <https://github.com/AussieSeaweed/pokerface>`_.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   setup
   cards
   decks
   evaluations
   games
   samples
   customizations
   pokerface

License
-------

`GNU GPLv3 <https://choosealicense.com/licenses/gpl-3.0/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
