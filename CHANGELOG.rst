=========
Changelog
=========

All notable changes to this project will be documented in this file.

Version 0.4.2 (December 15, 2023)
---------------------------------

**Added**

- New .phh optional fields: ``time``, ``time_limit``, ``time_banks``, ``level``.

Version 0.4.1 (December 13, 2023)
---------------------------------

**Added**

- New .phh optional fields: ``url``, ``city``, ``region``, ``postal_code``,
  ``country``.

**Changed**

- ``ante_trimming_status`` now an optional field for .phh files.

Version 0.4.0 (December 11, 2023)
---------------------------------

**Changed**

- When not enough card to deal everybody hole cards, a board dealing is done.
- Showdown can specify what cards the player showed.
- More generous state operations when it comes to cards. Some things that were
  errors are now warnings.
- When all-in, cards are shown via ``show_or_muck_hole_cards``.
- ``None`` is no longer ``ValuesLike`` or ``CardsLike``.

**Added**

- Cards with unknown rank or suit.
- ``float`` compatibility (without static typing support).
- Poker action notation support.
- Poker hand history file format (.phh) support.

Version 0.3.2 (December 4, 2023)
--------------------------------

**Changed**

- When saving state configuration, ``player_count`` is not saved.

Version 0.3.1 (December 4, 2023)
--------------------------------

**Added**

- Allow state configuration to be saved.

Version 0.3.0 (October 7, 2023)
-------------------------------

**Changed**

- Call ``unittest.main`` in unit test files when executed as ``__main__``.
- Move the ``automations`` parameter to be the first parameter of
  ``pokerkit.state.State``.

Version 0.2.1 (September 27, 2023)
----------------------------------

**Changed**

- Make ``pokerkit.state.Operation`` available as ``pokerkit.Operation`` by
  importing it in ``pokerkit.__init__``.

Version 0.2.0 (September 10, 2023)
----------------------------------

**Changed**

- Limit maximum number of completions, bets, or raises to 4 in the
  pre-configured Fixed-limit deuce-to-seven triple draw and Fixed-limit badugi
  variants.
- Flip antes just like blinds during heads-up play (in case of big blind antes).
- Also reshuffle all discarded cards (including from current draw round) along
  with mucked and burn cards when the deck runs out. Previously, discarded cards
  from the same draw round was excluded.
- Rename ``pokerkit.state.State.verify_card_availability_making`` to
  ``pokerkit.state.State.verify_cards_availability_making``.

**Added**

- Add more unittests and doctests to achieve 99% code coverage.

Version 0.1.1 (August 29, 2023)
-------------------------------

**Bugfixes**

- Fix ``AssertionError`` being raised in certain scenarios after discards are
  made when the state was configured to automatically deal hole cards.

**Changed**

- When the dealer deals hole cards after standing pat or discarding, an explicit
  ``ValueError`` is raised unless every player has stood pat or discarded.

Version 0.1.0 (August 27, 2023)
-------------------------------

**Added**

- ``pokerkit.state.Operation`` abstract base class for all operation classes.
- ``pokerkit.utilities.shuffled`` helper function.
- ``pokerkit.state.State.discarded_cards`` to keep track of discarded cards.
- ``pokerkit.state.State.street_count`` property.
- ``pokerkit.state.State.street_indices`` property.

**Changed**

- ``pokerkit.state.State`` now also accepts ``pokerkit.utilities.ValuesLike``
  instances as arguments for various parameters.
- ``pokerkit.state.State`` requires ``player_count`` argument to be passed
  during initialization.
- Various operation classes such as ``pokerkit.state.State.AntePosting`` moved
  to ``pokerkit.state`` and is no longer a nested class of
  ``pokerkit.state.State``.
- Renamed ``pokerkit.lookups.RegularLowLookup`` to
  ``pokerkit.lookups.RegularLookup`` for enhanced consistency.
- Renamed ``pokerkit.state.State.burned_cards`` to
  ``pokerkit.state.State.burn_cards``.
- Renamed ``pokerkit.state.State.verify_card_availabilities`` to
  ``pokerkit.state.State.verify_card_availability_making``.
- Changed the property ``pokerkit.state.State.available_cards`` to method
  ``pokerkit.state.State.get_available_cards``.
- Cards can be dealt from the mucked cards or burn cards if the deck is empty.
- Warning is printed if cards are dealt from burn cards without any good reason.

Version 0.0.2 (August 17, 2023)
-------------------------------

**Added**

- Introduce ``pokerkit.utilities.CardsLike`` and
  ``pokerkit.utilities.ValuesLike`` type aliases to simplify type annotations
  of various methods.

Version 0.0.1 (August 7, 2023)
------------------------------

**Changed**

- Modify the methods that only accepted an iterable of ``Card`` so they can
  accept any card-like object.
- Make the protected attributes of the instances of the ``Hand`` type and its
  descendants public.
- Move ``pokerkit.state.State._clean_cards`` and
  ``pokerkit.games.Game._clean_values`` to ``pokerkit.utilities``.

Version 0.0.0 (August 2, 2023)
------------------------------

**Initial Release**
