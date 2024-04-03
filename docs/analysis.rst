Statistical Analysis
====================

PokerKit contains tools for various poker statistical analysis methods, compatible with any variant.

Range Parsing
-------------

PokerKit can parse common range notations to come up with set of hole card combinations.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> parse_range('AKs')
   {frozenset({As, Ks}), frozenset({Kd, Ad}), frozenset({Kh, Ah}), frozenset({Ac, Kc})}
   >>> parse_range('22')
   {frozenset({2s, 2d}), frozenset({2d, 2h}), frozenset({2c, 2d}), frozenset({2s, 2h}), frozenset({2c, 2s}), frozenset({2c, 2h})}
   >>> parse_range('T9o') | parse_range('T9s') == parse_range('T9')
   True
   >>> parse_range('33', '44;55') == parse_range('33-55')
   True
   >>> parse_range('T9s') | parse_range('JTs') | parse_range('QJs') == parse_range('T9s-QJs')
   True
   >>> parse_range('T9s-QJs') | parse_range('T9o-QJo') == parse_range('T9-QJ')
   True
   >>> parse_range('J8s,J9s JTs') == parse_range('J8s+')
   True
   >>> parse_range('T9') - parse_range('T9s') == parse_range('T9o')
   True
   >>> parse_range('AdAh') < parse_range('AA')
   True

The notations can be separated either by whitespace(s), comma(s) (``,``), and/or semicolon(s) (``;``). In PokerKit, a range is simply a set of frozen sets of cards and thus can be manipulated through set operations.

Equity Calculations
-------------------

Monte Carlo simulations can be carried out to estimate player equities. The hole cards (if any), board cards (if any), total number of hole dealings (including those already dealt), total number of board dealings (including those already dealt), deck (including those already dealt), hand types (multiple if split-pot) must be supplied. The user must also supply the number of samples to use. Concurrency mechanisms can be leveraged by passing relevant executor to the equity calculator. Below show some equity calculations in Texas hold'em.

.. code-block:: pycon

   >>> from concurrent.futures import ProcessPoolExecutor
   >>> from pokerkit import *
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_equities(
   ...         (
   ...             parse_range('AK'),
   ...             parse_range('22'),
   ...         ),
   ...         (),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=10000,
   ...         executor=executor,
   ...     )
   ... 
   [0.4807, 0.5193]
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_equities(
   ...         (
   ...             parse_range('AsKs'),
   ...             parse_range('AcJc'),
   ...         ),
   ...         Card.parse('Js8s5d'),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=1000,
   ...         executor=executor,
   ...     )
   ... 
   [0.485, 0.515]
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_equities(
   ...         (
   ...             parse_range('2h2c'),
   ...             parse_range('3h3c'),
   ...             parse_range('AsKs'),
   ...         ),
   ...         Card.parse('QsJsTs'),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=1000,
   ...         executor=executor,
   ...     )
   ...
   [0.0, 0.0, 1.0]
   >>> calculate_equities(
   ...     (
   ...         parse_range('33'),
   ...         parse_range('33'),
   ...     ),
   ...     Card.parse('Tc8d6h4s'),
   ...     2,
   ...     5,
   ...     Deck.STANDARD,
   ...     (StandardHighHand,),
   ...     sample_count=1000,
   ... )
   [0.5, 0.5]

Hand Strength Calculations
--------------------------

Monte Carlo simulations can be carried out to estimate hand strengths: the odds of beating a single other hand chosen uniformly at random. Just like in equity calculations, the number of active players, hole cards, board cards (if any), total number of hole dealings (including those already dealt), total number of board dealings (including those already dealt), deck (including those already dealt), hand types (multiple if split-pot) must be supplied. The user must also supply the number of samples to use. Concurrency mechanisms can be leveraged by passing relevant executor to the equity calculator.

.. code-block:: pycon

   >>> from concurrent.futures import ProcessPoolExecutor
   >>> from pokerkit import *
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_hand_strength(
   ...         2,
   ...         parse_range('AsKs'),
   ...         Card.parse('Kc8h8d'),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=1000,
   ...         executor=executor,
   ...     )
   ... 
   0.885
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_hand_strength(
   ...         3,
   ...         parse_range('AsKs'),
   ...         Card.parse('QsJsTs'),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=1000,
   ...         executor=executor,
   ...     )
   ...
   1.0
   >>> calculate_hand_strength(
   ...     3,
   ...     parse_range('3h3c'),
   ...     Card.parse('3s3d2c'),
   ...     2,
   ...     5,
   ...     Deck.STANDARD,
   ...     (StandardHighHand,),
   ...     sample_count=1000,
   ... )
   1.0

Player Statistics
-----------------

Hand histories can be analyzed through PokerKit. Information for each player is aggregated and can be accessed as attributes or properties.

.. code-block:: python

   from pokerkit import *

   hh0 = ...
   hh1 = ...
   hh2 = ...
   ...

   ss = Statistics.from_hand_history(hh0, hh1, hh2, ...)

   print(ss['John Smith'].payoff_mean)
   print(ss['John Smith'].payoff_stdev)
   print(ss['Jane Doe'].payoff_mean)
   print(ss['Jane Doe'].payoff_stdev)

Statistics can be merged.

.. code-block:: python

   from pokerkit import *

   s0 = ...
   s1 = ...
   s2 = ...
   ...

   s = Statistics.merge(s0, s1, s2, ...)

For a full list of accessible statistics, please see the API references for the class :class:`pokerkit.analysis.Statistics`.
