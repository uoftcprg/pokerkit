=========
Changelog
=========

All notable changes to this project will be documented in this file.

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
