Hand History
============

PokerKit can save and load hands. The hand is written in .toml compatible format with an extension: .phh

Below is a general overview of the fields in poker hand history file formats. For more details and requirements, refer to the `Poker Hand History File Format Specification <https://doi.org/10.48550/arXiv.2312.11753>`__.

Required fields:

- ``variant``: The game code, string.

  - ``FT``: Fixed-limit Texas hold'em.
  - ``NT``: No-limit Texas hold'em.
  - ``NS``: No-limit short-deck hold'em.
  - ``PO``: Pot-limit Omaha hold'em.
  - ``FO/8``: Fixed-limit Omaha hold'em high/low-split eight or better.
  - ``F7S``: Fixed-limit seven card stud.
  - ``F7S/8``: Fixed-limit seven card stud high/low-split eight or better.
  - ``FR``: Fixed-limit razz.
  - ``N2L1D``: No-limit deuce-to-seven lowball single draw.
  - ``F2L3D``: Fixed-limit deuce-to-seven lowball triple draw.
  - ``FB``: Fixed-limit badugi.

- ``antes``: The antes, array of non-negative integers or floats.
- ``blinds_or_straddles``: The blinds or straddles (some variants), an array of non-negative integers or floats.
- ``bring_in``: The bring-in (some variants), positive integer or float.
- ``small_bet``: The small bet (some variants), positive integer or float.
- ``big_bet``: The big bet (some variants), positive integer or float.
- ``min_bet``: The minimum bet (some variants), positive integer or float.
- ``starting_stacks``: The starting stacks, an array of positive integers or floats.
- ``actions``: The actions where dealer is ``d`` and n'th player is ``pn``, array of strings.

  - ``<actor> <action>[ <argument-1>, ...][ # commentary...]
  - ``d db <cards>``: deal board cards.
  - ``d dh <player> <cards>``: deal hole cards.
  - ``<player> sd[ <cards>]``: stand pat or discard.
  - ``<player> pb``: post bring-in.
  - ``<player> f``: fold.
  - ``<player> cc``: check or call.
  - ``<player> cbr <amount>``: complete, bet, or raise to an amount.
  - ``<player> sm[ <cards>]``: show or muck hole cards.
  - ``<player> sm -``: show hole cards.

Optional fields:

- ``author``: The author, string (First name last name).
- ``event``: The event, string.
- ``url``: The url, string.
- ``address``: The address, string.
- ``city``: The city, string.
- ``region``: The region, string.
- ``postal_code``: The postal code, string.
- ``country``: The country, string
- ``time``: The time, local time.
- ``time_zone``: The time zone, string.
- ``day``: The day, integer.
- ``month``: The month, integer.
- ``year``: The year, integer.
- ``hand``: The hand number, integer.
- ``level``: The level number, integer.
- ``seats``: The seat numbers, an array of integers or floats.
- ``seat_count``: The number of seats, integer.
- ``table``: The table number, integer.
- ``players``: The player names, an array of strings (First name last name).
- ``finishing_stacks``: The finishing stacks, an array of non-negative integers or floats.
- ``currency``: The currency, string (ISO 4127).
- ``ante_trimming_status``: How to handle unequal ante contributions, Boolean.
- ``time_limit``: The time limit, integer, or float.
- ``time_banks``: The time banks, an array of integers or floats.

Examples
--------

Over 10,000 example hand histories from sources ranging from Pluribus's gameplay, 2023 WSOP Event #43: $50,000 Poker Players Championship | Day 5, and other various historical hands are in the `PokerKit GitHub repository <https://github.com/uoftcprg/pokerkit>`__. They cover 11 poker variants. One of the historical hands, played by Dwan and Ivey is shown below:

.. code-block:: toml

   # The first televised million-dollar pot between Tom Dwan and Phil Ivey.
   # Link: https://youtu.be/GnxFohpljqM
   
   variant = "NT"
   ante_trimming_status = true
   antes = [500, 500, 500]
   blinds_or_straddles = [1000, 2000, 0]
   min_bet = 2000
   starting_stacks = [1125600, 2000000, 553500]
   actions = [
     # Pre-flop
   
     "d dh p1 Ac2d",  # Ivey
     "d dh p2 ????",  # Antonius
     "d dh p3 7h6h",  # Dwan
   
     "p3 cbr 7000",  # Dwan
     "p1 cbr 23000",  # Ivey
     "p2 f",  # Antonius
     "p3 cc",  # Dwan
   
     # Flop
   
     "d db Jc3d5c",
   
     "p1 cbr 35000",  # Ivey
     "p3 cc",  # Dwan
   
     # Turn
   
     "d db 4h",
   
     "p1 cbr 90000",  # Ivey
     "p3 cbr 232600",  # Dwan
     "p1 cbr 1067100",  # Ivey
     "p3 cc",  # Dwan
   
     # Showdown
   
     "p1 sm Ac2d",  # Ivey
     "p3 sm 7h6h",  # Dwan
   
     # River
   
     "d db Jh",
   ]
   author = "Juho Kim"
   event = "Full Tilt Million Dollar Cash Game S4E12"
   year = 2009
   players = ["Phil Ivey", "Patrik Antonius", "Tom Dwan"]
   currency = "USD"

Interactions
------------

The PokerKit library features PHH file format reader and writer utilities. It offers "load" and "dump" programmatic APIs akin to those provided by Python's standard libraries such as "json," and "pickle". Below are sample usages of the PHH file format utilities in PokerKit. The hand history object in Python serves as an iterator of the corresponding poker state which first yields the initial state, followed by the same state after applying each action one-by-one in the “actions” field. From game and state objects that are interacted with programmatically, the hand history object can also be created which can subsequently be saved in the file system.

Reading hands
^^^^^^^^^^^^^

.. code-block:: python

   from pokerkit import *

   # Hand loading
   with open("...", "rb") as file:
       hh = HandHistory.load(file)

   # Create game
   game = hh.create_game()

   # Create state
   state = hh.create_state()

   # Iterate through each action step
   for state in hh:
       ...

   # Iterate through each action step
   for state, action in hh.iter_state_actions():
       ...

It is possible to supply your own chip value parsing function, divmod, or rake function to construct the game states.

.. code-block:: python

   from pokerkit import *

   hh = HandHistory.load(
       ...,
       automations=...,
       divmod=...,
       rake=...,
       parse_value=...,
   )

   hh = HandHistory.loads(
       ...,
       automations=...,
       divmod=...,
       rake=...,
       parse_value=...,
   )

The default value parsing function, also supplied as ``parse_float`` to TOML loading functions in Python, is defined as :func:`pokerkit.utilities.parse_value` and automatically parses integers or floats based on the raw string value. You may supply your own number type parsers.

Writing Hands
^^^^^^^^^^^^^

.. code-block:: python

   from pokerkit import *

   # Game state construction
   game = PotLimitOmahaHoldem(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,
       0,
       (500, 1000),
       1000,
   )
   state = game((1259450.25, 678473.5), 2)

   # State progression; Pre-flop
   state.deal_hole("Ah3sKsKh")  # Antonius
   state.deal_hole("6d9s7d8h")  # Blom
   state.complete_bet_or_raise_to(3000)  # Blom
   state.complete_bet_or_raise_to(9000)  # Antonius
   state.complete_bet_or_raise_to(27000)  # Blom
   state.complete_bet_or_raise_to(81000)  # Antonius
   state.check_or_call()  # Blom

   # Flop
   state.deal_board("4s5c2h")
   state.complete_bet_or_raise_to(91000)  # Antonius
   state.complete_bet_or_raise_to(435000)  # Blom
   state.complete_bet_or_raise_to(779000)  # Antonius
   state.check_or_call()  # Blom

   # Turn & River
   state.deal_board("5h")
   state.deal_board("9c")

   # Creating hand history
   hh = HandHistory.from_game_state(game, state)
   hh.players = ["Patrik Antonius", "Viktor Blom"]

   # Dump hand
   with open("...", "wb") as file:
       hh.dump(file)
