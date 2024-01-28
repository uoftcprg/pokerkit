Poker Simulation
================

The functionalities of PokerKit primarily fall into two categories: game simulations and hand evaluations. Game simulations encompass creating an environment where poker games can be played out programmatically, simulating real-world scenarios with high fidelity. On the other hand, hand evaluations are concerned with determining the strength of particular poker hands.

Our `PokerKit paper <https://doi.org/10.1109/TG.2023.3325637>`__ gives a general overview of our library that summarizes the content of this page.

Introduction
------------

PokerKit is a very powerful tool you can use to simulate games. Its customizability allows users to define and utilize almost every poker variant that exists.

Each poker variant often introduces unique game rules and hand types not seen in other variants. The versatility of PokerKit allows for the customization of poker variants, allowing users to define their own unique games, adapt an existing variant, or implement a variant not currently supported by PokerKit out of the box. This flexibility is achieved without compromising the robustness of the implementation, backed by extensive unit tests and doctests to ensure error-free operations. Naturally, common variants are already defined out of the box, so, for most use cases, users will not have to define their own variants.

PokerKit stands out with its ability to cater to an assortment of use cases, offering varying degrees of control over the game state. For instance, in use cases for poker AI agent development, where the agents' focus lies primarily in action selection during betting rounds, minute details such as showdown order, posting blinds, posting antes, and bet collection may not be pertinent. On the other hand, an online poker casino requires granular control over each game aspect. These include dealing hole cards one by one, burning cards, deciding to muck or show during the showdown (even when unnecessary), killing hands after the showdown, pushing chips to the winner's stack, and even the winner collecting the chips into their stack. PokerKit rises to this challenge, providing users with varying levels of automation tailored to their specific needs.

Initializing States
-------------------

There are two methods the user can initialize a poker state to simulate them. The first method involves using pre-defined games from which the user just needs to specify the initial chip configurations. The second method involves defining every parameter such that all the various aspects of poker games such as the variant and the initial chip configurations.

Pre-Defined Variants
^^^^^^^^^^^^^^^^^^^^

PokerKit offers virtually unlimited poker variants to be played. However, defining poker variants can be quite an overwhelming task for a new user. We offer pre-defined poker variants where the user can just supply arguments such as antes, blinds, starting stacks, et cetera, which are as follows:

- Fixed-limit badugi: :class:`pokerkit.games.FixedLimitBadugi`
- Fixed-limit deuce-to-seven lowball triple draw: :class:`pokerkit.games.FixedLimitDeuceToSevenLowballTripleDraw`
- Fixed-limit Omaha hold'em hi-low split-eight or better low: :class:`pokerkit.games.FixedLimitOmahaHoldemHighLowSplitEightOrBetter`
- Fixed-limit razz: :class:`pokerkit.games.FixedLimitRazz`
- Fixed-limit seven card stud: :class:`pokerkit.games.FixedLimitSevenCardStud`
- Fixed-limit seven card stud hi-low split-eight or better low: :class:`pokerkit.games.FixedLimitSevenCardStudHighLowSplitEightOrBetter`
- Fixed-limit Texas hold'em: :class:`pokerkit.games.FixedLimitTexasHoldem`
- No-limit deuce-to-seven single draw: :class:`pokerkit.games.NoLimitDeuceToSevenLowballSingleDraw`
- No-limit short-deck hold'em: :class:`pokerkit.games.NoLimitShortDeckHoldem`
- No-limit Texas hold'em: :class:`pokerkit.games.NoLimitTexasHoldem`
- Pot-limit Omaha hold'em: :class:`pokerkit.games.PotLimitOmahaHoldem`

These pre-defined games can be created as shown below:

.. code-block:: python

   from pokerkit import (
        Automation,
        FixedLimitDeuceToSevenLowballTripleDraw,
        NoLimitTexasHoldem,
   )

   state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
       # automations
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
       True,  # False for big blind ante, True otherwise
       0,  # ante
       (75000, 150000),  # blinds or straddles
       150000,  # small bet
       300000,  # big bet
       (1180000, 4340000, 5910000, 10765000),  # starting stacks
       4,  # number of players
   )

   state = NoLimitTexasHoldem.create_state(
       # automations
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
       True,  # False for big blind ante, True otherwise
       500,  # ante
       (1000, 2000),  # blinds or straddles
       2000,  # min bet
       (1125600, 2000000, 553500),  # starting stacks
       3,  # number of players
   )

One can create an instance of a poker variant from which states can be created simply by supplying the starting stacks and the number of players. The code below is equivalent to the previous code.

.. code-block:: python

   from pokerkit import (
        Automation,
        FixedLimitDeuceToSevenLowballTripleDraw,
        NoLimitTexasHoldem,
   )

   variant = FixedLimitDeuceToSevenLowballTripleDraw(
       # automations
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
       True,  # False for big blind ante, True otherwise
       0,  # ante
       (75000, 150000),  # blinds or straddles
       150000,  # small bet
       300000,  # big bet
   )
   state = variant(
       (1180000, 4340000, 5910000, 10765000),  # starting stacks
       4,  # number of players
   )

   variant = NoLimitTexasHoldem(
       # automations
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
       True,  # False for big blind ante, True otherwise
       500,  # ante
       (1000, 2000),  # blinds or straddles
       2000,  # min bet
   )
   state = variant(
       (1125600, 2000000, 553500),  # starting stacks
       3,  # number of players
   )

The exact parameters that must be specified differ depending on the variant being played. Some pre-defined games do not accept blinds or straddles but instead accept a bring-in amount. For a specific list of parameters, refer to the API references.

Defining States from Scratch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to create a state of a variant not listed above, you will have to define a variant. What exactly is a variant then? A variant is composed of the following definitions:

- **Deck**: Most variants use a 52-card deck.
- **Hand Types**: Most variants have one, but high/low-split games have two.
- **Streets**: Each specifies whether to burn a card, deal the board, deal the players, draw cards, the opener, the minimum bet, and the maximum number of bets or raises.
- **Betting Structure**: Betting limits such as no-limit, pot-limit, or fixed-limit.

When creating a state, the user must not only supply these parameters but also supply additional values that denote the state's initial configurations such as antes (uniform or non-uniform), blinds/straddles, bring-ins, and starting stacks.

The below definition shows a Kuhn poker variant:

.. code-block:: python

   from pokerkit import (
        Automation,
        BettingStructure,
        Deck,
        KuhnPokerHand,
        Opening,
        State,
        Street,
   )

   state = State(
       # automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_DEALING,
           Automation.BOARD_DEALING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       Deck.KUHN_POKER,  # deck
       (KuhnPokerHand,),  # hand types (high/low-split will have two types)
       # streets
       (
           Street(
               False,  # card burning
               (False,),  # hole card dealing statuses (False for face-down)
               0,  # board dealing count
               False,  # standing pat or discarding
               Opening.POSITION,  # who opens the betting?
               1,  # min bet
               None,  # maximum number of completions/bettings/raisings
           ),
       ),
       BettingStructure.FIXED_LIMIT,  # betting structure
       True,  # ``False`` for big blind ante, otherwise ``True``
       (1,) * 2,  # ante
       (0,) * 2,  # blind or straddles
       0,  # bring-in
       (2,) * 2,  # starting stacks
       2,  # number of players
   )

When creating states, there is a lot to specify and you will have to experiment to get it right. If you want to see other variants pre-defined, create an issue.

Note that depending on the variant, one of the blinds/straddles or bring-in must be zero. More details about each parameter follow.

Automations
^^^^^^^^^^^

The PokerKit state allows the state to be modified in a really fine-grained way, down to posting antes, blinds, straddles, burning cards before dealing, dealing hole cards, dealing board cards, standing pat, discarding, folding, checking, calling, posting bring-ins, completing, betting, raising, showing hole cards, mucking, dealer killing losing hands, collecting bets, pushing chips to the winners, winners putting the chips they won back into their stack.

This fine-grained state transition is necessary for use in online casinos. However, depending on the use cases, many of these operations are completely irrelevant and can be automated without any user input, as users can specify which operations they want to be manual and automatic.

For example, if you are trying to create a poker AI, you are not worried about mucking the best hand or showing the worst hand, burning a card, pushing the chips to the winners, collecting chips a player won, collecting bets after each street, et cetera. But, you want to handle user actions like fold, check, call, bring-in, complete, bet, and raise. Also, you might want to control what cards are dealt to each player and to the board. The below automations will suit the aforesaid use cases.

.. code-block:: python

   from pokerkit import Automation

   # automate everything except player actions
   # Examples:
   #   - Standing pat
   #   - Discarding
   #   - Folding
   #   - Checking
   #   - Calling
   #   - Posting bring-in
   #   - Completing
   #   - Betting
   #   - Raising
   automations = (
       Automation.ANTE_POSTING,
       Automation.BET_COLLECTION,
       Automation.BLIND_OR_STRADDLE_POSTING,
       Automation.CARD_BURNING,
       Automation.HOLE_DEALING,
       Automation.BOARD_DEALING,
       Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
       Automation.HAND_KILLING,
       Automation.CHIPS_PUSHING,
       Automation.CHIPS_PULLING,
   )

   # Automate everything except player actions and dealings
   # Examples:
   #   - Player:
   #     - Standing pat
   #     - Discarding
   #     - Folding
   #     - Checking
   #     - Calling
   #     - Posting bring-in
   #     - Completing
   #     - Betting
   #     - Raising
   #   - Dealer:
   #     - Deal hole cards
   #     - Deal board cards
   automations = (
       Automation.ANTE_POSTING,
       Automation.BET_COLLECTION,
       Automation.BLIND_OR_STRADDLE_POSTING,
       Automation.CARD_BURNING,
       Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
       Automation.HAND_KILLING,
       Automation.CHIPS_PUSHING,
       Automation.CHIPS_PULLING,
   )

However, if you are trying to create an online poker room, you need to represent all these fine changes to create a smooth user experience. In such a case, nothing must be automated.

Even if you are trying to use this for video poker and you are happy with PokerKit dealing cards at random (hopefully), you should still pass an empty automation as this parameter. This is because the dealing of each card is still a change in the state and therefore you might want to represent the state changing as each card is dealt.

.. code-block:: python

   # Automate nothing (control even what cards are dealt)
   automations = ()

:class:`pokerkit.state.Automation` describes a complete list of operations that can be automated.

Deck
^^^^

When you supply a deck to the state, the state automatically shuffles it so the cards can be dealt at random when required. :class:`pokerkit.utilities.Deck` describes a complete list of decks. Decks are simply tuples of cards and you can define your own as needed.

Most poker games use a standard 52-card deck, accessible as :class:`pokerkit.utilities.Deck.STANDARD` or :class:`pokerkit.utilities.Deck.REGULAR`. Both are composed of 52 cards and have no difference in content. The only difference between the two is that they are sorted differently. The standard deck has aces after kings while the regular deck has aces before deuces. Obviously, after shuffling, there is no real difference. Simply choose whatever you prefer. In pre-defined games within PokerKit, standard decks are usually used while regular decks are used for variants that always consider ace to be low. Note that the terms ``standard deck`` and ``regular deck`` are something we made up. But, ace-low games are sometimes referred to with the word ``regular`` as in ``seven card stud high-low regular``.

Hand Types
^^^^^^^^^^

Hand types denote how hands are evaluated. This also considers how many hole cards are considered, et cetera. Most games like Texas hold 'em or short-deck use one, but some games like high-low split games use two. Technically, you can define more than two in PokerKit, but no mainstream variant uses more than two hand types.

.. code-block:: python

   from pokerkit import *

   # Texas hold'em, et cetera
   hand_types = (StandardHighHand,)

   # Omaha hold'em Hi-lo split 8-or-better
   hand_types = OmahaHoldemHand, OmahaEightOrBetterLowHand

Hand types are defined in :mod:`pokerkit.hands`.

Streets
^^^^^^^

Streets describe each betting round and the dealing(s) before it. When you define a street, internal checks are carried out to make sure the definition is sound. For example, either the dealer deals something or the players can discard it before each street. Examples of some variants are shown below:

.. code-block:: python

   from pokerkit import *

   # No-limit Texas hold'em
   streets = (
       Street(
           card_burning_status=False,
           hole_dealing_statuses=(False, False),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.POSITION,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=None,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(),
           board_dealing_count=3,
           draw_status=False,
           opening=Opening.POSITION,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=None,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(),
           board_dealing_count=1,
           draw_status=False,
           opening=Opening.POSITION,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=None,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(),
           board_dealing_count=1,
           draw_status=False,
           opening=Opening.POSITION,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=None,
       ),
   )

   # Fixed-limit razz
   streets = (
       Street(
           card_burning_status=False,
           hole_dealing_statuses=(False, False, True),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.HIGH_CARD,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=4,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(True,),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.LOW_HAND,
           min_completion_betting_or_raising_amount=2,
           max_completion_betting_or_raising_count=4,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(True,),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.LOW_HAND,
           min_completion_betting_or_raising_amount=4,
           max_completion_betting_or_raising_count=4,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(True,),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.LOW_HAND,
           min_completion_betting_or_raising_amount=4,
           max_completion_betting_or_raising_count=4,
       ),
       Street(
           card_burning_status=True,
           hole_dealing_statuses=(False,),
           board_dealing_count=0,
           draw_status=False,
           opening=Opening.LOW_HAND,
           min_completion_betting_or_raising_amount=4,
           max_completion_betting_or_raising_count=4,
       ),
   )

Each street is defined with the following parameters.

Card Burning
""""""""""""

You might want to burn cards before any cards are dealt such as when dealing flops, turns, or rivers in Texas hold'em, or before dealing hole cards after drawing in draw games.

Hole Card Dealing Statuses
""""""""""""""""""""""""""

Most poker variants deal cards face down, but this is not the case for stud games. In seven card stud, cards are dealt "down down up", "up", "up", and so on. This parameter allows the user to specify how to deal with hole cards.

Board Dealing Count
"""""""""""""""""""

This parameter denotes how many board cards are dealt.

Standing Pat or Discarding Status
"""""""""""""""""""""""""""""""""

This parameter denotes whether the players can discard hole cards before betting.

Opening
"""""""

This parameter specifies how to choose the first player to act. The complete list of openings is shown in :class:`pokerkit.state.Opening`.

All button games without exception have openers that are decided by position. The position takes account of blinds or straddles, if any. It happens to be that all button games do not use bring-ins.

Games that do have bring-ins, such as stud games, have openers that are either decided by the face-up card (first betting round) or the strength of the open hand (subsequent betting rounds). Depending on whether the game is a low game or not, the low or high card/hand is used to pick the opener. Suits are only used to break ties when comparing cards, not hands. When some hands are tied, the player with the lowest player index opens the pot as per the `2023 WSOP Tournament Rules <_static/2023-WSOP-Tournament-Rules.pdf>`_.

Minimum Completion, Betting, or Raising Amount
""""""""""""""""""""""""""""""""""""""""""""""

Simply put, this value denotes the min-bet in no-limit games (typically the big blind) or small/big bets in limit games (typically the big blind or double it, respectively). It should be a positive value.

Maximum Completion, Betting, or Raising Count
"""""""""""""""""""""""""""""""""""""""""""""

This value denotes how many times a bet/raise can be made. In no-limit games, this value is unlimited, for which the user can supply ``None``. Otherwise, if the number of bets/raises is limited, as for typical fixed-limit games, an integral value must be supplied. In the `2023 WSOP Tournament Rules <_static/2023-WSOP-Tournament-Rules.pdf>`_, this value is typically ``4``, which is the value we use for pre-defined fixed-limit games.

In heads-up levels, the `2023 WSOP Tournament Rules <_static/2023-WSOP-Tournament-Rules.pdf>`_ states that unlimited bets/raises are possible. Our pre-defined games do not follow this due to consistency. Michael Bowling's Science paper that says "heads-up limit hold'em poker is solved" (misleading since they assume static starting stacks) uses the rule of ``4`` bet/raises max.

Betting Structure
^^^^^^^^^^^^^^^^^

The betting structure denotes whether a game is fixed-limit, pot-limit, or no-limit. The complete list of possible values is shown in :class:`pokerkit.state.BettingStructure`.

Ante Trimming Status
^^^^^^^^^^^^^^^^^^^^

This parameter exists due to a possible room for ambiguity in the way antes are handled. If you are using uniform antes, you are recommended to use ``True``. If you are not using uniform antes, such as button ante or big-blind ante, you must use ``False``.

Essentially, this must be specified because it answers the crucial question of: "If you put in less ante than others, do you deserve to win the full antes by others?" This question is only relevant when one of the winners was so ridiculously short-stacked that they could not even afford to put in the full ante. If they win, maybe they should not be able to take the full antes of others. In the situation of big-blind ante, most players do not contribute any antes at all. But, they nonetheless are entitled to the big blind's ante.

Raw Antes
^^^^^^^^^

This parameter states the antes. PokerKit is quite intelligent when interpreting this value. If you just put in a single value like ``2.00``, all players will be anted exactly ``2.00``. If you put in ``[0, 2]`` or ``{1: 2}``, it will be interpreted as a big-blind ante. Similarly, ``{-1: 2}`` is the button ante. This parameter is raw in that it must be cleaned by PokerKit.

Raw Blinds or Straddles
^^^^^^^^^^^^^^^^^^^^^^^

This parameter states the blinds or straddles. It is raw in that it must be cleaned by PokerKit just like raw antes. Standard small and big blinds can be supplied as ``[0.5, 1]``. With straddles, it would be ``[0.5, 1, 2]``. With double straddles ``[0.5, 1, 2, 4]``. With button straddle, ``{0: 0.5, 1: 1, -1: 2}``. If the small and big blinds are equal, then it would be ``[2, 2]``. The possibilities are endless. If the game does not use blinds or straddles, the user must supply ``0`` meaning no player is blinded or straddled.

Bring-In
^^^^^^^^

Some games use bring-ins. If this is supplied it must be a positive value like ``1.5``. Otherwise, simply supply ``0``. If this value is relevant, the blinds or straddles must be ``0`` or its equivalent.

Raw Starting Stacks
^^^^^^^^^^^^^^^^^^^

This parameter states the starting stacks. Again, the values are interpreted by PokerKit.

Player Count
^^^^^^^^^^^^

This parameter simply states the number of players.

Divmod
^^^^^^

This is an optional parameter. It is a callable that divides up a pot among the winners who are entitled to win the pot. By default, if PokerKit deems that the values in the poker state are integral, the pot is divided evenly using floor division. The remainder (akin to odd-chips) is given to the player most out of position. If PokerKit deems that the values in the poker state are real, the pot is divided up using "true" division among the winners. To be safe, if you want to always handle integers, make sure all numerical values supplied to PokerKit states are integral. Obviously, if you want to handle all the chip values as a real number, supply them as floats.

The user may want to use dollar values with two decimal places. PokerKit is designed to automatically handle that if you are using Python's built-in decimal types. Just to be safe, or if you want to somehow simulate how actual chips on a poker table sometimes cannot be divided evenly among the players, you can define a custom function that divides up the pot. For function signatures and what to return, check out our default :func:`pokerkit.utilities.divmod` function.

Rake
^^^^

This is an optional parameter. It is a callable that takes a rake from the pot. By default, PokerKit states take no rake. The default :func:`pokerkit.utilities.rake` function can accept parameters to take non-zero rake. You can use ``partial`` with it to supply it when creating states. Of course, the user can define their own to do something more complex like min-rake or max-rake per hand.

State Transitions
-----------------

PokerKit structures the game flow into distinct phases, each supporting a different set of operations (dealing, betting, collecting bets, showing hands, et cetera).

Phases
^^^^^^

Depending on the game state, each phase may be skipped. For instance, if the user has specified no antes, the ante posting phase will be omitted. Likewise, if no bets were placed during the betting phase, the bet collection phase will be bypassed. A phase transition occurs upon the completion of a phase. This transition is internally managed by the game framework, facilitating a seamless game flow to the end user. During each phase of PokerKit’s game simulation, the user can invoke various methods to execute operations. Each operation belongs to a specific phase and can only be enacted when the corresponding phase is active.

1. **Ante Posting**: During the ante-posting phase, each player has the option to execute an ante-posting operation. The parameters supplied to the state during its creation may dictate no antes, uniform antes, or non-uniform antes, such as big blind antes. If no player is due to post an ante, this phase is bypassed.
2. **Bet Collection**: The collection of bets on the table occurs after any phase that allows players to bet. If any bet is present, the bet collection operation must be performed before proceeding to the subsequent phase. This phase only occurs after ante-posting or betting. When no bets are pending collection, this phase is skipped.
3. **Blind or Straddle Posting**: Forced bets like blinds or straddles must be posted before the start of the first street. PokerKit accommodates a variety of blind or straddle configurations, ranging from small and big blinds, to button blinds or even no blind at all. If the state is configured to exclude any forced bets, this phase is skipped.
4. **Dealing**: The dealing phase precedes the betting phase. During this phase, the user can deal with board or hole cards, contingent upon the state's configuration. Options to burn a card or discard and draw cards are also available when applicable. This phase is bypassed if only one player remains in the hand.
5. **Betting**: During betting, players can execute the actions such as folding, checking, calling, posting a bring-in, completing, betting, or raising. During state creation, the user must specify how to select the first player to act and the betting limits. This phase is bypassed if all players are all-in or if only one player remains in the hand.
6. **Showdown**: During the showdown, players reveal or muck their hands in accordance with the showdown order. The first to show is typically the last aggressor in the final street. If no one bet, the player who was the first to act in the final betting round must show first. Players can opt to show a losing hand or muck a winning hand, even though this is often disadvantageous. When dealing with all-in pots, players are obligated to show their hands in order to prevent chip-dumping. If this is the case, or if only one player remains in the pot, the showdown phase is bypassed.
7. **Hand Killing**: The dealer is responsible for "killing," or discarding, hands that cannot win any portion of the pot. If no hand should be killed, this phase is bypassed.
8. **Chips Pushing**: The dealer is charged with pushing the chips to the winners. In button games, the pot size is always non-zero due to the mandatory presence of antes, forced bets, or bring-ins (as enforced by PokerKit). Thus, this phase is always carried out in button games. This might not be the case in non-button games like stud games without antes where everyone folds after the opener brings in or completes.
9. **Chips Pulling**: Players may incorporate the chips they've won back into their stack. In poker, at least one player is guaranteed to win the pot. Consequently, this phase is never skipped.

Note that, depending on the number of betting rounds, the **Dealing**, **Betting**, and **Bet Collection** phases may be repeated.

Operations
^^^^^^^^^^

Each operation is coupled with two associated methods: a verification method and an action query. The verification method validates if a move can be executed within the rules, considering the current game state and the variant in play. It raises an error if any discrepancy is detected. Users can directly invoke this or use a corresponding action query method (with optional arguments), which simply checks if the verification method triggers an error and returns a Boolean value indicating the validity of the action. The method that performs the operation initially runs the verification method, executing the operation only if no errors are raised. If the verification fails, the state remains unchanged.

Below list of all the operations supported by PokerKit. Depending on your use case, many of these operations will not be of concern and can be automated.

- Ante posting: :meth:`pokerkit.state.State.post_ante`
- Bet collection: :meth:`pokerkit.state.State.collect_bets`
- Blind/straddle posting: :meth:`pokerkit.state.State.post_blind_or_straddle`
- Card burning: :meth:`pokerkit.state.State.burn_card`
- Hole dealing: :meth:`pokerkit.state.State.deal_hole`
- Board dealing: :meth:`pokerkit.state.State.deal_board`
- Standing pat/discarding: :meth:`pokerkit.state.State.stand_pat_or_discard`
- Folding: :meth:`pokerkit.state.State.fold`
- Checking/calling: :meth:`pokerkit.state.State.check_or_call`
- Bring-in posting: :meth:`pokerkit.state.State.post_bring_in`
- Completion/betting/raising to: :meth:`pokerkit.state.State.complete_bet_or_raise_to`
- Hole cards showing/mucking: :meth:`pokerkit.state.State.show_or_muck_hole_cards`
- Hand killing: :meth:`pokerkit.state.State.kill_hand`
- Chips pushing: :meth:`pokerkit.state.State.push_chips`
- Chips pulling: :meth:`pokerkit.state.State.pull_chips`

Now, let's say you know what operations you should worry about. How do you know when to invoke them? PokerKit has handy methods to query whether you can perform an operation:

- Ante posting: :meth:`pokerkit.state.State.can_post_ante`
- Bet collection: :meth:`pokerkit.state.State.can_collect_bets`
- Blind/straddle posting: :meth:`pokerkit.state.State.can_post_blind_or_straddle`
- Card burning: :meth:`pokerkit.state.State.can_burn_card`
- Hole dealing: :meth:`pokerkit.state.State.can_deal_hole`
- Board dealing: :meth:`pokerkit.state.State.can_deal_board`
- Standing pat/discarding: :meth:`pokerkit.state.State.can_stand_pat_or_discard`
- Folding: :meth:`pokerkit.state.State.can_fold`
- Checking/calling: :meth:`pokerkit.state.State.can_check_or_call`
- Bring-in posting: :meth:`pokerkit.state.State.can_post_bring_in`
- Completion/betting/raising to: :meth:`pokerkit.state.State.can_complete_bet_or_raise_to`
- Hole cards showing/mucking: :meth:`pokerkit.state.State.can_show_or_muck_hole_cards`
- Hand killing: :meth:`pokerkit.state.State.can_kill_hand`
- Chips pushing: :meth:`pokerkit.state.State.can_push_chips`
- Chips pulling: :meth:`pokerkit.state.State.can_pull_chips`

These methods return ``True`` if you can perform such an operation (with
specified arguments, if any) or ``False`` if otherwise.

There exist methods that, instead of returning a Boolean, throw an error with specific error messages.

- Ante posting: :meth:`pokerkit.state.State.verify_ante_posting`
- Bet collection: :meth:`pokerkit.state.State.verify_bet_collection`
- Blind/straddle posting: :meth:`pokerkit.state.State.verify_blind_or_straddle_posting`
- Card burning: :meth:`pokerkit.state.State.verify_card_burning`
- Hole dealing: :meth:`pokerkit.state.State.verify_hole_dealing`
- Board dealing: :meth:`pokerkit.state.State.verify_board_dealing`
- Standing pat/discarding: :meth:`pokerkit.state.State.verify_standing_pat_or_discarding`
- Folding: :meth:`pokerkit.state.State.verify_folding`
- Checking/calling: :meth:`pokerkit.state.State.verify_checking_or_calling`
- Bring-in posting: :meth:`pokerkit.state.State.verify_bring_in_posting`
- Completion/betting/raising to: :meth:`pokerkit.state.State.verify_completion_betting_or_raising_to`
- Hole cards showing/mucking: :meth:`pokerkit.state.State.verify_hole_cards_showing_or_mucking`
- Hand killing: :meth:`pokerkit.state.State.verify_hand_killing`
- Chips pushing: :meth:`pokerkit.state.State.verify_chips_pushing`
- Chips pulling: :meth:`pokerkit.state.State.verify_chips_pulling`

Most of the operations can optionally accept arguments. Some are more important
than others. Let's see what we can or must specify for each action.

- Ante posting: player_index, defaults to the first player who did not post ante
- Bet collection: N/A
- Blind/straddle posting: player_index, defaults to the first player who did not post the blind or straddle
- Card burning: card, defaults to randomly drawing from the deck
- Hole dealing: cards, defaults to randomly drawing a single card from the deck
- Board dealing: cards, defaults to randomly drawing required cards from the deck
- Standing pat/discarding: cards, defaults to standing pat
- Folding: N/A
- Checking/calling: N/A
- Bring-in posting: N/A
- Completion/betting/raising to: amount, defaults to completion, min-bet, or min-raise
- Hole cards showing/mucking: status, defaults to showing only when no one else has shown a better hand
- Hand killing: player_index, defaults to the first player who cannot win any portion of the pot
- Chips pushing: N/A
- Chips pulling: player_index, defaults to the first player who won a portion of the pot

Information crucial for each operation such as what the minimum bets are, to whom the hole card will be dealt next when the dealee is unspecified, the call amount, the actor, et cetera is below.

- Effective ante: :meth:`pokerkit.state.State.get_effective_ante`

  - The actual amount the player is anted. Almost always the full ante amount unless seriously short-stacked.

- Ante poster indices: :attr:`pokerkit.state.State.ante_poster_indices`
- Effective blind/straddle: :meth:`pokerkit.state.State.get_effective_blind_or_straddle`

  - The actual amount the player is blinded or straddled. Almost always the full blind/straddle amount unless seriously short-stacked.

- Blind/straddle poster indices: :attr:`pokerkit.state.State.blind_or_straddle_poster_indices`
- Available cards to be dealt: :attr:`pokerkit.state.State.available_cards`
- Next default hole dealee: :attr:`pokerkit.state.State.hole_dealee_index`
- Next stander pat or discarder: :attr:`pokerkit.state.State.stander_pat_or_discarder_index`
- Next actor (fold, check, ...): :attr:`pokerkit.state.State.actor_index`
- Effective stack: :attr:`pokerkit.state.State.get_effective_stack`
- Checking/Calling amount: :attr:`pokerkit.state.State.checking_or_calling_amount`
- Effective bring-in amount: :attr:`pokerkit.state.State.effective_bring_in_amount`
- Min completion/bet/raise to amount: :attr:`pokerkit.state.State.min_completion_betting_or_raising_to_amount`
- Pot completion/bet/raise to amount: :attr:`pokerkit.state.State.pot_completion_betting_or_raising_to_amount`
- Max completion/bet/raise to amount: :attr:`pokerkit.state.State.max_completion_betting_or_raising_to_amount`
- Person who is in showdown: :attr:`pokerkit.state.State.showdown_index`
- Indices of players who cannot win and whose hand is about to be killed: :attr:`pokerkit.state.State.hand_killing_indices`
- Players who won but have not taken back the chips into their stack yet: :attr:`pokerkit.state.State.chips_pulling_indices`

After each operation is performed, a description of which player was involved, what was the amount, what card was burnt, what cards were dealt, how much bets were collected, et cetera are returned. The types of these are as shown:

- Ante posting: :class:`pokerkit.state.AntePosting`
- Bet collection: :class:`pokerkit.state.BetCollection`
- Blind/straddle posting: :class:`pokerkit.state.BlindOrStraddlePosting`
- Card burning: :class:`pokerkit.state.CardBurning`
- Hole dealing: :class:`pokerkit.state.HoleDealing`
- Board dealing: :class:`pokerkit.state.BoardDealing`
- Standing pat/discarding: :class:`pokerkit.state.StandingPatOrDiscarding`
- Folding: :class:`pokerkit.state.Folding`
- Checking/calling: :class:`pokerkit.state.CheckingOrCalling`
- Bring-in posting: :class:`pokerkit.state.BringInPosting`
- Completion/betting/raising to:
  :class:`pokerkit.state.CompletionBettingOrRaisingTo`
- Hole cards showing/mucking:
  :class:`pokerkit.state.HoleCardsShowingOrMucking`
- Hand killing: :class:`pokerkit.state.HandKilling`
- Chips pushing: :class:`pokerkit.state.ChipsPushing`
- Chips pulling: :class:`pokerkit.state.ChipsPulling`

Again, if an operation is not valid, errors will be raised. PokerKit’s philosophy is that it should focus on maintaining the game state and enforcing rules. Error handling is left to the user, who may need to handle errors differently depending on the application. All the errors raised are ``ValueError``.

Errors versus Warnings
^^^^^^^^^^^^^^^^^^^^^^

As mentioned, when an invalid operation is carried out, PokerKit raises a ``ValueError``. What is an invalid operation? Simply put, it is something that violates the rules. Many of the rules are laid out through the definition of the poker state through the streets where we specify min-bet/raise, the number of bets/raises possible, et cetera. While poker is a diverse game with different rules across regions, we follow the rules set in the `2023 WSOP Tournament Rules <_static/2023-WSOP-Tournament-Rules.pdf>`_.

Warnings are shown when an operation does something sketchy with the cards. Various dealing methods (hole, board, burning) allow the user to specify what cards to deal. In such a scenario, the user may deal a card that is not in the deck that has already been dealt, mucked, burnt, et cetera. Since it is a hassle to check this, we allow the user to deal cards that should not be dealt. The user can configure Python to treat UserWarning as an error. Should this be the case, PokerKit's action query methods will handle it when returning a Boolean value. Note that this is particularly important when the user configures card burning to be automated but does not automate board or hole dealings. Since the user may pass in cards that are burnt, there may be strange warning messages. As such, when any dealing is not automated, card burning, too, should not be automated and the unknown card, denoted as ``"??"`` should be supplied as the burnt card.

Automating without Automating
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For casino use cases, it might be better not to use any automation and handle each operation step by step and display to the players the state at each snapshot of the state. For such a purpose, one might modify the code below.

.. code-block:: python

   from pokerkit import *

   state = ...

   while state.status:
       if state.can_post_ante():
           state.post_ante()
       elif state.can_collect_bets():
           state.collect_bets()
       elif state.can_post_blind_or_straddle():
           state.post_blind_or_straddle()
       elif state.can_burn_card():
           state.burn_card('??')
       elif state.can_deal_hole():
           state.deal_hole()
       elif state.can_deal_board():
           state.deal_board()
       elif state.can_kill_hand():
           state.kill_hand()
       elif state.can_push_chips():
           state.push_chips()
       elif state.can_pull_chips():
           state.pull_chips()
       else:
           action = ...  # standing pat, discarding, folding, checking, etc.

           parse_action(state, action)

The default dealing behavior is quite convenient for casinos. Each time the hole card dealing method is called, only a single hole card is dealt. The first player dealt is the player in the first position, and so on. The dealings go around until all players are dealt. If each player is dealt 4 hole cards (Omaha), the hole dealing function must be called 4 times the number of players. However, when it is a draw stage, a single call deals the necessary number of cards to replace the drawn cards by a player. The order is, again, based on position. Therefore, in the draw stages, the number of times the hole dealing method is called is equal to the number of players who discarded at least one card. A single board dealing method deals all the necessary cards at once (3 for flop, 1 for turn, et cetera).

State Attributes
----------------

PokerKit's poker simulations are architected around the concept of states, encapsulating all the vital information about the current game through its attributes.

- **Cards in deck**: :attr:`pokerkit.state.State.deck_cards`
- **Community cards**: :attr:`pokerkit.state.State.board_cards`
- **Cards in muck**: :attr:`pokerkit.state.State.mucked_cards`
- **Burn cards (if the user wants to, they can also deal burnt cards)**:
  :attr:`pokerkit.state.State.burn_cards`
- **Player statuses (are they still in?)**:
  :attr:`pokerkit.state.State.statuses`
- **Bets**: :attr:`pokerkit.state.State.bets`
- **Stacks**: :attr:`pokerkit.state.State.stacks`
- **Hole cards**: :attr:`pokerkit.state.State.hole_cards`
- **Hole card statuses (up or down?)**:
  :attr:`pokerkit.state.State.hole_card_statuses`
- **Street index**: :attr:`pokerkit.state.State.street_index`
- **Status (is the game over?)**: :attr:`pokerkit.state.State.status`
- **Total pot amount**: :attr:`pokerkit.state.State.total_pot_amount`
- **Pots (main + all sides)**: :attr:`pokerkit.state.State.pots`
- And more...

There are more, such as the initial game parameters and attributes that keep track of who is in turn, what phase the game is in, and et cetera. You can look at :class:`pokerkit.state.State` for a comprehensive list.

Examples
--------

Now, let's look at some sample interactions.

Below is a simple interaction.

**An example hand in fixed-limit Texas hold'em.**

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitTexasHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.CARD_BURNING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     2,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('AcAs')
   HoleDealing(player_index=0, cards=(Ac, As), statuses=(False, False))
   >>> state.deal_hole('7h6h')
   HoleDealing(player_index=1, cards=(7h, 6h), statuses=(False, False))

   >>> state.complete_bet_or_raise_to()
   CompletionBettingOrRaisingTo(player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()
   CompletionBettingOrRaisingTo(player_index=0, amount=6)
   >>> state.fold()
   Folding(player_index=1)

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [204, 196]

**The first televised million-dollar pot between Tom Dwan and Phil
Ivey.**

Link: https://youtu.be/GnxFohpljqM

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = NoLimitTexasHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     500,
   ...     (1000, 2000),
   ...     2000,
   ...     (1125600, 2000000, 553500),
   ...     3,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Ac2d')  # Ivey
   HoleDealing(player_index=0, cards=(Ac, 2d), statuses=(False, False))
   >>> state.deal_hole('????')  # Antonius
   HoleDealing(player_index=1, cards=(??, ??), statuses=(False, False))
   >>> state.deal_hole('7h6h')  # Dwan
   HoleDealing(player_index=2, cards=(7h, 6h), statuses=(False, False))

   >>> state.complete_bet_or_raise_to(7000)  # Dwan
   CompletionBettingOrRaisingTo(player_index=2, amount=7000)
   >>> state.complete_bet_or_raise_to(23000)  # Ivey
   CompletionBettingOrRaisingTo(player_index=0, amount=23000)
   >>> state.fold()  # Antonius
   Folding(player_index=1)
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(player_index=2, amount=16000)

Below are the flop dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('Jc3d5c')
   BoardDealing(cards=(Jc, 3d, 5c))

   >>> state.complete_bet_or_raise_to(35000)  # Ivey
   CompletionBettingOrRaisingTo(player_index=0, amount=35000)
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(player_index=2, amount=35000)

Below are the turn dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('4h')
   BoardDealing(cards=(4h,))

   >>> state.complete_bet_or_raise_to(90000)  # Ivey
   CompletionBettingOrRaisingTo(player_index=0, amount=90000)
   >>> state.complete_bet_or_raise_to(232600)  # Dwan
   CompletionBettingOrRaisingTo(player_index=2, amount=232600)
   >>> state.complete_bet_or_raise_to(1067100)  # Ivey
   CompletionBettingOrRaisingTo(player_index=0, amount=1067100)
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(player_index=2, amount=262400)

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('Jh')
   BoardDealing(cards=(Jh,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [572100, 1997500, 1109500]

**An all-in hand between Xuan and Phua.**

Link: https://youtu.be/QlgCcphLjaQ

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = NoLimitShortDeckHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     3000,
   ...     {-1: 3000},
   ...     3000,
   ...     (495000, 232000, 362000, 403000, 301000, 204000),
   ...     6,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Th8h')  # Badziakouski
   HoleDealing(player_index=0, cards=(Th, 8h), statuses=(False, False))
   >>> state.deal_hole('QsJd')  # Zhong
   HoleDealing(player_index=1, cards=(Qs, Jd), statuses=(False, False))
   >>> state.deal_hole('QhQd')  # Xuan
   HoleDealing(player_index=2, cards=(Qh, Qd), statuses=(False, False))
   >>> state.deal_hole('8d7c')  # Jun
   HoleDealing(player_index=3, cards=(8d, 7c), statuses=(False, False))
   >>> state.deal_hole('KhKs')  # Phua
   HoleDealing(player_index=4, cards=(Kh, Ks), statuses=(False, False))
   >>> state.deal_hole('8c7h')  # Koon
   HoleDealing(player_index=5, cards=(8c, 7h), statuses=(False, False))

   >>> state.check_or_call()  # Badziakouski
   CheckingOrCalling(player_index=0, amount=3000)
   >>> state.check_or_call()  # Zhong
   CheckingOrCalling(player_index=1, amount=3000)
   >>> state.complete_bet_or_raise_to(35000)  # Xuan
   CompletionBettingOrRaisingTo(player_index=2, amount=35000)
   >>> state.fold()  # Jun
   Folding(player_index=3)
   >>> state.complete_bet_or_raise_to(298000)  # Phua
   CompletionBettingOrRaisingTo(player_index=4, amount=298000)
   >>> state.fold()  # Koon
   Folding(player_index=5)
   >>> state.fold()  # Badziakouski
   Folding(player_index=0)
   >>> state.fold()  # Zhong
   Folding(player_index=1)
   >>> state.check_or_call()  # Xuan
   CheckingOrCalling(player_index=2, amount=263000)

Below is the flop dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('9h6cKc')
   BoardDealing(cards=(9h, 6c, Kc))

Below is the turn dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('Jh')
   BoardDealing(cards=(Jh,))

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('Ts')
   BoardDealing(cards=(Ts,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [489000, 226000, 684000, 400000, 0, 198000]

**The largest online poker pot ever played between Patrik Antonius and Viktor Blom.**

Link: https://youtu.be/UMBm66Id2AA

.. code-block:: pycon

   >>> state = PotLimitOmahaHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (500, 1000),
   ...     2000,
   ...     (1259450.25, 678473.5),
   ...     2,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Ah3sKsKh')  # Antonius  # doctest: +ELLIPSIS
   HoleDealing(player_index=0, cards=(Ah, 3s, Ks, Kh), statuses=(False,...
   >>> state.deal_hole('6d9s7d8h')  # Blom  # doctest: +ELLIPSIS
   HoleDealing(player_index=1, cards=(6d, 9s, 7d, 8h), statuses=(False,...

   >>> state.complete_bet_or_raise_to(3000)  # Blom
   CompletionBettingOrRaisingTo(player_index=1, amount=3000)
   >>> state.complete_bet_or_raise_to(9000)  # Antonius
   CompletionBettingOrRaisingTo(player_index=0, amount=9000)
   >>> state.complete_bet_or_raise_to(27000)  # Blom
   CompletionBettingOrRaisingTo(player_index=1, amount=27000)
   >>> state.complete_bet_or_raise_to(81000)  # Antonius
   CompletionBettingOrRaisingTo(player_index=0, amount=81000)
   >>> state.check_or_call()  # Blom
   CheckingOrCalling(player_index=1, amount=54000)

Below are the flop dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('4s5c2h')
   BoardDealing(cards=(4s, 5c, 2h))

   >>> state.complete_bet_or_raise_to(91000)  # Antonius
   CompletionBettingOrRaisingTo(player_index=0, amount=91000)
   >>> state.complete_bet_or_raise_to(435000)  # Blom
   CompletionBettingOrRaisingTo(player_index=1, amount=435000)
   >>> state.complete_bet_or_raise_to(779000)  # Antonius
   CompletionBettingOrRaisingTo(player_index=0, amount=779000)
   >>> state.check_or_call()  # Blom
   CheckingOrCalling(player_index=1, amount=162473.5)

Below is the turn dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('5h')
   BoardDealing(cards=(5h,))

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_board('9c')
   BoardDealing(cards=(9c,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [1937923.75, 0.0]

**A bad beat between Yockey and Arieh.**

Link: https://youtu.be/pChCqb2FNxY

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (75000, 150000),
   ...     150000,
   ...     300000,
   ...     (1180000, 4340000, 5910000, 10765000),
   ...     4,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('7h6c4c3d2c')  # Yockey  # doctest: +ELLIPSIS
   HoleDealing(player_index=0, cards=(7h, 6c, 4c, 3d, 2c), statuses=(Fa...
   >>> state.deal_hole('??????????')  # Hui  # doctest: +ELLIPSIS
   HoleDealing(player_index=1, cards=(??, ??, ??, ??, ??), statuses=(Fa...
   >>> state.deal_hole('??????????')  # Esposito  # doctest: +ELLIPSIS
   HoleDealing(player_index=2, cards=(??, ??, ??, ??, ??), statuses=(Fa...
   >>> state.deal_hole('AsQs6s5c3c')  # Arieh  # doctest: +ELLIPSIS
   HoleDealing(player_index=3, cards=(As, Qs, 6s, 5c, 3c), statuses=(Fa...

   >>> state.fold()  # Esposito
   Folding(player_index=2)
   >>> state.complete_bet_or_raise_to()  # Arieh
   CompletionBettingOrRaisingTo(player_index=3, amount=300000)
   >>> state.complete_bet_or_raise_to()  # Yockey
   CompletionBettingOrRaisingTo(player_index=0, amount=450000)
   >>> state.fold()  # Hui
   Folding(player_index=1)
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(player_index=3, amount=150000)

Below are the first draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('AsQs')  # Arieh
   StandingPatOrDiscarding(player_index=3, cards=(As, Qs))
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('2hQh')  # Arieh
   HoleDealing(player_index=3, cards=(2h, Qh), statuses=(False, False))

   >>> state.complete_bet_or_raise_to()  # Yockey
   CompletionBettingOrRaisingTo(player_index=0, amount=150000)
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(player_index=3, amount=150000)

Below are the second draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('Qh')  # Arieh
   StandingPatOrDiscarding(player_index=3, cards=(Qh,))
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('4d')  # Arieh
   HoleDealing(player_index=3, cards=(4d,), statuses=(False,))

   >>> state.complete_bet_or_raise_to()  # Yockey
   CompletionBettingOrRaisingTo(player_index=0, amount=300000)
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(player_index=3, amount=300000)

Below are the third draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('6s')  # Arieh
   StandingPatOrDiscarding(player_index=3, cards=(6s,))
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('7c')  # Arieh
   HoleDealing(player_index=3, cards=(7c,), statuses=(False,))

   >>> state.complete_bet_or_raise_to()  # Yockey
   CompletionBettingOrRaisingTo(player_index=0, amount=280000)
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(player_index=3, amount=280000)

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [0, 4190000, 5910000, 12095000]

**An example badugi hand from Wikipedia.**

Link: https://en.wikipedia.org/wiki/Badugi

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitBadugi.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     4,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('????????')  # Bob  # doctest: +ELLIPSIS
   HoleDealing(player_index=0, cards=(??, ??, ??, ??), statuses=(False,...
   >>> state.deal_hole('????????')  # Carol  # doctest: +ELLIPSIS
   HoleDealing(player_index=1, cards=(??, ??, ??, ??), statuses=(False,...
   >>> state.deal_hole('????????')  # Ted  # doctest: +ELLIPSIS
   HoleDealing(player_index=2, cards=(??, ??, ??, ??), statuses=(False,...
   >>> state.deal_hole('????????')  # Alice  # doctest: +ELLIPSIS
   HoleDealing(player_index=3, cards=(??, ??, ??, ??), statuses=(False,...

   >>> state.fold()  # Ted
   Folding(player_index=2)
   >>> state.check_or_call()  # Alice
   CheckingOrCalling(player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   CheckingOrCalling(player_index=0, amount=1)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(player_index=1, amount=0)

Below are the first draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('????')  # Bob
   StandingPatOrDiscarding(player_index=0, cards=(??, ??))
   >>> state.stand_pat_or_discard('????')  # Carol
   StandingPatOrDiscarding(player_index=1, cards=(??, ??))
   >>> state.stand_pat_or_discard('??')  # Alice
   StandingPatOrDiscarding(player_index=3, cards=(??,))
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('????')  # Bob
   HoleDealing(player_index=0, cards=(??, ??), statuses=(False, False))
   >>> state.deal_hole('????')  # Carol
   HoleDealing(player_index=1, cards=(??, ??), statuses=(False, False))
   >>> state.deal_hole('??')  # Alice
   HoleDealing(player_index=3, cards=(??,), statuses=(False,))

   >>> state.check_or_call()  # Bob
   CheckingOrCalling(player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   CompletionBettingOrRaisingTo(player_index=1, amount=2)
   >>> state.check_or_call()  # Alice
   CheckingOrCalling(player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   CheckingOrCalling(player_index=0, amount=2)

Below are the second draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('??')  # Bob
   StandingPatOrDiscarding(player_index=0, cards=(??,))
   >>> state.stand_pat_or_discard()  # Carol
   StandingPatOrDiscarding(player_index=1, cards=())
   >>> state.stand_pat_or_discard('??')  # Alice
   StandingPatOrDiscarding(player_index=3, cards=(??,))
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('??')  # Bob
   HoleDealing(player_index=0, cards=(??,), statuses=(False,))
   >>> state.deal_hole('??')  # Alice
   HoleDealing(player_index=3, cards=(??,), statuses=(False,))

   >>> state.check_or_call()  # Bob
   CheckingOrCalling(player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   CompletionBettingOrRaisingTo(player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()  # Alice
   CompletionBettingOrRaisingTo(player_index=3, amount=8)
   >>> state.fold()  # Bob
   Folding(player_index=0)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(player_index=1, amount=4)

Below are the third draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('??')  # Carol
   StandingPatOrDiscarding(player_index=1, cards=(??,))
   >>> state.stand_pat_or_discard()  # Alice
   StandingPatOrDiscarding(player_index=3, cards=())
   >>> state.burn_card('??')
   CardBurning(card=??)
   >>> state.deal_hole('??')  # Carol
   HoleDealing(player_index=1, cards=(??,), statuses=(False,))

   >>> state.check_or_call()  # Carol
   CheckingOrCalling(player_index=1, amount=0)
   >>> state.complete_bet_or_raise_to()  # Alice
   CompletionBettingOrRaisingTo(player_index=3, amount=4)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(player_index=1, amount=4)

Below is the showdown.

.. code-block:: pycon

   >>> state.show_or_muck_hole_cards('2s4c6d9h')  # Alice
   HoleCardsShowingOrMucking(player_index=3, hole_cards=(2s, 4c, 6d, 9h))
   >>> state.show_or_muck_hole_cards('3s5d7c8h')  # Carol
   HoleCardsShowingOrMucking(player_index=1, hole_cards=(3s, 5d, 7c, 8h))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [196, 220, 200, 184]

There are more example hands in the unit tests. Please take a look at the repository to learn more.
