.. pokertools documentation master file, created by
   sphinx-quickstart on Sat Mar  6 19:04:55 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PokerTools
==========

PokerTools is a Python package for various poker tools.

The following features are present in PokerTools...

- Types for cards and their components and related helper functions: :mod:`pokertools.cards`
   - Rank: :class:`pokertools.cards.Rank`
   - Suit: :class:`pokertools.cards.Suit`
   - Ranks: :class:`pokertools.cards.Ranks`
   - Card: :class:`pokertools.cards.Card`
   - Hole Card: :class:`pokertools.cards.HoleCard`
- Various types of poker decks: :mod:`pokertools.decks`
   - Standard Deck: :class:`pokertools.decks.StandardDeck`
   - Short Deck: :class:`pokertools.decks.ShortDeck`
- Poker hand evaluations: :mod:`pokertools.hands` and :mod:`pokertools.evaluators`
   - Standard Evaluator: :class:`pokertools.hands.StandardHand` and :class:`pokertools.evaluators.StandardEvaluator`
   - Greek Evaluator: :class:`pokertools.hands.StandardHand` and :class:`pokertools.evaluators.GreekEvaluator`
   - Omaha Evaluator: :class:`pokertools.hands.StandardHand` and :class:`pokertools.evaluators.OmahaEvaluator`
   - Short-Deck Evaluator: :class:`pokertools.hands.ShortDeckHand` and :class:`pokertools.evaluators.ShortDeckEvaluator`
   - Deuce-to-Seven Lowball Evaluator: :class:`pokertools.hands.Lowball27Hand` and :class:`pokertools.evaluators.Lowball27Evaluator`
   - Ace-to-Five Lowball Evaluator: :class:`pokertools.hands.LowballA5Hand` and :class:`pokertools.evaluators.LowballA5Evaluator`
   - Badugi Evaluator: :class:`pokertools.hands.BadugiHand` and :class:`pokertools.evaluators.BadugiEvaluator`
- Poker game variants: :mod:`pokertools.variants` and :mod:`pokertools.factories`
   - Texas Hold'em: :class:`pokertools.variants.TexasHoldEmVariant`
      - Fixed-Limit Texas Hold'em: :const:`pokertools.factories.FixedLimitTexasHoldEm`
      - No-Limit Texas Hold'em: :const:`pokertools.factories.NoLimitTexasHoldEm`
   - Omaha Hold'em: :class:`pokertools.variants.OmahaHoldEmVariant`
      - Pot-Limit Omaha Hold'em: :const:`pokertools.factories.PotLimitOmahaHoldEm`
   - 5-Card Omaha Hold'em: :class:`pokertools.variants.FiveCardOmahaHoldEmVariant`
      - Fixed-Limit 5-Card Omaha Hold'em: :const:`pokertools.factories.FixedLimitFiveCardOmahaHoldEm`
      - Pot-Limit 5-Card Omaha Hold'em: :const:`pokertools.factories.PotLimitFiveCardOmahaHoldEm`
   - 6-Card Omaha Hold'em: :class:`pokertools.variants.SixCardOmahaHoldEmVariant`
      - Pot-Limit 6-Card Omaha Hold'em: :const:`pokertools.factories.PotLimitSixCardOmahaHoldEm`
   - Greek Hold'em: :class:`pokertools.variants.GreekHoldEmVariant`
      - Fixed-Limit Greek Hold'em: :const:`pokertools.factories.FixedLimitGreekHoldEm`
      - Pot-Limit Greek Hold'em: :const:`pokertools.factories.PotLimitGreekHoldEm`
      - No-Limit Greek Hold'em: :const:`pokertools.factories.NoLimitGreekHoldEm`
   - Short-Deck Hold'em: :class:`pokertools.variants.ShortDeckHoldEmVariant`
      - No-Limit Short-Deck Hold'em: :const:`pokertools.factories.NoLimitShortDeckHoldEm`
   - 5-Card Draw: :class:`pokertools.variants.FiveCardDrawVariant`
      - Fixed-Limit 5-Card Draw: :const:`pokertools.factories.FixedLimitFiveCardDraw`
      - Pot-Limit 5-Card Draw: :const:`pokertools.factories.PotLimitFiveCardDraw`
      - No-Limit 5-Card Draw: :const:`pokertools.factories.NoLimitFiveCardDraw`
   - Badugi: :class:`pokertools.variants.BadugiVariant`
      - Fixed-Limit Badugi: :const:`pokertools.factories.FixedLimitBadugi`
   - 2-to-7 Single Draw Lowball: :class:`pokertools.variants.SingleDrawLowball27Variant`
      - No-Limit 2-to-7 Single Draw Lowball: :const:`pokertools.factories.NoLimitSingleDrawLowball27`
   - 2-to-7 Triple Draw Lowball: :class:`pokertools.variants.TripleDrawLowball27Variant`
      - Fixed-Limit 2-to-7 Triple Draw Lowball: :const:`pokertools.factories.FixedLimitTripleDrawLowball27`
      - Pot-Limit 2-to-7 Triple Draw Lowball: :const:`pokertools.factories.PotLimitTripleDrawLowball27`
   - Kuhn Poker: :class:`pokertools.variants.KuhnPokerVariant`
      - Fixed-Limit Kuhn Poker: :const:`pokertools.factories.KuhnPoker`

Speed
-----

Although PokerTools is entirely written in Python, it should be fast
enough for many tasks. Below table show the speeds of PokerTools and
treys (other popular framework) when evaluating all possible 5 card
combinations (2598960) as standard hands.

============  ================  ===================
  Framework    Total Time (s)    Speed (# hands/s)
------------  ----------------  -------------------
 PokerTools         ~40               ~65000
   treys            ~30               ~87000
============  ================  ===================

As seen, treys is a bit faster than PokerTools. However, PokerTools
offer a number of advantages over treys.

- Treys represent card as ints, but PokerTools represent them as an
  instance of Card type (more intuitive)
- PokerTools have more types of evaluators such as Omaha, Short-Deck, et
  cetera
- PokerTools offer range interpretation
- PokerTools provides seamless integration with PokerTools game logic

Contributing
------------

Current focuses of development are the following:

   - improve existing tools' speed
   - implement more types of poker variants
   - improve documentations

You can contribute on
`Github <https://github.com/AussieSeaweed/pokertools>`_.

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
   pokertools

License
-------

`GNU GPLv3 <https://choosealicense.com/licenses/gpl-3.0/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
