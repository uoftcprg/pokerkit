Hand History
============

PokerKit can save and load hands. The hand is written in .toml compatible
format with an extension: .phh.

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
  - et cetera

- ``antes``: The antes, array of non-negative integers or floats.
- ``blinds_or_straddles``: The blinds or straddles (some variants), array of
  non-negative integers or floats.
- ``bring_in``: The bring-in (some variants), positive integer or float.
- ``small_bet``: The small bet (some variants), positive integer or float.
- ``big_bet``: The big bet (some variants), positive integer or float.
- ``min_bet``: The minimum bet (some variants), positive integer or float.
- ``starting_stacks``: The starting stacks, array of positive integers or floats.
- ``actions``: The actions where dealer is ``d`` and n'th player is ``pn``, array of
  strings.

  - ``d db <cards>``: deal board cards.
  - ``d dh <player> <cards>``: deal hole cards.
  - ``<player> sd[ <cards>]``: stand pat or discard.
  - ``<player> pb``: post bring-in.
  - ``<player> f``: fold.
  - ``<player> cc``: check or call.
  - ``<player> cbr <amount>``: complete, bet, or raise to an amount.
  - ``<player> sm[ <cards>]``: show or muck hole cards.

Optional fields:

- ``author``: The author, string (First name last name).
- ``event``: The event, string.
- ``url``: The url, string.
- ``address``: The address, string.
- ``city``: The city, string.
- ``region``: The region, string.
- ``postal_code``: The postal code, string.
- ``country``: The country, string
- ``day``: The day, integer.
- ``month``: The month, integer.
- ``year``: The year, integer.
- ``hand``: The hand number, integer.
- ``seats``: The seat numbers, array of integers or floats.
- ``seat_count``: The number of seats, integer.
- ``table``: The table number, integer.
- ``players``: The player names, array of strings (First name last name).
- ``finishing_stacks``: The finishing stacks, array of non-negative integers or
  floats.
- ``currency``: The currency, string (ISO 4127).
- ``ante_trimming_status``: How to handle unequal ante contributions, Boolean.

Example .phh file:

.. code-block:: toml

   # The first televised million dollar pot between Tom Dwan and Phil
   # Ivey.
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
   event = "Full Tilt Million Dollar Cash Game"
   year = 2009
   players = ["Phil Ivey", "Patrik Antonius", "Tom Dwan"]
   currency = "USD"
