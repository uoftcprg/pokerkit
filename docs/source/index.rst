.. pokertools documentation master file, created by
sphinx-quickstart on Sat Mar  6 19:04:55 2021.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive.

PokerTools
==========

PokerTools is a Python package for various poker tools.

The following features are present in PokerTools...

- Basic rank, suit, card, and hole card data types
- String interpretation of cards
- Various types of poker decks
   - Standard
   - Short
- Various types of poker evaluators
   - Standard
   - Greek
   - Omaha
   - Short-Deck
   - Lowball
      - Ace-to-Five
      - Deuce-to-Seven
- Range parsing (AKo, T6s, 66, KQ, AsKc, ...)


Speed
-----

Although PokerTools is entirely written in Python, it should be fast enough for many tasks. Below table show the speeds
of PokerTools and treys (other popular framework) when evaluating all possible 5 card combinations (2598960) as standard
hands.

============  ================  ===================
  Framework    Total Time (s)    Speed (# hands/s)
------------  ----------------  -------------------
 PokerTools         ~70               ~37000
   treys            ~30               ~87000
============  ================  ===================

As seen, treys is more than 2 times faster than PokerTools. However, PokerTools offer a number of advantages over treys.

- Treys represent card as ints, but PokerTools represent them as an instance of Card type (more intuitive)
- PokerTools have more types of evaluators (incl. Omaha, Short-Deck, etc.)
- PokerTools offer range interpretation
- PokerTools is completely typed


Contributing
------------

Current focuses of development are the following:
   - improve existing tools' speed
   - implement more types of evaluators
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
`MIT <https://choosealicense.com/licenses/mit/>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
