.. gameframe documentation master file, created by
   sphinx-quickstart on Sat Dec 26 10:33:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GameFrame
=========

GameFrame is a Python package for various game implementations.

The following games are supported in GameFrame...

- Poker
   - Hold'em
      - Texas Hold'em
         - Fixed-Limit Texas Hold'em
         - Pot-Limit Texas Hold'em
         - No-Limit Texas Hold'em
      - Omaha Hold'em
         - Fixed-Limit Omaha Hold'em
         - Pot-Limit Omaha Hold'em
         - No-Limit Omaha Hold'em
         - 5-Card Omaha Hold'em
            - Fixed-Limit 5-Card Omaha Hold'em
            - Pot-Limit 5-Card Omaha Hold'em
            - No-Limit 5-Card Omaha Hold'em
         - 6-Card Omaha Hold'em
            - Fixed-Limit 6-Card Omaha Hold'em
            - Pot-Limit 6-Card Omaha Hold'em
            - No-Limit 6-Card Omaha Hold'em
         - Courchevel
            - Fixed-Limit Courchevel
            - Pot-Limit Courchevel
            - No-Limit Courchevel
      - Greek Hold'em
         - Fixed-Limit Greek Hold'em
         - Pot-Limit Greek Hold'em
         - No-Limit Greek Hold'em
      - Short-Deck Hold'em
         - Fixed-Limit Short-Deck Hold'em
         - Pot-Limit Short-Deck Hold'em
         - No-Limit Short-Deck Hold'em
   - Draw
      - 5-Card Draw
         - Fixed-Limit 5-Card Draw
         - Pot-Limit 5-Card Draw
         - No-Limit 5-Card Draw
      - Badugi
         - Fixed-Limit Badugi
         - Pot-Limit Badugi
         - No-Limit Badugi
      - 2-to-7 Single Draw Lowball
         - Fixed-Limit 2-to-7 Single Draw Lowball
         - Pot-Limit 2-to-7 Single Draw Lowball
         - No-Limit 2-to-7 Single Draw Lowball
      - 2-to-7 Triple Draw Lowball
         - Fixed-Limit 2-to-7 Triple Draw Lowball
         - Pot-Limit 2-to-7 Triple Draw Lowball
         - No-Limit 2-to-7 Triple Draw Lowball
   - Kuhn Poker
- Tic Tac Toe
- Rock Paper Scissors


Speed
-----

Although GameFrame is entirely written in Python, it should be fast enough for many tasks.

=================================  ===================
              Game                  Speed (# games/s)
---------------------------------  -------------------
 6-Max No-Limit Texas Hold'em             ~500
 6-Max No-Limit Greek Hold'em             ~300
 6-Max No-Limit Omaha Hold'em             ~100
 Heads-Up No-Limit Texas Hold'em          ~2000
 Heads-Up No-Limit Greek Hold'em          ~1500
 Heads-Up No-Limit Omaha Hold'em          ~500
 Kuhn Poker                               ~5000
 Tic Tac Toe                              ~10000
 Rock Paper Scissors                      ~100000
=================================  ===================


Contributing
------------

Current focuses of development are the following:
   - improve existing games' speed
   - implement more types of games
   - improve documentations

You can contribute on `Github <https://github.com/AussieSeaweed/gameframe>`_.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   install
   create
   interact
   gameframe


License
-------
`GNU GPLv3 <https://choosealicense.com/licenses/gpl-3.0/>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
