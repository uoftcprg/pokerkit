=========
Changelog
=========

All notable changes to this project will be documented in this file.

Version 0.5.2 (June 13, 2024)
----------------------------

**Changed**

- Allow ``numbers.Number`` like ``decimal.Decimal`` to be used as chip values. While documented as allowed, usage of non-``int`` or non-``float`` used to result in error.
- The main pot is pushed first, followed by side pots (reverse was true previously).
- Chips pushing operation is more fine-grained in that each operation pushes a portion of the main/side pot should there be multiple boards or hand types.
- Removed ``pokerkit.state.ChipsPushing.raked_amount`` attribute.
- Removed ``pokerkit.state.ChipsPushing.unraked_amount`` property.

**Added**

- Added ``pokerkit.state.ChipsPushing.pot_index``, ``pokerkit.state.ChipsPushing.board_index``, and ``pokerkit.state.ChipsPushing.hand_type_index`` attributes to provide information on what portion of the pot was pushed.

Version 0.5.1 (May 24, 2024)
----------------------------

**Added**

- Add standard error property ``pokerkit.analysis.Statistics.payoff_stderr`` to statistics.

Version 0.5.0 (April 25, 2024)
------------------------------

This version release introduces a number of backward incompatible changes. Please read the below content carefully!

**Summary of changes**

- Minor cleanup that **may** break older code.
- Option to choose cash-game vs. tournament (default) mode (defaults to tournament mode).

  - Unlike in tourneys, in cash-games, players can select the number of runouts during all-in situations.

- Option to choose the number of runouts during all-in situations (disabled in tournament mode).

  - In theory, people choose number of runouts before they show their hands. But, this isn't always followed. It is also unclear who must select the number of runouts first. As such, after all-in, when showdown takes place, 

- Multi-board games.
- More degree of freedom in hole dealing/showdown order.
- Docstring and documentation overhaul.
- Unknown starting stacks can be expressed with ``math.inf``.
- More flexible raking system.

**Changed**

- The parameters ``divmod``, and ``rake`` for relevant poker game/state initialization methods are now keyword-only arguments. Before, one could supply them as positional arguments but this is no longer allowed!
- ``pokerkit.state.State.board_cards`` (previously ``list[Card]``) is now of type ``list[list[Card]]``.

  - For example, if an all-in happens on the flop (AsKsQs) and is run twice (JsTs, JhTh), ``state.board_cards == [[As], [Ks], [Qs], [Js, Jh], [Ts, Th]]``. Or, when double board omaha is played, something like ``state.board_cards == [[??, ??], [??, ??], [??, ??]]`` will develop after the flop.
  - The function signatures for ``pokerkit.state.State.get_hand``, ``pokerkit.state.State.get_up_hand``, and ``pokerkit.state.State.get_up_hands`` now also requires the ``board_index`` to be supplied.
  - The properties/method ``pokerkit.state.State.reserved_cards``, ``pokerkit.state.State.cards_in_play``, ``pokerkit.state.State.cards_not_in_play``, and ``pokerkit.state.State.get_dealable_cards(deal_count: int)`` now return ``Iterator[Card]`` instead of ``tuple[Card, ...]``.
  - The method triplets for the hole dealing and showdown operation ``pokerkit.state.State.verify_hole_dealing()``, ``pokerkit.state.State.can_deal_hole()``, ``pokerkit.state.State.deal_hole()``, ``pokerkit.state.State.verify_hole_cards_showing_or_mucking()``, ``pokerkit.state.State.can_show_or_muck_hole_cards()``, and ``pokerkit.state.State.show_or_muck_hole_cards()`` also accepts an optional positional argument ``player_index`` to control the dealee, or the showdown performer. The verifiers also returns a player dealt if the dealee is not specified.

- The card-burning-related methods ``pokerkit.state.State.verify_card_burning``, ``pokerkit.state.State.can_burn_card``, and ``pokerkit.state.State.burn_card`` also accept a singleton card iterable.
- The ``pokerkit.state.State.all_in_show_status`` was renamed to ``pokerkit.state.State.all_in_status``.
- Renamed ``pokerkit.state.ChipsPushing.rake`` to ``pokerkit.state.ChipsPushing.raked_amount``.
- The attribute ``pokerkit.state.Pot.amount`` is now a property and no longer a parameter during initialization.

**Added**

- New enum class ``pokerkit.state.State.Mode`` for setting tournament/cash-game mode while initializing poker states.

  - Tournament mode: ``pokerkit.state.Mode.TOURNAMENT`` 
  - Cash-game mode: ``pokerkit.state.Mode.CASH_GAME``

    - In all-in situations, players have a chance to choose the number of runouts during showdown.

- New parameter ``mode`` in relevant poker game/state initialization methods. It defaults to tournament mode.
- New parameter ``starting_board_count`` in relevant poker game/state initialization methods. It defaults to ``1``. This allow multiple boards to be dealt if wished.
- New automation ``pokerkit.state.State.Automation.RUNOUT_COUNT_SELECTION`` which instructs PokerKit to carry out only one run-out.
- New ``pokerkit.state.RunoutCountSelection`` operation.

  - Arguments: ``runout_count`` and ``player_index`` who gives out the selection.
  - Querier: ``pokerkit.state.State.can_select_runout_count(player_index: int | None = None, runout_count: int | None = None)``.
  - Validator: ``pokerkit.state.State.verify_runout_count_selection(player_index: int | None = None, runout_count: int | None = None)``.
  - Operator: ``pokerkit.state.State.select_runout_count(player_index: int | None = None, runout_count: int | None = None, *, commentary: str | None = None)``.
  - People who can select run count: ``pokerkit.state.State.runout_count_selector_indices``.
  - If ``runout_count`` are in disagreement among active players, only ``1`` runout is performed.
  - When multiple runs are selected, the state will be incompatible with the PHH file format, as it stands.

- New attributes ``pokerkit.state.State.street_return_index`` and ``pokerkit.state.State.street_return_count`` that internally keeps track what street to return to and how many times to do so during multiple runouts.
- New attribute ``pokerkit.state.State.runout_count`` that shows the players' preferences on the number of runouts. It maybe ``None`` in which case the runout selection was skipped due to the state being of tournament mode or all players showed no preference by passing in ``None`` (or leaving empty) for the ``runout_count`` argument during the corresponding method call of ``pokerkit.state.select_runout_count()``.
- New attributes ``pokerkit.state.State.board_count`` and ``pokerkit.state.State.board_indices`` on the number of boards and the range of its indices. The number of boards is at least ``1`` but may be more due to multiple runouts or the variant being played.
- New method ``pokerkit.state.State.get_board_cards(board_index: int)`` on getting the ``board_index``'th board.

  - The maximum number of boards is either equal to the number of boards of the variant or (in case of multiple runouts) the product of it and the number of runouts.

- New attribute ``pokerkit.state.State.runout_count_selector_statuses`` that keeps track of who can select the number of runouts.
- New attribute ``pokerkit.state.State.runout_count_selection_flag`` that keeps track of whether the runout count selection has been carried out.
- In ``pokerkit.utilities.rake``, added parameters ``state``, ``cap``, and ``no_flop_no_drop``, and ``rake`` is now renamed as ``percentage`` and is a keyword parameter.
- New attributes ``pokerkit.state.Pot.raked_amount`` and ``pokerkit.state.Pot.unraked_amount`` that gives the raked and the unraked amounts of the pot.
- New property ``pokerkit.state.ChipsPushing.unraked_amount``.
- New attribute ``pokerkit.state.payoffs`` for keeping track of payoffs (rewards).

Version 0.4.17 (April 9, 2024)
------------------------------

**Changed**

- Make error/warning messages more descriptive.

**Added**

- Censored hole cards ``pokerkit.state.State.get_censored_hole_cards()``.
- Turn index ``pokerkit.state.State.turn_index``.

Version 0.4.16 (April 5, 2024)
------------------------------

**Added**

- Restore action notation ``pn sm -`` for showing hole cards.

Version 0.4.15 (March 29, 2024)
-------------------------------

**Added**

- Raise error for ACPC protocol converter when hole cards unknown.
- PHH to Pluribus protocol converter.

Version 0.4.14 (March 25, 2024)
-------------------------------

**Added**

- Analysis module

  - Range parser ``pokerkit.analysis.parse_range`` (e.g. ``"AKs,T8o-KJo,6h5h,A2+"``).
  - Equity calculator ``pokerkit.analysis.calculate_equities``.
  - Hand strength calculator ``pokerkit.analysis.calculate_hand_strength``.
  - Player statistics ``pokerkit.analysis.Statistics``.

Version 0.4.13 (March 23, 2024)
-------------------------------

**Changed**

- Renamed ``pokerkit.state.State.all_in_show_status`` to  ``pokerkit.state.State.all_in_status``.

**Added**

- ``pokerkit.state.State.reserved_cards``
- ``pokerkit.state.State.cards_in_play``
- ``pokerkit.state.State.cards_not_in_play``

Version 0.4.12 (March 21, 2024)
-------------------------------

**Removed**

- Remove non-compliant action notation ``pn sm -`` for showing hole cards.

**Added**

- Commentary for state actions.
- User-defined field support for PHH.
- PHH to ACPC protocol converter

Version 0.4.11 (March 15, 2024)
-------------------------------

**Added**

- Deuce-to-seven badugi hand lookup/evaluator.

Version 0.4.10 (February 11, 2024)
----------------------------------

**Added**

- ``pokerkit.state.State.pot_amounts`` for iterating through main/side pot amounts.

**Changed**

- Forbid showdown without specifying cards if unknown hole cards are dealt.

Version 0.4.9 (January 28, 2024)
--------------------------------

**Changed**

- New field ``rake`` for ``pokerkit.notation.HandHistory`` when constructing games/states.

Version 0.4.8 (January 22, 2024)
--------------------------------

**Changed**

- New action notation ``pn sm -`` for showing hole cards.
- ``pokerkit.notation.HandHistory.iter_state_actions`` for iterating through states with actions.

Version 0.4.7 (January 20, 2024)
--------------------------------

**Changed**

- If there are multiple pots (main + side), ``pokerkit.state.State.push_chips`` must be called multiple times.
- Custom automations are passed through the constructor for ``pokerkit.notation.HandHistory``.
- Support rakes.

Version 0.4.6 (January 8, 2024)
-------------------------------

**Changed**

- Collapse pots (main + side) that have the same players in the ``pokerkit.state.State.pots`` property.
- Allow default automations to be overridden in ``pokerkit.notation.HandHistory.create_game`` and ``pokerkit.notation.HandHistory.create_game``.

Version 0.4.5 (January 4, 2024)
-------------------------------

**Changed**

- Fix incorrect type annotation for class attribute ``optional_field_names`` in ``optional_field_names`` in``pokerkit.notation.HandHistory``.
- Operation queries also catch ``UserWarning``.

Version 0.4.4 (January 1, 2024)
-------------------------------

**Added**

- Add class attributes ``game_field_names`` and ``ignored_field_names`` to ``pokerkit.notation.HandHistory``.

**Changed**

- Remove class attributes ``game_field_names`` and ``ignored_field_names`` from ``pokerkit.notation.HandHistory``

Version 0.4.3 (December 17, 2023)
---------------------------------

**Added**

- The new .phh optional fields: ``time_zone``

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

- ``ante_trimming_status`` is now an optional field for .phh files.

Version 0.4.0 (December 11, 2023)
---------------------------------

**Changed**

- When not enough cards to deal everybody's hole cards, a board dealing is done.
- Showdown can specify what cards the player showed.
- More generous state operations when it comes to cards. Some things that were errors are now warnings.
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
- Move the ``automations`` parameter to be the first parameter of ``pokerkit.state.State``.

Version 0.2.1 (September 27, 2023)
----------------------------------

**Changed**

- Make ``pokerkit.state.Operation`` available as ``pokerkit.Operation`` by importing it in ``pokerkit.__init__``.

Version 0.2.0 (September 10, 2023)
----------------------------------

**Changed**

- Limit the maximum number of completions, bets, or raises to 4 in the pre-configured Fixed-limit deuce-to-seven triple draw and Fixed-limit badugi variants.
- Flip antes just like blinds during heads-up play (in the case of big blind antes).
- Also reshuffle all discarded cards (including from the current draw round) along with mucked and burned cards when the deck runs out. Previously, discarded cards from the same draw round was excluded.
- Rename ``pokerkit.state.State.verify_card_availability_making`` to ``pokerkit.state.State.verify_cards_availability_making``.

**Added**

- Add more unit tests and doctests to achieve 99% code coverage.

Version 0.1.1 (August 29, 2023)
-------------------------------

**Bugfixes**

- Fix ``AssertionError`` being raised in certain scenarios after discards are made when the state was configured to automatically deal with hole cards.

**Changed**

- When the dealer deals hole cards after standing pat or discarding, an explicit ``ValueError`` is raised unless every player has stood pat or discarded.

Version 0.1.0 (August 27, 2023)
-------------------------------

**Added**

- ``pokerkit.state.Operation`` abstract base class for all operation classes.
- ``pokerkit.utilities.shuffled`` helper function.
- ``pokerkit.state.State.discarded_cards`` to keep track of discarded cards.
- ``pokerkit.state.State.street_count`` property.
- ``pokerkit.state.State.street_indices`` property.

**Changed**

- ``pokerkit.state.State`` now also accepts ``pokerkit.utilities.ValuesLike`` instances as arguments for various parameters.
- ``pokerkit.state.State`` requires ``player_count`` argument to be passed during initialization.
- Various operation classes such as ``pokerkit.state.State.AntePosting`` moved to ``pokerkit.state`` and is no longer a nested class of ``pokerkit.state.State``.
- Renamed ``pokerkit.lookups.RegularLowLookup`` to ``pokerkit.lookups.RegularLookup`` for enhanced consistency.
- Renamed ``pokerkit.state.State.burned_cards`` to ``pokerkit.state.State.burn_cards``.
- Renamed ``pokerkit.state.State.verify_card_availabilities`` to ``pokerkit.state.State.verify_card_availability_making``.
- Changed the property ``pokerkit.state.State.available_cards`` to method ``pokerkit.state.State.get_available_cards``.
- Cards can be dealt from the mucked cards or burn cards if the deck is empty.
- Warning is printed if cards are dealt from burn cards without any good reason.

Version 0.0.2 (August 17, 2023)
-------------------------------

**Added**

- Introduce ``pokerkit.utilities.CardsLike`` and ``pokerkit.utilities.ValuesLike`` type aliases to simplify type annotations of various methods.

Version 0.0.1 (August 7, 2023)
------------------------------

**Changed**

- Modify the methods that only accept an iterable of ``Card`` so they can accept any card-like object.
- Make the protected attributes of the instances of the ``Hand`` type and its descendants public.
- Move ``pokerkit.state.State._clean_cards`` and ``pokerkit.games.Game._clean_values`` to ``pokerkit.utilities``.

Version 0.0.0 (August 2, 2023)
------------------------------

**Initial Release**
