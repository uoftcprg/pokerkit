.. pokertools documentation master file, created by
   sphinx-quickstart on Sat Mar  6 19:04:55 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PokerTools
==========

PokerTools is a Python package for various poker tools.

The following features are present in PokerTools...

- Basic rank, suit, card, and hole card data types
- Various types of poker decks
   - Standard
   - Short-Deck
- Various types of poker evaluators
   - Standard
   - Greek
   - Omaha
   - Short-Deck
   - Badugi
   - Ace-to-Five Lowball
   - Deuce-to-Seven Lowball
- Range parsing (AKo, T6s, 66, KQ, AsKc, ...)
- Various poker game variants
   - Texas Hold'em
      - Fixed-Limit Texas Hold'em
      - No-Limit Texas Hold'em
   - Omaha Hold'em
      - Pot-Limit Omaha Hold'em
   - 5-Card Omaha Hold'em
      - Fixed-Limit 5-Card Omaha Hold'em
      - Pot-Limit 5-Card Omaha Hold'em
   - 6-Card Omaha Hold'em
      - Pot-Limit 6-Card Omaha Hold'em
   - Greek Hold'em
      - Fixed-Limit Greek Hold'em
      - Pot-Limit Greek Hold'em
      - No-Limit Greek Hold'em
   - Short-Deck Hold'em
      - No-Limit Short-Deck Hold'em
   - 5-Card Draw
      - Fixed-Limit 5-Card Draw
      - Pot-Limit 5-Card Draw
      - No-Limit 5-Card Draw
   - Badugi
      - Fixed-Limit Badugi
   - 2-to-7 Single Draw Lowball
      - No-Limit 2-to-7 Single Draw Lowball
   - 2-to-7 Triple Draw Lowball
      - Fixed-Limit 2-to-7 Triple Draw Lowball
      - Pot-Limit 2-to-7 Triple Draw Lowball
   - Kuhn Poker
      - Fixed-Limit Kuhn Poker

Speed
-----

Although PokerTools is entirely written in Python, it should be fast enough for many tasks. Below table show the speeds
of PokerTools and treys (other popular framework) when evaluating all possible 5 card combinations (2598960) as standard
hands.

============  ================  ===================
  Framework    Total Time (s)    Speed (# hands/s)
------------  ----------------  -------------------
 PokerTools         ~40               ~65000
   treys            ~30               ~87000
============  ================  ===================

As seen, treys is a bit faster than PokerTools. However, PokerTools offer a number of advantages over treys.

- Treys represent card as ints, but PokerTools represent them as an instance of Card type (more intuitive)
- PokerTools have more types of evaluators such as Omaha, Short-Deck, et cetera
- PokerTools offer range interpretation
- Seamless integration with PokerTools game logic

Contributing
------------

Current focuses of development are the following:
   - improve existing tools' speed
   - implement more types of games
   - improve documentations

You can contribute on `Github <https://github.com/AussieSeaweed/pokertools>`_.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   install
   interact
   pokertools

License
-------

`GNU GPLv3 <https://choosealicense.com/licenses/gpl-3.0/>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
