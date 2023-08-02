Poker Simulation
================

``PokerKit`` is a very powerful tool you can use to simulate games. It allow
you to play any poker games and modify the state at any level. It also gives
you handy programmatic API to query if you can do something or get information
such as maximum completion/betting/raising to amount, or checking/calling
amount.

All poker games progresses as follows:

1. Ante posting
2. Bet collection (if anyone anted)
3. Blind/straddle posting
4. Dealing (if hand is still on) (burning card, hole, board, stand pat or
   discard)
5. Betting (if hand is still on and people are not all in) (fold, check, call,
   bring-in, complete, bet, raise to)
6. Bet collection (if anyone bet)
7. Go back to Step 4 if any street remains and the hand is on
8. Showdown (if there are still people in the pot)
9. Hand killing (if anyone has shown hands that cannot win anything)
10. Chips pushing (move chips from center to the winner(s))
11. Chips pulling (winner(s) pull the chips they won into the pot)

Depending on the use cases, many of these phases can be automated without any
user input, as user can specify which operations they want to be manual and
automatic.

Initialization
--------------

``PokerKit`` offers virtually unlimited poker variants to be played. However,
defining poker variants can be quite an overwhelming task for a new user. We
offer pre-defined poker variants where user can just supply arguments such as
antes, blinds, starting stacks, et cetera.

Pre-defined poker variants:

- Fixed-limit badugi: :class:`pokerkit.games.FixedLimitBadugi`
- Fixed-limit deuce-to-seven lowball triple draw:
  :class:`pokerkit.games.FixedLimitDeuceToSevenLowballTripleDraw`
- Fixed-limit Omaha hold'em hi-low split-eight or better low:
  :class:`pokerkit.games.FixedLimitOmahaHoldemHighLowSplitEightOrBetter`
- Fixed-limit razz: :class:`pokerkit.games.FixedLimitRazz`
- Fixed-limit seven card stud: :class:`pokerkit.games.FixedLimitSevenCardStud`
- Fixed-limit seven card stud hi-low split-eight or better low:
  :class:`pokerkit.games.FixedLimitSevenCardStudHighLowSplitEightOrBetter`
- Fixed-limit Texas hold'em: :class:`pokerkit.games.FixedLimitTexasHoldem`
- No-limit deuce-to-seven single draw:
  :class:`pokerkit.games.NoLimitDeuceToSevenLowballSingleDraw`
- No-limit short-deck hold'em: :class:`pokerkit.games.NoLimitShortDeckHoldem`
- No-limit Texas hold'em: :class:`pokerkit.games.NoLimitTexasHoldem`
- Pot-limit Omaha hold'em: :class:`pokerkit.games.PotLimitOmahaHoldem`

Not finding what you are looking for? Define your own or create an issue!

They can be created as shown below:

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
           Automation.CHIP_PUSHING,
           Automation.CHIP_PULLING,
       ),
       True,  # False for big blind ante, True otherwise
       None,  # ante
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
           Automation.CHIP_PUSHING,
           Automation.CHIP_PULLING,
       ),
       True,  # False for big blind ante, True otherwise
       500,  # ante
       (1000, 2000),  # blinds or straddles
       2000,  # min bet
       (1125600, 2000000, 553500),  # starting stacks
       3,  # number of players
   )

You can define your own variant as shown below:

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
       # deck
       Deck.KUHN_POKER,
       # hand types (high/low-split will have two types)
       (KuhnPokerHand,),
       # streets
       (
           Street(
               False,  # card burning
               (False,),  # hole card dealing statuses (False for face-down)
               0,  # board dealing card
               False,  # standing pat or discarding
               Opening.POSITION,  # who opens the betting?
               1,  # min bet
               None,  # maximum number of completions/bettings/raisings
           ),
       ),
       # betting structure
       BettingStructure.FIXED_LIMIT,
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
       # False for big blind ante, otherwise True
       True,
       # ante
       (1,) * 2,
       # blind or straddles
       (0,) * 2,
       # bring-in
       0,
       # starting stacks
       (2,) * 2,
   )

There is a lot to specify and you will have to experiment to get it right.

These are two different ways to create a state. Now that we have a state, we
can play around with it!

Attributes
----------

You can access various things about the state by accessing the following
attributes and methods.

- Cards in deck: :attr:`pokerkit.state.State.deck_cards`
- Community cards: :attr:`pokerkit.state.State.board_cards`
- Cards in muck: :attr:`pokerkit.state.State.mucked_cards`
- Burned cards (if user wants to, they can also deal burnt cards):
  :attr:`pokerkit.state.State.burned_cards`
- Player statuses (are they still in?): :attr:`pokerkit.state.State.statuses`
- Bets: :attr:`pokerkit.state.State.bets`
- Stacks: :attr:`pokerkit.state.State.stacks`
- Hole cards: :attr:`pokerkit.state.State.hole_cards`
- Hole card statuses (up or down?):
  :attr:`pokerkit.state.State.hole_card_statuses`
- Street index: :attr:`pokerkit.state.State.street_index`
- Status (is the game over?): :attr:`pokerkit.state.State.status`
- Total pot amount: :attr:`pokerkit.state.State.total_pot_amount`
- Pots (main + all sides): :attr:`pokerkit.state.State.pots`

There are more, such as the initial game parameters and attributes that keep
track of who is acting, et cetera. You can look at :class:`pokerkit.state.State`
for a complete list.

Operations
----------

The wide selection you have is not the only thing that will overwhelm you. We
also offer fine-grained poker state modifications. Depending on your use case,
many of our operations will not be of concern.

All operations:

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
- Completion/betting/raising to:
  :meth:`pokerkit.state.State.complete_bet_or_raise_to`
- Hole cards showing/mucking:
  :meth:`pokerkit.state.State.show_or_muck_hole_cards`
- Hand killing: :meth:`pokerkit.state.State.kill_hand`
- Chips pushing: :meth:`pokerkit.state.State.push_chips`
- Chips pulling: :meth:`pokerkit.state.State.pull_chips`

For example, if you are trying to create a poker AI, you are not worried about
mucking the best hand or showing the worse hand, burning a card, pushing the
chips to the winners, collecting chips a player won, collecting bets after each
street, et cetera. But, you want to handle user actions like fold, check, call,
bring-in, complete, bet, and raise. Also, you might want to control what cards
are dealt to each player and to the board.

However, if you are trying to create an online poker room, you need all these
fine changes to create smooth user experience. Although, you might not be
concerned about exactly what cards are dealt. You would be happy with cards
being dealt at random (hopefully).

``PokerKit`` allow you to specify what you are worried about, and what you are
not worried about. :class:`pokerkit.state.Automation` describes operations that
can be automated.

Sample automations:

.. code-block:: python

   from pokerkit import Automation

   # automate everything except actions
   automations = (
       Automation.ANTE_POSTING,
       Automation.BET_COLLECTION,
       Automation.BLIND_OR_STRADDLE_POSTING,
       Automation.CARD_BURNING,
       Automation.HOLE_DEALING,
       Automation.BOARD_DEALING,
       Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
       Automation.HAND_KILLING,
       Automation.CHIP_PUSHING,
       Automation.CHIP_PULLING,
   )

   # Automate everything except actions and dealings
   automations = (
       Automation.ANTE_POSTING,
       Automation.BET_COLLECTION,
       Automation.BLIND_OR_STRADDLE_POSTING,
       Automation.CARD_BURNING,
       Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
       Automation.HAND_KILLING,
       Automation.CHIP_PUSHING,
       Automation.CHIP_PULLING,
   )

   # Automate nothing
   automations = ()

Now, let's say you know what operations you should worry about. How do you know
when to invoke them? PokerKit has handy methods to query whether you can perform
an operation:

- Ante posting?: :meth:`pokerkit.state.State.can_post_ante`
- Bet collection?: :meth:`pokerkit.state.State.can_collect_bets`
- Blind/straddle posting?: :meth:`pokerkit.state.State.can_post_blind_or_straddle`
- Card burning?: :meth:`pokerkit.state.State.can_burn_card`
- Hole dealing?: :meth:`pokerkit.state.State.can_deal_hole`
- Board dealing?: :meth:`pokerkit.state.State.can_deal_board`
- Standing pat/discarding?: :meth:`pokerkit.state.State.can_stand_pat_or_discard`
- Folding?: :meth:`pokerkit.state.State.can_fold`
- Checking/calling?: :meth:`pokerkit.state.State.can_check_or_call`
- Bring-in posting?: :meth:`pokerkit.state.State.can_post_bring_in`
- Completion/betting/raising to?:
  :meth:`pokerkit.state.State.can_complete_bet_or_raise_to`
- Hole cards showing/mucking?:
  :meth:`pokerkit.state.State.can_show_or_muck_hole_cards`
- Hand killing?: :meth:`pokerkit.state.State.can_kill_hand`
- Chips pushing?: :meth:`pokerkit.state.State.can_push_chips`
- Chips pulling?: :meth:`pokerkit.state.State.can_pull_chips`

These methods return ``True`` if you can perform such an operation (with
specified arguments, if any)  or ``False`` if otherwise.

Most of the operations can optionally accept arguments. Some are more important
than others. Let's see what we can specify for each action.

- Ante posting: player_index, defaults to first player who did not post ante
- Bet collection: N/A
- Blind/straddle posting: player_index, defaults to first player who did not
  post the blind or straddle
- Card burning: card, defaults to randomly drawing from the deck
- Hole dealing: cards, defaults to randomly drawing a single card from the deck
- Board dealing: cards, defaults to randomly drawing required cards from the deck
- Standing pat/discarding: cards, defaults to standing pat
- Folding: N/A
- Checking/calling: N/A
- Bring-in posting: N/A
- Completion/betting/raising to: amount, defaults to completion, min-bet, or
  min-raise
- Hole cards showing/mucking: status, defaults to showing only when no-one else
  has shown a better hand
- Hand killing: player_index, defaults to the first player who cannot win any
                portion of the pot
- Chips pushing: N/A
- Chips pulling: player_index, defaults to the first player who won a portion of
                 the pot

How do you know what the minimum bets are? How do you know to whom the hole card
will be dealt next? How do you know the call amount? Whose action is it? You can
access all these information through the following methods or properties

- Effective ante: :meth:`poker.state.State.get_effective_ante`
- Ante poster indices: :attr:`poker.state.State.ante_poster_indices`
- Effective blind/straddle:
  :meth:`poker.state.State.get_effective_blind_or_straddle`
- Blind/straddle poster indices:
  :attr:`poker.state.State.blind_or_straddle_poster_indices`
- Available cards to be dealt: :attr:`poker.state.State.available_cards`
- Next default hole dealee: :attr:`poker.state.State.hole_dealee_index`
- Next stander pat or discarder:
  :attr:`poker.state.State.stander_pat_or_discarder_index`
- Next actor (fold, check, ...): :attr:`poker.state.State.actor_index`
- Effective stack:  :attr:`poker.state.State.get_effective_stack`
- Checking/Calling amount: :attr:`poker.state.State.checking_or_calling_amount`
- Effective bring-in amount: :attr:`poker.state.State.effective_bring_in_amount`
- Min completion/bet/raise to amount:
  :attr:`poker.state.State.min_completion_betting_or_raising_to_amount`
- Pot completion/bet/raise to amount:
  :attr:`poker.state.State.pot_completion_betting_or_raising_to_amount`
- Max completion/bet/raise to amount:
  :attr:`poker.state.State.max_completion_betting_or_raising_to_amount`
- Person who is in showdown: :attr:`poker.state.State.showdown_index`
- Indices of players who cannot win and whose hand is about to be killed:
  :attr:`poker.state.State.hand_killing_indices`
- Players who won but has not taken back the chips into their stack yet:
  :attr:`poker.state.State.chips_pulling_indices``

After each action is performed, description of which player was involved,
what was the amount, what card was burnt, what cards were dealt, how much bets
were collected, et cetera are returned. The types of these are as shown:

- Ante posting: :class:`pokerkit.state.State.AntePosting`
- Bet collection: :class:`pokerkit.state.State.BetCollection`
- Blind/straddle posting: :class:`pokerkit.state.State.BlindOrStraddlePosting`
- Card burning: :class:`pokerkit.state.State.CardBurning`
- Hole dealing: :class:`pokerkit.state.State.HoleDealing`
- Board dealing: :class:`pokerkit.state.State.BoardDealing`
- Standing pat/discarding: :class:`pokerkit.state.State.StandingPatOrDiscarding`
- Folding: :class:`pokerkit.state.State.Folding`
- Checking/calling: :class:`pokerkit.state.State.CheckingOrCalling`
- Bring-in posting: :class:`pokerkit.state.State.BringInPosting`
- Completion/betting/raising to:
  :class:`pokerkit.state.State.CompletionBettingOrRaisingTo`
- Hole cards showing/mucking:
  :class:`pokerkit.state.State.HoleCardsShowingOrMucking`
- Hand killing: :class:`pokerkit.state.State.HandKilling`
- Chips pushing: :class:`pokerkit.state.State.ChipsPushing`
- Chips pulling: :class:`pokerkit.state.State.ChipsPulling`

Interactions
------------

Now, let's look at some sample interactions!

This is a simple interaction.

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
   ...     None,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     2,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('AcAs')
   State.HoleDealing(player_index=0, cards=(Ac, As), statuses=(False, False))
   >>> state.deal_hole('7h6h')
   State.HoleDealing(player_index=1, cards=(7h, 6h), statuses=(False, False))
   >>> state.complete_bet_or_raise_to()
   State.CompletionBettingOrRaisingTo(player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()
   State.CompletionBettingOrRaisingTo(player_index=0, amount=6)
   >>> state.fold()
   State.Folding(player_index=1)
   >>> # Below show the final stacks.
   >>> state.stacks
   [204, 196]

Below shows the first televised million dollar pot between Tom Dwan and Phil
Ivey.

Link: https://youtu.be/GnxFohpljqM

.. code-block:: pycon

   >>> state = NoLimitTexasHoldem.create_state(
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
   ...     500,
   ...     (1000, 2000),
   ...     2000,
   ...     (1125600, 2000000, 553500),
   ...     3,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('Ac2d')  # Ivey
   State.HoleDealing(player_index=0, cards=(Ac, 2d), statuses=(False, False))
   >>> state.deal_hole('5h7s')  # Antonius*
   State.HoleDealing(player_index=1, cards=(5h, 7s), statuses=(False, False))
   >>> state.deal_hole('7h6h')  # Dwan
   State.HoleDealing(player_index=2, cards=(7h, 6h), statuses=(False, False))
   >>> state.complete_bet_or_raise_to(7000)  # Dwan
   State.CompletionBettingOrRaisingTo(player_index=2, amount=7000)
   >>> state.complete_bet_or_raise_to(23000)  # Ivey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=23000)
   >>> state.fold()  # Antonius
   State.Folding(player_index=1)
   >>> state.check_or_call()  # Dwan
   State.CheckingOrCalling(player_index=2, amount=16000)
   >>> # Below shows the flop dealing and actions.
   >>> state.deal_board('Jc3d5c')
   State.BoardDealing(cards=(Jc, 3d, 5c))
   >>> state.complete_bet_or_raise_to(35000)  # Ivey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=35000)
   >>> state.check_or_call()  # Dwan
   State.CheckingOrCalling(player_index=2, amount=35000)
   >>> # Below shows the turn dealing and actions.
   >>> state.deal_board('4h')
   State.BoardDealing(cards=(4h,))
   >>> state.complete_bet_or_raise_to(90000)  # Ivey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=90000)
   >>> state.complete_bet_or_raise_to(232600)  # Dwan
   State.CompletionBettingOrRaisingTo(player_index=2, amount=232600)
   >>> state.complete_bet_or_raise_to(1067100)  # Ivey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=1067100)
   >>> state.check_or_call()  # Dwan
   State.CheckingOrCalling(player_index=2, amount=262400)
   >>> # Below shows the river dealing.
   >>> state.deal_board('Jh')
   State.BoardDealing(cards=(Jh,))
   >>> # Below show the final stacks.
   >>> state.stacks
   [572100, 1997500, 1109500]

Below shows an all-in hand between Xuan and Phua.

Link: https://youtu.be/QlgCcphLjaQ

.. code-block:: pycon

   >>> state = NoLimitShortDeckHoldem.create_state(
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
   ...     3000,
   ...     {-1: 3000},
   ...     3000,
   ...     (495000, 232000, 362000, 403000, 301000, 204000),
   ...     6,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('Th8h')  # Badziakouski
   State.HoleDealing(player_index=0, cards=(Th, 8h), statuses=(False, False))
   >>> state.deal_hole('QsJd')  # Zhong
   State.HoleDealing(player_index=1, cards=(Qs, Jd), statuses=(False, False))
   >>> state.deal_hole('QhQd')  # Xuan
   State.HoleDealing(player_index=2, cards=(Qh, Qd), statuses=(False, False))
   >>> state.deal_hole('8d7c')  # Jun
   State.HoleDealing(player_index=3, cards=(8d, 7c), statuses=(False, False))
   >>> state.deal_hole('KhKs')  # Phua
   State.HoleDealing(player_index=4, cards=(Kh, Ks), statuses=(False, False))
   >>> state.deal_hole('8c7h')  # Koon
   State.HoleDealing(player_index=5, cards=(8c, 7h), statuses=(False, False))
   >>> state.check_or_call()  # Badziakouski
   State.CheckingOrCalling(player_index=0, amount=3000)
   >>> state.check_or_call()  # Zhong
   State.CheckingOrCalling(player_index=1, amount=3000)
   >>> state.complete_bet_or_raise_to(35000)  # Xuan
   State.CompletionBettingOrRaisingTo(player_index=2, amount=35000)
   >>> state.fold()  # Jun
   State.Folding(player_index=3)
   >>> state.complete_bet_or_raise_to(298000)  # Phua
   State.CompletionBettingOrRaisingTo(player_index=4, amount=298000)
   >>> state.fold()  # Koon
   State.Folding(player_index=5)
   >>> state.fold()  # Badziakouski
   State.Folding(player_index=0)
   >>> state.fold()  # Zhong
   State.Folding(player_index=1)
   >>> state.check_or_call()  # Xuan
   State.CheckingOrCalling(player_index=2, amount=263000)
   >>> # Below shows the flop dealing.
   >>> state.deal_board('9h6cKc')
   State.BoardDealing(cards=(9h, 6c, Kc))
   >>> # Below shows the turn dealing.
   >>> state.deal_board('Jh')
   State.BoardDealing(cards=(Jh,))
   >>> # Below shows the river dealing.
   >>> state.deal_board('Ts')
   State.BoardDealing(cards=(Ts,))
   >>> # Below show the final stacks.
   >>> state.stacks
   [489000, 226000, 684000, 400000, 0, 198000]

Below shows the largest online poker pot every played between
Patrik Antonius and Viktor Blom.

Link: https://youtu.be/UMBm66Id2AA

.. code-block:: pycon

   >>> state = PotLimitOmahaHoldem.create_state(
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
   ...     None,
   ...     (50000, 100000),
   ...     2000,
   ...     (125945025, 67847350),
   ...     2,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('Ah3sKsKh')  # Antonius
   State.HoleDealing(player_index=0, cards=(Ah, 3s, Ks, Kh), statuses=(False, False, False, False))
   >>> state.deal_hole('6d9s7d8h')  # Blom
   State.HoleDealing(player_index=1, cards=(6d, 9s, 7d, 8h), statuses=(False, False, False, False))
   >>> state.complete_bet_or_raise_to(300000)  # Blom
   State.CompletionBettingOrRaisingTo(player_index=1, amount=300000)
   >>> state.complete_bet_or_raise_to(900000)  # Antonius
   State.CompletionBettingOrRaisingTo(player_index=0, amount=900000)
   >>> state.complete_bet_or_raise_to(2700000)  # Blom
   State.CompletionBettingOrRaisingTo(player_index=1, amount=2700000)
   >>> state.complete_bet_or_raise_to(8100000)  # Antonius
   State.CompletionBettingOrRaisingTo(player_index=0, amount=8100000)
   >>> state.check_or_call()  # Blom
   State.CheckingOrCalling(player_index=1, amount=5400000)
   >>> # Below shows the flop dealing and actions.
   >>> state.deal_board('4s5c2h')
   State.BoardDealing(cards=(4s, 5c, 2h))
   >>> state.complete_bet_or_raise_to(9100000)  # Antonius
   State.CompletionBettingOrRaisingTo(player_index=0, amount=9100000)
   >>> state.complete_bet_or_raise_to(43500000)  # Blom
   State.CompletionBettingOrRaisingTo(player_index=1, amount=43500000)
   >>> state.complete_bet_or_raise_to(77900000)  # Antonius
   State.CompletionBettingOrRaisingTo(player_index=0, amount=77900000)
   >>> state.check_or_call()  # Blom
   State.CheckingOrCalling(player_index=1, amount=16247350)
   >>> # Below shows the turn dealing.
   >>> state.deal_board('5h')
   State.BoardDealing(cards=(5h,))
   >>> # Below shows the river dealing.
   >>> state.deal_board('9c')
   State.BoardDealing(cards=(9c,))
   >>> # Below show the final stacks.
   >>> state.stacks
   [193792375, 0]

Below shows a bad beat between Yockey and Arieh.

Link: https://youtu.be/pChCqb2FNxY

.. code-block:: pycon

   >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
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
   ...     None,
   ...     (75000, 150000),
   ...     150000,
   ...     300000,
   ...     (1180000, 4340000, 5910000, 10765000),
   ...     4,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('7h6c4c3d2c')  # Yockey
   State.HoleDealing(player_index=0, cards=(7h, 6c, 4c, 3d, 2c), statuses=(False, False, False, False, False))
   >>> state.deal_hole('JsJcJdJhTs')  # Hui*
   State.HoleDealing(player_index=1, cards=(Js, Jc, Jd, Jh, Ts), statuses=(False, False, False, False, False))
   >>> state.deal_hole('KsKcKdKhTh')  # Esposito*
   State.HoleDealing(player_index=2, cards=(Ks, Kc, Kd, Kh, Th), statuses=(False, False, False, False, False))
   >>> state.deal_hole('AsQs6s5c3c')  # Arieh
   State.HoleDealing(player_index=3, cards=(As, Qs, 6s, 5c, 3c), statuses=(False, False, False, False, False))
   >>> state.fold()  # Esposito
   State.Folding(player_index=2)
   >>> state.complete_bet_or_raise_to()  # Arieh
   State.CompletionBettingOrRaisingTo(player_index=3, amount=300000)
   >>> state.complete_bet_or_raise_to()  # Yockey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=450000)
   >>> state.fold()  # Hui
   State.Folding(player_index=1)
   >>> state.check_or_call()  # Arieh
   State.CheckingOrCalling(player_index=3, amount=150000)
   >>> # Below shows the first draw and actions.
   >>> state.stand_pat_or_discard()  # Yockey
   State.StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('AsQs')  # Arieh
   State.StandingPatOrDiscarding(player_index=3, cards=(As, Qs))
   >>> state.deal_hole('2hQh')  # Arieh
   State.HoleDealing(player_index=3, cards=(2h, Qh), statuses=(False, False))
   >>> state.complete_bet_or_raise_to()  # Yockey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=150000)
   >>> state.check_or_call()  # Arieh
   State.CheckingOrCalling(player_index=3, amount=150000)
   >>> # Below shows the second draw and actions.
   >>> state.stand_pat_or_discard()  # Yockey
   State.StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('Qh')  # Arieh
   State.StandingPatOrDiscarding(player_index=3, cards=(Qh,))
   >>> state.deal_hole('4d')  # Arieh
   State.HoleDealing(player_index=3, cards=(4d,), statuses=(False,))
   >>> state.complete_bet_or_raise_to()  # Yockey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=300000)
   >>> state.check_or_call()  # Arieh
   State.CheckingOrCalling(player_index=3, amount=300000)
   >>> # Below shows the third draw and actions.
   >>> state.stand_pat_or_discard()  # Yockey
   State.StandingPatOrDiscarding(player_index=0, cards=())
   >>> state.stand_pat_or_discard('6s')  # Arieh
   State.StandingPatOrDiscarding(player_index=3, cards=(6s,))
   >>> state.deal_hole('7c')  # Arieh
   State.HoleDealing(player_index=3, cards=(7c,), statuses=(False,))
   >>> state.complete_bet_or_raise_to()  # Yockey
   State.CompletionBettingOrRaisingTo(player_index=0, amount=280000)
   >>> state.check_or_call()  # Arieh
   State.CheckingOrCalling(player_index=3, amount=280000)
   >>> # Below show the final stacks.
   >>> state.stacks
   [0, 4190000, 5910000, 12095000]

Below shows an example badugi hand from Wikipedia.

Link: https://en.wikipedia.org/wiki/Badugi

.. code-block:: pycon

   >>> state = FixedLimitBadugi.create_state(
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
   ...     None,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     4,
   ... )
   >>> # Below shows the pre-flop dealings and actions.
   >>> state.deal_hole('As4hJcKh')  # Bob*
   State.HoleDealing(player_index=0, cards=(As, 4h, Jc, Kh), statuses=(False, False, False, False))
   >>> state.deal_hole('3s5d7s8s')  # Carol*
   State.HoleDealing(player_index=1, cards=(3s, 5d, 7s, 8s), statuses=(False, False, False, False))
   >>> state.deal_hole('KsKdQsQd')  # Ted*
   State.HoleDealing(player_index=2, cards=(Ks, Kd, Qs, Qd), statuses=(False, False, False, False))
   >>> state.deal_hole('2s4c6dKc')  # Alice*
   State.HoleDealing(player_index=3, cards=(2s, 4c, 6d, Kc), statuses=(False, False, False, False))
   >>> state.fold()  # Ted
   State.Folding(player_index=2)
   >>> state.check_or_call()  # Alice
   State.CheckingOrCalling(player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   State.CheckingOrCalling(player_index=0, amount=1)
   >>> state.check_or_call()  # Carol
   State.CheckingOrCalling(player_index=1, amount=0)
   >>> # Below shows the first draw and actions.
   >>> state.stand_pat_or_discard('JcKh')  # Bob*
   State.StandingPatOrDiscarding(player_index=0, cards=(Jc, Kh))
   >>> state.stand_pat_or_discard('7s8s')  # Carol*
   State.StandingPatOrDiscarding(player_index=1, cards=(7s, 8s))
   >>> state.stand_pat_or_discard('Kc')  # Alice*
   State.StandingPatOrDiscarding(player_index=3, cards=(Kc,))
   >>> state.deal_hole('TcJs')  # Bob*
   State.HoleDealing(player_index=0, cards=(Tc, Js), statuses=(False, False))
   >>> state.deal_hole('7cTh')  # Carol*
   State.HoleDealing(player_index=1, cards=(7c, Th), statuses=(False, False))
   >>> state.deal_hole('Qc')  # Alice*
   State.HoleDealing(player_index=3, cards=(Qc,), statuses=(False,))
   >>> state.check_or_call()  # Bob
   State.CheckingOrCalling(player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   State.CompletionBettingOrRaisingTo(player_index=1, amount=2)
   >>> state.check_or_call()  # Alice
   State.CheckingOrCalling(player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   State.CheckingOrCalling(player_index=0, amount=2)
   >>> # Below shows the second draw and actions.
   >>> state.stand_pat_or_discard('Js')  # Bob*
   State.StandingPatOrDiscarding(player_index=0, cards=(Js,))
   >>> state.stand_pat_or_discard()  # Carol*
   State.StandingPatOrDiscarding(player_index=1, cards=())
   >>> state.stand_pat_or_discard('Qc')  # Alice*
   State.StandingPatOrDiscarding(player_index=3, cards=(Qc,))
   >>> state.deal_hole('Ts')  # Bob*
   State.HoleDealing(player_index=0, cards=(Ts,), statuses=(False,))
   >>> state.deal_hole('9h')  # Alice*
   State.HoleDealing(player_index=3, cards=(9h,), statuses=(False,))
   >>> state.check_or_call()  # Bob
   State.CheckingOrCalling(player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   State.CompletionBettingOrRaisingTo(player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()  # Alice
   State.CompletionBettingOrRaisingTo(player_index=3, amount=8)
   >>> state.fold()  # Bob
   State.Folding(player_index=0)
   >>> state.check_or_call()  # Carol
   State.CheckingOrCalling(player_index=1, amount=4)
   >>> # Below shows the third draw and actions.
   >>> state.stand_pat_or_discard('Th')  # Carol*
   State.StandingPatOrDiscarding(player_index=1, cards=(Th,))
   >>> state.stand_pat_or_discard()  # Alice*
   State.StandingPatOrDiscarding(player_index=3, cards=())
   >>> state.deal_hole('8h')  # Carol*
   State.HoleDealing(player_index=1, cards=(8h,), statuses=(False,))
   >>> state.check_or_call()  # Carol
   State.CheckingOrCalling(player_index=1, amount=0)
   >>> state.complete_bet_or_raise_to()  # Alice
   State.CompletionBettingOrRaisingTo(player_index=3, amount=4)
   >>> state.check_or_call()  # Carol
   State.CheckingOrCalling(player_index=1, amount=4)
   >>> # Below show the final stacks.
   >>> state.stacks
   [196, 220, 200, 184]

There are more example hands in the unit tests. Please take a look at the
repository to learn more.
