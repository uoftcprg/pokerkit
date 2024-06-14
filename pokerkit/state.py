""":mod:`pokerkit.state` implements classes related to poker states."""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Iterable, Iterator
from collections import Counter, deque
from dataclasses import InitVar, dataclass, field, KW_ONLY
from enum import StrEnum, unique
from functools import partial
from itertools import chain, filterfalse, islice, starmap
from operator import getitem, sub
from random import shuffle
from warnings import warn

from pokerkit.hands import Hand
from pokerkit.lookups import Label, Lookup
from pokerkit.utilities import (
    Card,
    CardsLike,
    clean_values,
    Deck,
    divmod,
    max_or_none,
    min_or_none,
    rake,
    Rank,
    RankOrder,
    shuffled,
    Suit,
    ValuesLike,
)


@unique
class BettingStructure(StrEnum):
    """The enum class for betting structures.

    >>> BettingStructure.FIXED_LIMIT
    <BettingStructure.FIXED_LIMIT: 'Fixed-limit'>
    >>> BettingStructure.NO_LIMIT
    <BettingStructure.NO_LIMIT: 'No-limit'>

    It tells PokerKit what betting limit (e.g. No-Limit, Pot-Limit,
    etc.) the variant uses.

    The limit may set the limitations on the maximum bet/raise amounts.

    Some commentators put cap-limit as possible betting structure, but
    we disagree in this aspect since the "cap-limit" is equivalent to
    simply having lesser starting stack values.

    The number of maximum bet/raises and the min-bet are set by streets'
    :attr:`pokerkit.state.Street.max_completion_betting_or_raising_count`
    attribute.
    """

    FIXED_LIMIT: str = 'Fixed-limit'
    """The fixed-limit.

    Here, min and max amounts are identical.

    Typically, the number of bet/raises permitted is also limited. This
    is not the case in some tournament settings when heads-up play is
    reached.
    """
    POT_LIMIT: str = 'Pot-limit'
    """The pot-limit.

    This limits the bet/raise amount to the pot bet amount, following
    the following formula ``M = (3L + T) + S`` where ``M`` is the
    maximum bet, ``L`` is the last wager, ``T`` is the trail (action
    prior to the previous bet), and ``S`` the starting pot (source:
    https://en.wikipedia.org/wiki/Betting_in_poker).

    The number of bet/raises is typically unlimited when this limit is
    used.
    """
    NO_LIMIT: str = 'No-limit'
    """The no-limit.

    This denotes unlimited bet/raises in both the amounts (limited by
    the stack/cap).

    The number of them per betting round is typically unlimited in
    no-limit games.
    """


@unique
class Opening(StrEnum):
    """The enum class for openings.

    >>> Opening.POSITION
    <Opening.POSITION: 'Position'>
    >>> Opening.LOW_HAND
    <Opening.LOW_HAND: 'Low hand'>
    """

    POSITION: str = 'Position'
    """The opener is decided by position.

    If blinds or straddles are present, they are taken account of.
    """
    LOW_CARD: str = 'Low card'
    """The opener is decided by having the lowest exposed card."""
    HIGH_CARD: str = 'High card'
    """The opener is decided by having the highest exposed card."""
    LOW_HAND: str = 'Low hand'
    """The opener is decided by having the lowest exposed hand, then
    position.
    """
    HIGH_HAND: str = 'High hand'
    """The opener is decided by having the highest exposed hand, then
    position.
    """


@dataclass
class _LowHandOpeningLookup(Lookup):
    rank_order = RankOrder.REGULAR

    def _add_entries(self) -> None:
        for i in range(1, 5):
            self._add_multisets(
                Counter({1: i}),
                (False, True),
                Label.HIGH_CARD,
            )

        for i in range(3):
            self._add_multisets(
                Counter({2: 1, 1: i}),
                (False,),
                Label.ONE_PAIR,
            )

        self._add_multisets(Counter({2: 2}), (False,), Label.TWO_PAIR)

        for i in range(2):
            self._add_multisets(
                Counter({3: 1, 1: i}),
                (False,),
                Label.THREE_OF_A_KIND,
            )

        self._add_multisets(Counter({4: 1}), (False,), Label.FOUR_OF_A_KIND)


@dataclass
class _HighHandOpeningLookup(Lookup):
    rank_order = RankOrder.STANDARD

    def _add_entries(self) -> None:
        for i in range(1, 5):
            self._add_multisets(
                Counter({1: i}),
                (False, True),
                Label.HIGH_CARD,
            )

        for i in range(3):
            self._add_multisets(
                Counter({2: 1, 1: i}),
                (False,),
                Label.ONE_PAIR,
            )

        self._add_multisets(Counter({2: 2}), (False,), Label.TWO_PAIR)

        for i in range(2):
            self._add_multisets(
                Counter({3: 1, 1: i}),
                (False,),
                Label.THREE_OF_A_KIND,
            )

        self._add_multisets(Counter({4: 1}), (False,), Label.FOUR_OF_A_KIND)


@dataclass(frozen=True)
class Street:
    """The class for streets.

    >>> street = Street(
    ...     False,
    ...     (False, False),
    ...     0,
    ...     False,
    ...     Opening.POSITION,
    ...     2,
    ...     None,
    ... )
    >>> street.card_burning_status
    False
    >>> street.hole_dealing_statuses
    (False, False)

    :param card_burning_status: Whether to burn card (``True`` if this
                                is so). For more information, please
                                refer to
                                :attr:`pokerkit.state.Street.card_burning_status`.
    :param hole_dealing_statuses: The statuses of dealt hole cards. For
                                  more information, please refer to
                                  :attr:`pokerkit.state.Street.hole_dealing_statuses`.
    :param board_dealing_count: The number of dealt board cards (``0``
                                if none). For more information, please
                                refer to
                                :attr:`pokerkit.state.Street.board_dealing_count`.
    :param draw_status: Whether to draw cards prior to betting (``True``
                        if this is so). For more information, please
                        refer to
                        :attr:`pokerkit.state.Street.draw_status`.
    :param opening: The opening. For more information, please refer to
                    :attr:`pokerkit.state.Street.opening`.
    :param min_completion_betting_or_raising_amount: The minimum
                                                     completion,
                                                     betting, or raising
                                                     amount. For more
                                                     information, please
                                                     refer to
                                                     :attr:`pokerkit.state.Street.min_completion_betting_or_raising_amount`.
    :param max_completion_betting_or_raising_count: The maximum number
                                                    of completions,
                                                    bettings, or
                                                    raisings. For more
                                                    information, please
                                                    refer to
                                                    :attr:`pokerkit.state.Street.max_completion_betting_or_raising_count`.
    :raises ValueError: If the arguments are invalid.
    """

    card_burning_status: bool
    """Whether to burn card (``True`` if this is so)."""
    hole_dealing_statuses: tuple[bool, ...]
    """The statuses of dealt hole cards.

    The length of this ``tuple`` denotes the number of hole cards dealt
    in the current street. Each item denotes whether to deal a card as
    an up card (``True``) or a down card (``False``).

    If there is no board dealing and no drawing, this value should be
    non-empty. If drawing, this should be left empty.
    """
    board_dealing_count: int
    """The number of dealt board cards (``0`` if none).

    This number of cards is dealt for each board (for multi-board
    games).

    If there is no hole dealing and no drawing, this value should be
    non-empty.
    """
    draw_status: bool
    """Whether to draw cards prior to betting (``True`` if this is so).

    This flag is mutually exclusive with the enabling of hole dealings.
    In other words, if this is ``True``,
    :attr:`pokerkit.state.Street.hole_dealing_statuses` should be
    ``()``.

    If there is no hole dealing and no board dealing, this value should
    be non-empty.
    """
    opening: Opening
    """The opening.

    It decides who acts first for each betting round.
    """
    min_completion_betting_or_raising_amount: int
    """The minimum completion, betting, or raising amount."""
    max_completion_betting_or_raising_count: int | None
    """The maximum number of completions, bettings, or raisings."""

    def __post_init__(self) -> None:
        if self.board_dealing_count < 0:
            raise ValueError(
                (
                    f'The number of dealt cards {self.board_dealing_count}'
                    ' is negative.'
                ),
            )
        elif (
                not self.hole_dealing_statuses
                and not self.board_dealing_count
                and not self.draw_status
        ):
            raise ValueError('At least one dealing must be carried out.')
        elif self.hole_dealing_statuses and self.draw_status:
            raise ValueError(
                (
                    'Only one of hole dealing or drawing is permitted as draws'
                    ' are followed by hole dealings.'
                ),
            )
        elif self.min_completion_betting_or_raising_amount <= 0:
            raise ValueError(
                (
                    'Non-positive minimum completion, betting, or raising'
                    f' amount {self.min_completion_betting_or_raising_amount}'
                    ' was supplied.'
                ),
            )
        elif (
                self.max_completion_betting_or_raising_count is not None
                and self.max_completion_betting_or_raising_count < 0
        ):
            raise ValueError(
                (
                    'Negative maximum number of completion, bets, or raises'
                    f' {self.max_completion_betting_or_raising_count} was'
                    ' supplied.'
                ),
            )


@unique
class Automation(StrEnum):
    """The enum class for automation.

    >>> Automation.ANTE_POSTING
    <Automation.ANTE_POSTING: 'Ante posting'>
    >>> Automation.CARD_BURNING
    <Automation.CARD_BURNING: 'Card burning'>

    Each member of this enum specify what specific capability in
    PokerKit the user is not interested in handling and therefore should
    be reasonably handled by the library.
    """

    ANTE_POSTING: str = 'Ante posting'
    """The ante posting automation.

    By default, the players' antes are posted in order of their player
    indices.
    """
    BET_COLLECTION: str = 'Bet collection'
    """The bet collection automation."""
    BLIND_OR_STRADDLE_POSTING: str = 'Blind or straddle posting'
    """The blind or straddle posting automation.

    On automation, the players' antes are posted in order of their
    player indices.
    """
    CARD_BURNING: str = 'Card burning'
    """The card burning automation.

    When automated, the burnt card is dealt from the deck.
    """
    HOLE_DEALING: str = 'Hole dealing'
    """The hole dealing automation.

    When automated, the hole cards are dealt from the deck, in proper
    hole card dealing order (in accordance to player indices).
    """
    BOARD_DEALING: str = 'Board dealing'
    """The board dealing automation.

    The automated dealing behavior is simply drawing from the deck.
    """
    RUNOUT_COUNT_SELECTION: str = 'Runout-count selection'
    """The runout-count selection automation.

    This automation is useless in tournament mode, as tournament mode
    automatically skips runout-count selection phase since only 1
    runout is done, by rule.
    """
    HOLE_CARDS_SHOWING_OR_MUCKING: str = 'Hole cards showing or mucking'
    """The hole cards showing or mucking automation.

    By default, proper showdown order is followed and players show only
    when necessary.
    """
    HAND_KILLING: str = 'Hand killing'
    """The hand killing automation.

    When automated, the hand killing is done in the order of player
    indices.
    """
    CHIPS_PUSHING: str = 'Chips pushing'
    """The chips pushing automation.

    When automated, the chips pushing is done one by one, for each
    split main/side pot.
    """
    CHIPS_PULLING: str = 'Chips pulling'
    """The chips pulling automation.

    When automated, the chips-pulling is done in the order of player
    indices.
    """


@unique
class Mode(StrEnum):
    """The enum class for poker state types.

    Depending on whether the poker state is of a tournament or a
    cash-game, its behavior is different. Tournament settings tend to be
    stricter.

    >>> Mode.TOURNAMENT
    <Mode.TOURNAMENT: 'Tournament'>
    >>> Mode.CASH_GAME
    <Mode.CASH_GAME: 'Cash-game'>

    Tournament mode sets limitation on some of the operations: the
    number of runouts in all-in situations is always ``1``.
    """

    TOURNAMENT = 'Tournament'
    """The tournament poker state type."""
    CASH_GAME = 'Cash-game'
    """The cash-game poker state type."""


@dataclass
class Pot:
    """The class for pots.


    :param raked_amount: The raked amount. For more details, please
                         refer to
                         :attr:`pokerkit.state.Pot.raked_amount`.
    :param unraked_amount: The unraked amount. For more details, please
                           refer to
                           :attr:`pokerkit.state.Pot.unraked_amount`.
    :param player_indices: The player indices. For more details, please
                           refer to
                           :attr:`pokerkit.state.Pot.player_indices`.
    :raises ValueError: If the arguments are invalid.
    """

    raked_amount: int
    """The raked amount (from the original amount
    :attr:`pokerkit.state.Pot`).

    This value must be non-negative.
    """
    unraked_amount: int
    """The unraked amount (remaining from the original amount
    :attr:`pokerkit.state.Pot`).

    This vealue must be non-negative.
    """
    player_indices: tuple[int, ...]
    """The player indices of those who are eligible to win.

    This means A: they contributed to this pot and B: they are still
    active (in the hand).
    """

    def __post_init__(self) -> None:
        if self.raked_amount < 0:
            raise ValueError(
                f'The raked amount {self.raked_amount} is negative.',
            )
        elif self.unraked_amount < 0:
            raise ValueError(
                f'The unraked amount {self.unraked_amount} is negative.',
            )

    @property
    def amount(self) -> int:
        """Return the pot amount.

        This is the sum of the portion it is raked and the remaining
        pot.

        :return: The pot amount.
        """
        return self.raked_amount + self.unraked_amount


@dataclass(frozen=True)
class Operation(ABC):
    """The abstract base class for operations."""

    _: KW_ONLY
    commentary: str | None = None
    """The optional commentary."""


@dataclass(frozen=True)
class AntePosting(Operation):
    """The class for ante postings."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class BetCollection(Operation):
    """The class for bet collections."""

    bets: tuple[int, ...]
    """The bets."""

    @property
    def total_bets(self) -> int:
        """Return the total bets.

        >>> bet_collection = BetCollection((1, 2, 3))
        >>> bet_collection.total_bets
        6

        :return: The total bets.
        """
        return sum(self.bets)


@dataclass(frozen=True)
class BlindOrStraddlePosting(Operation):
    """The class for blind or straddle postings."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class CardBurning(Operation):
    """The class for card burnings."""

    card: Card
    """The card."""


@dataclass(frozen=True)
class HoleDealing(Operation):
    """The class for hole dealings."""

    player_index: int
    """The player index."""
    cards: tuple[Card, ...]
    """The cards."""
    statuses: tuple[bool, ...]
    """The statuses."""


@dataclass(frozen=True)
class BoardDealing(Operation):
    """The class for board dealings."""

    cards: tuple[Card, ...]
    """The cards."""


@dataclass(frozen=True)
class StandingPatOrDiscarding(Operation):
    """The class for standing pat or discardings."""

    player_index: int
    """The player index."""
    cards: tuple[Card, ...]
    """The discarded cards, empty if stood pat."""


@dataclass(frozen=True)
class Folding(Operation):
    """The class for foldings."""

    player_index: int
    """The player index."""


@dataclass(frozen=True)
class CheckingOrCalling(Operation):
    """The class for checking or callings."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class BringInPosting(Operation):
    """The class for bring-in postings."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class CompletionBettingOrRaisingTo(Operation):
    """The class for completion, betting, or raising tos."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class RunoutCountSelection(Operation):
    """The class for runout-count selection."""

    player_index: int
    """The player index."""
    runout_count: int | None
    """The runout-count."""


@dataclass(frozen=True)
class HoleCardsShowingOrMucking(Operation):
    """The class for hole cards showing or muckings."""

    player_index: int
    """The player index."""
    hole_cards: tuple[Card, ...]
    """The hole cards."""


@dataclass(frozen=True)
class HandKilling(Operation):
    """The class for hand killings."""

    player_index: int
    """The player index."""


@dataclass(frozen=True)
class ChipsPushing(Operation):
    """The class for chips pushings."""

    amounts: tuple[int, ...]
    """The amounts."""
    pot_index: int
    """The index of the pot (or portion of the pot) that was pushed."""
    board_index: int
    """The index of the board used to evaluate players' hands.

    If the push was during a folded or mucked pot, this value is ``-1``.
    """
    hand_type_index: int
    """The index of the hand type used to evaluate players' hands.

    If the push was during a folded or mucked pot, this value is ``-1``.
    """

    @property
    def total_amount(self) -> int:
        """Return the amount that was not raked and therefore pushed.

        This is identical to the sum of values in
        :attr:`pokerkit.state.ChipsPushing.amounts`.

        :return: The unraked amount.
        """
        return sum(self.amounts)


@dataclass(frozen=True)
class ChipsPulling(Operation):
    """The class for chips pullings."""

    player_index: int
    """The player index."""
    amount: int
    """The amount."""


@dataclass(frozen=True)
class NoOperation(Operation):
    """The class for no-operations."""

    pass


@dataclass
class State:
    """The class for states.

    Below code shows an example Kuhn poker game with all non-player
    actions and showdown automated.

    >>> from pokerkit import KuhnPokerHand
    >>> state = State(
    ...     (
    ...         Automation.ANTE_POSTING,
    ...         Automation.BET_COLLECTION,
    ...         Automation.BLIND_OR_STRADDLE_POSTING,
    ...         Automation.CARD_BURNING,
    ...         Automation.HOLE_DEALING,
    ...         Automation.BOARD_DEALING,
    ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
    ...         Automation.HAND_KILLING,
    ...         Automation.CHIPS_PUSHING,
    ...         Automation.CHIPS_PULLING,
    ...     ),
    ...     Deck.KUHN_POKER,
    ...     (KuhnPokerHand,),
    ...     (
    ...         Street(
    ...             False,
    ...             (False,),
    ...             0,
    ...             False,
    ...             Opening.POSITION,
    ...             1,
    ...             None,
    ...         ),
    ...     ),
    ...     BettingStructure.FIXED_LIMIT,
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )

    The game is active with the following stacks, bets, and hole cards.

    >>> state.status
    True
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.hole_cards  # doctest: +ELLIPSIS
    [[...s], [...s]]

    First player checks.

    >>> state.check_or_call()
    CheckingOrCalling(commentary=None, player_index=0, amount=0)
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]

    The second player bets 1.

    >>> state.complete_bet_or_raise_to()
    CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=1)
    >>> state.stacks
    [1, 0]
    >>> state.bets
    [0, 1]

    The first player folds.

    >>> state.fold()
    Folding(commentary=None, player_index=0)
    >>> state.stacks
    [1, 3]
    >>> state.bets
    [0, 0]
    >>> state.total_pot_amount
    0
    >>> state.status
    False

    Below shows the identical game, but without any automation.

    >>> state = State(
    ...     (),
    ...     Deck.KUHN_POKER,
    ...     (KuhnPokerHand,),
    ...     (
    ...         Street(
    ...             False,
    ...             (False,),
    ...             0,
    ...             False,
    ...             Opening.POSITION,
    ...             1,
    ...             None,
    ...         ),
    ...     ),
    ...     BettingStructure.FIXED_LIMIT,
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )
    >>> state.status
    True

    Antes are collected.

    >>> state.post_ante(0)
    AntePosting(commentary=None, player_index=0, amount=1)
    >>> state.post_ante(1)
    AntePosting(commentary=None, player_index=1, amount=1)
    >>> state.collect_bets()
    BetCollection(commentary=None, bets=(1, 1))

    Hole cards are dealt.

    >>> state.deal_hole('Js')  # doctest: +ELLIPSIS
    HoleDealing(commentary=None, player_index=0, cards=(Js,), statuses=(Fals...
    >>> state.deal_hole()  # doctest: +ELLIPSIS
    HoleDealing(commentary=None, player_index=1, cards=(...s,), statuses=(Fa...

    The actions are carried out.

    >>> state.check_or_call()
    CheckingOrCalling(commentary=None, player_index=0, amount=0)
    >>> state.complete_bet_or_raise_to()
    CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=1)
    >>> state.fold()
    Folding(commentary=None, player_index=0)

    The bets are collected and distributed to the winner.

    >>> state.collect_bets()
    BetCollection(commentary=None, bets=(0, 0))
    >>> state.push_chips()  # doctest: +ELLIPSIS
    ChipsPushing(commentary=None, amounts=(0, 2), pot_index=0, board_index=-...
    >>> state.pull_chips(1)
    ChipsPulling(commentary=None, player_index=1, amount=3)

    The game has terminated.

    >>> state.status
    False

    :param automations: The automations. For more details, please refer
                        to :attr:`pokerkit.state.State.automations`.
    :param deck: The deck. For more details, please refer to
                 :attr:`pokerkit.state.State.deck`.
    :param hand_types: The hand types. For more details, please refer to
                       :attr:`pokerkit.state.State.hand_types`.
    :param streets: The streets. For more details, please refer to
                    :attr:`pokerkit.state.State.streets`.
    :param betting_structure: The betting structure. For more details,
                              please refer to
                              :attr:`pokerkit.state.State.betting_structure`.
    :param ante_trimming_status: The ante trimming status. For more
                                 details, please refer to
                                 :attr:`pokerkit.state.State.ante_trimming_status`.
    :param raw_antes: The "raw" antes. For more details, please refer to
                      :attr:`pokerkit.state.State.raw_antes`.
    :param raw_blinds_or_straddles: The "raw" blinds/straddles. For more
                                    details, please refer to
                                    :attr:`pokerkit.state.State.raw_blinds_or_straddles`.
    :param bring_in: The bring-in. For more details, please refer to
                     :attr:`pokerkit.state.State.bring_in`.
    :param raw_starting_stacks: The "raw" starting stacks. For more
                                details, please refer to
                                :attr:`pokerkit.state.State.raw_starting_stacks`.
    :param player_count: The number of players. For more details, please
                         refer to
                         :attr:`pokerkit.state.State.player_count`.
    :param mode: The mode. Defaults to tournament mode. For more
                 details, please refer to
                 :attr:`pokerkit.state.State.mode`.
    :param starting_board_count: The number of boards at the start of
                                 the game. For more details, please
                                 refer to
                                 :attr:`pokerkit.state.State.starting_board_count`.
    :param divmod: The divmod function. For more details, please refer
                   to :attr:`pokerkit.state.State.divmod`.
    :param rake: The rake function. For more details, please refer to
                 :attr:`pokerkit.state.State.rake`.
    :raises ValueError: If the arguments are invalid.
    """

    __low_hand_opening_lookup = _LowHandOpeningLookup()
    __high_hand_opening_lookup = _HighHandOpeningLookup()
    automations: tuple[Automation, ...]
    """The automations.

    Allows the user to specify what steps they do not care about and
    therefore should be automatically handled by PokerKit.
    """
    deck: Deck
    """The deck.

    Different variants use different decks, which must be specified.
    """
    hand_types: tuple[type[Hand], ...]
    """The hand types.

    While most poker games use just a single hand type, there exists
    variants where multiple hand types should be considered when
    evaluating hand strengths, namely in high/low-split contexts.

    In PokerKit, each concept of high and low hands are separately
    considered, through the use of multiple hand types.
    """
    streets: tuple[Street, ...]
    """The streets.

    Each street contains information about the corresponding betting
    round and corresponding dealing/draw stage before it occurs.

    This attribute must be non-empty and its first item must be of
    hole-dealing.
    """
    betting_structure: BettingStructure
    """The betting structure.

    This class attribute determines the betting limits of a particular
    game (e.g. no-limit, pot-limit, or fixed-limit).
    """
    ante_trimming_status: bool
    """The ante trimming status.

    It denotes whether or not to activate the ``trimming`` behavior
    during bet collection immediately after the antes are posted.

    Usually, if you want uniform antes, set this to ``True``.  If you
    want non-uniform antes like big blind antes, set this to ``False``.
    """
    raw_antes: InitVar[ValuesLike]
    """The "raw" antes.

    In PokerKit, the term ``raw`` is used to denote the fact that they
    can be supplied in many forms and will be "parsed" or "evaluated"
    further to convert them into a more ideal form.

    For instance, ``0`` will be interpreted as no ante for all players.
    Another value will be interpreted as that value as the antes for
    all. ``[0, 2]`` and ``{1: 2} will be considered as the big blind
    ante whereas ``{-1: 2}`` will be considered as the button ante.

    All of its ante values must be non-negative.
    """
    raw_blinds_or_straddles: InitVar[ValuesLike]
    """The "raw" blinds or straddles.

    Just like for the antes, the blinds/straddles are also "interpreted"
    by PokerKit in the same fashion.

    All of its blind/straddle values must be non-negative.

    If the bring-in is non-zero, the all blind/straddle values must be
    zero. If any of the bring-in is zero, there must be at least one
    positive blind/straddle value.
    """
    bring_in: int
    """The bring-in.

    Some poker games do not have the bring-in, in which case ``0``
    should be its value.

    This value must be non-negative. If all blind/straddle values are
    zero, the bring-in must be positive. If any of the blind/straddle
    values are non-zero, the bring-in must be zero.

    It must be less than the min-bet.
    """
    raw_starting_stacks: InitVar[ValuesLike]
    """The "raw" starting stacks.

    Similar to "raw" antes and "raw" blinds/straddles, the starting
    stacks can be represented in different ways which PokerKit
    interprets when creating the games. Not all representations
    explicitly express the number of players and therefore this value is
    accepted as a separate parameter ``player_count``.

    All items must be positive.
    """
    player_count: int
    """The number of players.

    This value must be at least ``2``.
    """
    _: KW_ONLY
    mode: Mode = Mode.TOURNAMENT
    """The mode. Defaults to tournament mode.

    There are two modes available to be set: the tournament and
    cash-game mode. Tournaments use a stricter rule-set than typical
    cash-games. For more details, please consult
    :class:`pokerkit.state.Mode`.
    """
    starting_board_count: int = 1
    """The number of boards at the start of the game. Defaults to 1.

    For most poker games, it should be ``1``. Of course, for double
    board games, it should be ``2``. Triple/Quadruple/etc. board games
    are almost unheard of. Therefore, this value should mostly be ``1``
    or sometimes ``2``.

    The actual number of boards may change depending on the number of
    runouts (during all-ins).

    This value must be positive.
    """
    divmod: Callable[[int, int], tuple[int, int]] = divmod
    """The divmod function. Defaults to PokerKit's that detects integral
    or real values automatically.

    This is used to denote how pots are divided up (for multiple boards,
    multiple winners, multiple hand types, etc.).
    """
    rake: Callable[[int, State], tuple[int, int]] = rake
    """The rake function. Defaults to zero rake.

    Rake functions are used in PokerKit to denote how the rakes are
    collected from the pot. Multiple pots may exist (side-pots) in which
    case the method is called for each pot.

    The user may supply a custom rake function. This function must
    accept two positional arguments: the state and the amount to be
    raked. Its return value should be a tuple consisting of two values:
    the raked amount and the remaining, unraked amount.
    """
    antes: tuple[int, ...] = field(init=False)
    """The antes.

    This value is "interpreted" version of the "raw" antes.
    """
    blinds_or_straddles: tuple[int, ...] = field(init=False)
    """The blinds or straddles.

    This value is "interpreted" version of the "raw" blinds/straddles.
    """
    starting_stacks: tuple[int, ...] = field(init=False)
    """The starting stacks.

    This value is "interpreted" version of the "raw" starting stacks.
    """
    deck_cards: deque[Card] = field(default_factory=deque, init=False)
    """The deck cards.

    The cards in this deck are shuffled and popped from throughout the
    state's lifespan.
    """
    board_cards: list[list[Card]] = field(default_factory=list, init=False)
    """The board cards.

    This is a 2D list as cards may be parallel to each other for games
    with multiple boards or in the case of multiple runouts (during
    all-ins).
    """
    mucked_cards: list[Card] = field(default_factory=list, init=False)
    """The mucked cards.

    Cards that are folded or mucked are added here. These may be used
    later to replenish the deck (should it run out).
    """
    burn_cards: list[Card] = field(default_factory=list, init=False)
    """The burn cards.

    Cards that are burned are added here. These may be used later to
    replenish the deck (should it run out).
    """
    statuses: list[bool] = field(default_factory=list, init=False)
    """The player statuses.

    If the corresponding item is ``True`` one can say the player at that
    index is still "in the hand".
    """
    bets: list[int] = field(default_factory=list, init=False)
    """The player bets."""
    stacks: list[int] = field(default_factory=list, init=False)
    """The player stacks."""
    payoffs: list[int] = field(default_factory=list, init=False)
    """The player payoffs.

    Note that a ``payoff = stack - starting_stack`` for each player.

    Negated versions of these values can be thought of as contributions
    to the hand by the individual players.
    """
    hole_cards: list[list[Card]] = field(default_factory=list, init=False)
    """The player hole cards.

    In PokerKit, the concept of hole cards is slightly warped as it
    includes both up and down cards.
    """
    hole_card_statuses: list[list[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The player hole card statuses.

    The corresponding hole card is an up card if ``True``, and down if
    ``False``.
    """
    discarded_cards: list[list[Card]] = field(
        default_factory=list,
        init=False,
    )
    """The discards.

    The discarded cards are added here. They may be used to replenish
    the deck when it runs out.
    """
    street_index: int | None = field(default=None, init=False)
    """The street index.

    If it is not ``None``, it denotes what street the state is at
    currently. The actual street instance can be accessed through
    :attr:`pokerkit.state.State.street`.
    """
    street_return_index: int | None = field(default=None, init=False)
    """The street return index.

    This is not ``None`` if and only if multiple runouts are
    performed/performing.
    """
    street_return_count: int | None = field(default=0, init=False)
    """The street return count.

    This is non-zero if there are pending runouts not underway already.

    This value gets decremented before the start of each runout.
    """
    all_in_status: bool = field(default=False, init=False)
    """The all-in status.

    Simply put, are all active players all-in? ``True`` if yes,
    ``False`` otherwise.
    """
    status: bool = field(default=True, init=False)
    """The game status.

    ``True`` if the state is not terminal. If it is not terminal, some
    operation can still be performed.
    """
    operations: list[Operation] = field(default_factory=list, init=False)
    """The operations that were applied to this state.

    Each subsequent operation appends to this list.
    """

    def __post_init__(
            self,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            raw_starting_stacks: ValuesLike,
    ) -> None:
        self.antes = clean_values(raw_antes, self.player_count)
        self.blinds_or_straddles = clean_values(
            raw_blinds_or_straddles,
            self.player_count,
        )
        self.starting_stacks = clean_values(
            raw_starting_stacks,
            self.player_count,
        )

        if not self.streets:
            raise ValueError('The streets are empty.')
        elif not self.streets[0].hole_dealing_statuses:
            raise ValueError('The first street must be of hole dealing.')
        elif (
                min(self.antes) < 0
                or min(self.blinds_or_straddles) < 0
                or self.bring_in < 0
        ):
            raise ValueError(
                'Negative antes, blinds, straddles, or bring-in was supplied.',
            )
        elif (
                not any(self.antes)
                and not any(self.blinds_or_straddles)
                and not self.bring_in
        ):
            raise ValueError(
                'No antes, blinds, straddles, or bring-in was supplied.',
            )
        elif min(self.starting_stacks) <= 0:
            raise ValueError('Non-positive starting stacks was supplied.')
        elif any(self.blinds_or_straddles) and self.bring_in:
            raise ValueError(
                (
                    'Only one of bring-in or (blinds or straddles) must'
                    ' specified, but both were.'
                ),
            )
        elif (
                self.bring_in
                >= self.streets[0].min_completion_betting_or_raising_amount
        ):
            raise ValueError('The bring-in must be less than the min bet.')
        elif self.player_count < 2:
            raise ValueError(
                (
                    'There must be at least 2 players (currently'
                    f' {self.player_count}).'
                ),
            )
        elif self.starting_board_count <= 0:
            raise ValueError(
                (
                    f'The starting board count {self.starting_board_count}'
                    ' must be positive.'
                ),
            )

        self._setup()
        self._begin()

    def _setup(self) -> None:
        self.deck_cards.extend(self.deck)

        shuffle(self.deck_cards)

        for i in self.player_indices:
            self.statuses.append(True)
            self.bets.append(0)
            self.stacks.append(self.starting_stacks[i])
            self.payoffs.append(0)
            self.hole_cards.append([])
            self.hole_card_statuses.append([])

        for _ in self.street_indices:
            self.discarded_cards.append([])

        self._setup_ante_posting()
        self._setup_bet_collection()
        self._setup_blind_or_straddle_posting()
        self._setup_dealing()
        self._setup_betting()
        self._setup_showdown()
        self._setup_hand_killing()
        self._setup_chips_pushing()
        self._setup_chips_pulling()

    def _begin(self) -> None:
        self._begin_ante_posting()

        self._update()

    def _update(self, operation: Operation | None = None) -> None:
        if operation is not None:
            self.operations.append(operation)

    def _end(self) -> None:
        self.status = False

    @property
    def hand_type_count(self) -> int:
        """Return the number of hand types.

        Typically, this is ``1``. ``2`` hand types are used for
        split-pot games.

        >>> from pokerkit import (
        ...     FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
        ...     NoLimitTexasHoldem,
        ... )
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.hand_type_count
        1
        >>> state = (
        ...     FixedLimitOmahaHoldemHighLowSplitEightOrBetter.create_state(
        ...         (),
        ...         True,
        ...         1,
        ...         (1, 2),
        ...         2,
        ...         4,
        ...         100,
        ...         3,
        ...     )
        ... )
        >>> state.hand_type_count
        2

        :return: The number of hand types.
        """
        return len(self.hand_types)

    @property
    def hand_type_indices(self) -> range:
        """Return the hand type indices.

        >>> from pokerkit import (
        ...     FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
        ...     NoLimitTexasHoldem,
        ... )
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.hand_type_indices
        range(0, 1)
        >>> state = (
        ...     FixedLimitOmahaHoldemHighLowSplitEightOrBetter.create_state(
        ...         (),
        ...         True,
        ...         1,
        ...         (1, 2),
        ...         2,
        ...         4,
        ...         100,
        ...         3,
        ...     )
        ... )
        >>> state.hand_type_indices
        range(0, 2)

        :return: The hand type indices.
        """
        return range(self.hand_type_count)

    @property
    def draw_statuses(self) -> Iterator[bool]:
        """Return the draw statuses.

        Each yielded item corresponds to the draw status of each street.

        A draw status is ``True`` if discard/draw is performed for that
        street.

        >>> from pokerkit import (
        ...     NoLimitTexasHoldem,
        ...     NoLimitDeuceToSevenLowballSingleDraw,
        ... )
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.draw_statuses  # doctest: +ELLIPSIS
        <generator object State.draw_statuses at 0x...>
        >>> tuple(state.draw_statuses)
        (False, False, False, False)
        >>> state = NoLimitDeuceToSevenLowballSingleDraw.create_state(
        ...     (),
        ...     True,
        ...     1,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     3,
        ... )
        >>> tuple(state.draw_statuses)
        (False, True)

        :return: The draw statuses.
        """
        for street in self.streets:
            yield street.draw_status

    @property
    def player_indices(self) -> range:
        """Return the player indices.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.player_indices
        range(0, 2)
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     True,
        ...     1,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     9,
        ... )
        >>> state.player_indices
        range(0, 9)

        :return: The player indices.
        """
        return range(self.player_count)

    @property
    def street_count(self) -> int:
        """Return the number of streets.

        :return: The number of streets.
        """
        return len(self.streets)

    @property
    def street_indices(self) -> range:
        """Return the street indices.

        :return: The street indices.
        """
        return range(self.street_count)

    @property
    def street(self) -> Street | None:
        """Return the current street.

        ``None`` is returned if the state is terminal or in showdown.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.street is None
        True

        Setup.

        >>> state.post_ante(0)
        AntePosting(commentary=None, player_index=0, amount=2)
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(2, 0))
        >>> state.post_blind_or_straddle(0)
        BlindOrStraddlePosting(commentary=None, player_index=0, amount=2)
        >>> state.street is None
        True
        >>> state.post_blind_or_straddle(1)
        BlindOrStraddlePosting(commentary=None, player_index=1, amount=1)
        >>> state.street is state.streets[0]
        True
        >>> state.street  # doctest: +ELLIPSIS
        Street(card_burning_status=False, hole_dealing_statuses=(False, Fals...

        Pre-flop.

        >>> state.deal_hole('Ac')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac,), statuses=(...
        >>> state.deal_hole('Kc')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc,), statuses=(...
        >>> state.deal_hole('Ad')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ad,), statuses=(...
        >>> state.deal_hole('Kd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kd,), statuses=(...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.street is state.streets[0]
        True
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(2, 2))
        >>> state.street is state.streets[1]
        True

        Flop.

        >>> state.burn_card('2c')
        CardBurning(commentary=None, card=2c)
        >>> state.deal_board('AhKhAs')
        BoardDealing(commentary=None, cards=(Ah, Kh, As))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.street is state.streets[1]
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.street is state.streets[2]
        True

        Turn.

        >>> state.burn_card('2d')
        CardBurning(commentary=None, card=2d)
        >>> state.deal_board('Ks')
        BoardDealing(commentary=None, cards=(Ks,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.street is state.streets[2]
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.street is state.streets[3]
        True

        River.

        >>> state.burn_card('2h')
        CardBurning(commentary=None, card=2h)
        >>> state.deal_board('2s')
        BoardDealing(commentary=None, cards=(2s,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.street is state.streets[3]
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.street is state.streets[3]
        True

        Showdown.

        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=0, hole_card...
        >>> state.street is state.streets[3]
        True
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...
        >>> state.street is None
        True

        Teardown.

        >>> state.push_chips()  # doctest: +ELLIPSIS
        ChipsPushing(commentary=None, amounts=(6, 0), pot_index=0, board_ind...
        >>> state.street is None
        True
        >>> state.pull_chips()
        ChipsPulling(commentary=None, player_index=0, amount=6)
        >>> state.street is None
        True

        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.street is state.streets[0]
        True
        >>> state.fold()
        Folding(commentary=None, player_index=1)
        >>> state.street is None
        True

        :return: The street if applicable, otherwise ``None``.
        """
        if self.street_index is None:
            return None

        return self.streets[self.street_index]

    @property
    def turn_index(self) -> int | None:
        """Return the turn index.

        Regardless of what stage the state is in, whoever must make a
        decision will be returned, which is one of the following:

        - :attr:`pokerkit.state.State.stander_pat_or_discarder_index`
        - :attr:`pokerkit.state.State.actor_index`
        - :attr:`pokerkit.state.State.showdown_index`

        :return: The index of the player whose turn it is or ``None`` if
                 no one is in turn.
        """
        if self.stander_pat_or_discarder_index is not None:
            player_index = self.stander_pat_or_discarder_index
        elif self.actor_index is not None:
            player_index = self.actor_index
        elif self.showdown_index is not None:
            player_index = self.showdown_index
        else:
            player_index = None

        return player_index

    @property
    def board_count(self) -> int:
        """Return the number of boards.

        It should equal to the number of runouts, if set, at the end of
        the game.

        If no card was dealt to the board, the
        :attr:`pokerkit.state.State.starting_board_count` is returned.

        :return: The number of boards.
        """
        if self.street_return_index is not None:
            assert self.runout_count is not None

            board_count = self.starting_board_count * self.runout_count
        else:
            board_count = self.starting_board_count

        return board_count

    @property
    def board_indices(self) -> range:
        """Return the board indices.

        :return: The board indices.
        """
        return range(self.board_count)

    def get_board_cards(self, board_index: int) -> Iterator[Card]:
        """Return the board at the ``board_index`` (i.e.
        ``board_index``'th board, accounting for runout).

        In most games, there are only one board and runout, so, setting
        the ``board_index`` argument to ``0`` should do the job.

        If multiple boards/runouts were used, one can supply a different
        argument.

        Consider the following board:
        ``[[A, D], [B, E], [C, F], [G, H], [I, J, K, L]]``.

        The alphabets denote cards dealt and defined to reflect the
        proper dealing order. Here, there are 4 boards. The first is
        ``ABCGI``, the second is ``ABCHJ``, the third is ``DEFHK``, and
        fourth is ``DEFHL``.

        :param: The board index.
        :return: The board at the desired index.
        """
        if board_index not in self.board_indices:
            raise ValueError(
                f'The board index {board_index} is not a valid board index.',
            )

        if self.street_return_index is not None:
            assert self.runout_count is not None

            mid = 0

            for i in range(self.street_return_index):
                mid += self.streets[i].board_dealing_count

            for i, cards in enumerate(self.board_cards):
                index = board_index

                if i < mid:
                    index //= self.runout_count

                if index < len(cards):
                    yield cards[index]
        else:
            for cards in self.board_cards:
                if board_index < len(cards):
                    yield cards[board_index]

    def get_censored_hole_cards(self, player_index: int) -> Iterator[Card]:
        """Return the censored hole cards of the player.

        The hole cards that are face-down are yielded as an unknown
        card.

        >>> from pokerkit import *
        >>> state = (
        ...     FixedLimitSevenCardStudHighLowSplitEightOrBetter.create_state(
        ...         (
        ...             Automation.ANTE_POSTING,
        ...             Automation.BET_COLLECTION,
        ...             Automation.BLIND_OR_STRADDLE_POSTING,
        ...             Automation.CARD_BURNING,
        ...             Automation.BOARD_DEALING,
        ...             Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...             Automation.HAND_KILLING,
        ...             Automation.CHIPS_PUSHING,
        ...             Automation.CHIPS_PULLING,
        ...         ),
        ...         True,
        ...         0,
        ...         1,
        ...         2,
        ...         4,
        ...         (50, 100),
        ...         2,
        ...     )
        ... )
        >>> state.deal_hole('AcAdAh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad, Ah), sta...
        >>> state.deal_hole('KcKdKh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc, Kd, Kh), sta...
        >>> state.get_down_cards(0)  # doctest: +ELLIPSIS
        <generator object State.get_down_cards at 0x...>
        >>> tuple(state.get_censored_hole_cards(0))
        (??, ??, Ah)
        >>> tuple(state.get_censored_hole_cards(1))
        (??, ??, Kh)

        :param player_index: The player index.
        :return: The censored hole cards.
        """
        for card, status in zip(
                self.hole_cards[player_index],
                self.hole_card_statuses[player_index],
        ):
            if status:
                yield card
            else:
                yield Card(Rank.UNKNOWN, Suit.UNKNOWN)

    def get_down_cards(self, player_index: int) -> Iterator[Card]:
        """Return the down cards of the player.

        >>> from pokerkit import FixedLimitSevenCardStud
        >>> state = FixedLimitSevenCardStud.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     1,
        ...     2,
        ...     4,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.deal_hole('AcAdAh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad, Ah), sta...
        >>> state.deal_hole('KcKdKh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc, Kd, Kh), sta...
        >>> state.get_down_cards(0)  # doctest: +ELLIPSIS
        <generator object State.get_down_cards at 0x...>
        >>> tuple(state.get_down_cards(0))
        (Ac, Ad)
        >>> tuple(state.get_down_cards(1))
        (Kc, Kd)
        >>> state.post_bring_in()
        BringInPosting(commentary=None, player_index=1, amount=1)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> tuple(state.get_down_cards(0))
        ()
        >>> tuple(state.get_down_cards(1))
        (Kc, Kd)

        :param player_index: The player index.
        :return: The down cards of the player.
        """
        for card, status in zip(
                self.hole_cards[player_index],
                self.hole_card_statuses[player_index],
        ):
            if not status:
                yield card

    def get_up_cards(self, player_index: int) -> Iterator[Card]:
        """Return the up cards of the player.

        >>> from pokerkit import FixedLimitSevenCardStud
        >>> state = FixedLimitSevenCardStud.create_state(
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
        ...     1,
        ...     2,
        ...     4,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.deal_hole('AcAdAh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad, Ah), sta...
        >>> state.deal_hole('KcKdKh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc, Kd, Kh), sta...
        >>> state.get_down_cards(0)  # doctest: +ELLIPSIS
        <generator object State.get_down_cards at 0x...>
        >>> tuple(state.get_up_cards(0))
        (Ah,)
        >>> tuple(state.get_up_cards(1))
        (Kh,)
        >>> state.post_bring_in()
        BringInPosting(commentary=None, player_index=1, amount=1)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> tuple(state.get_up_cards(0))
        ()
        >>> tuple(state.get_up_cards(1))
        (Kh,)

        :param player_index: The player index.
        :return: The up cards of the player.
        """
        for card, status in zip(
                self.hole_cards[player_index],
                self.hole_card_statuses[player_index],
        ):
            if status:
                yield card

    def get_hand(
            self,
            player_index: int,
            board_index: int,
            hand_type_index: int,
    ) -> Hand | None:
        """Return the corresponding hand of the player.

        The player whose hand must be evaluated must be provided
        through ``player_index``. Which hand type to evaluate must be
        provided through ``hand_type_index``. Since they may be multiple
        boards, so does ``board_index``.

        The down cards *are* considered here.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_hand(0, 0, 0) is None
        True
        >>> state.get_hand(1, 0, 0) is None
        True

        Pre-flop.

        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad), statuse...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ks, Qs), statuse...
        >>> state.get_hand(0, 0, 0) is None
        True
        >>> state.get_hand(1, 0, 0) is None
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('JsTs2c')
        BoardDealing(commentary=None, cards=(Js, Ts, 2c))
        >>> state.get_hand(0, 0, 0)
        AcAdJsTs2c
        >>> str(state.get_hand(0, 0, 0))
        'One pair (AcAdJsTs2c)'
        >>> str(state.get_hand(1, 0, 0))
        'High card (KsQsJsTs2c)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ah')
        BoardDealing(commentary=None, cards=(Ah,))
        >>> str(state.get_hand(0, 0, 0))
        'Three of a kind (AcAdJsTsAh)'
        >>> str(state.get_hand(1, 0, 0))
        'Straight (KsQsJsTsAh)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('As')
        BoardDealing(commentary=None, cards=(As,))
        >>> str(state.get_hand(0, 0, 0))
        'Four of a kind (AcAdJsAhAs)'
        >>> str(state.get_hand(1, 0, 0))
        'Straight flush (KsQsJsTsAs)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.get_hand(0, 0, 0) is None
        True
        >>> str(state.get_hand(1, 0, 0))
        'Straight flush (KsQsJsTsAs)'

        :param player_index: The player index.
        :param board_index: The board index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player if applicable,
                 otherwise ``None``.
        """
        if not self.statuses[player_index]:
            return None

        try:
            hand = self.hand_types[hand_type_index].from_game(
                self.hole_cards[player_index],
                self.get_board_cards(board_index),
            )
        except (KeyError, ValueError):
            hand = None

        return hand

    def get_up_hand(
            self,
            player_index: int,
            board_index: int,
            hand_type_index: int,
    ) -> Hand | None:
        """Return the corresponding hand of the player from up cards.

        The player whose hand must be evaluated must be provided
        through ``player_index``. Which hand type to evaluate must be
        provided through ``hand_type_index``. Since they may be multiple
        boards, so does ``board_index``.

        The down cards *are not* considered here.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_up_hand(0, 0, 0) is None
        True
        >>> state.get_up_hand(1, 0, 0) is None
        True

        Pre-flop.

        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad), statuse...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ks, Qs), statuse...
        >>> state.get_up_hand(0, 0, 0) is None
        True
        >>> state.get_up_hand(1, 0, 0) is None
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('JsTs2c')
        BoardDealing(commentary=None, cards=(Js, Ts, 2c))
        >>> state.get_up_hand(0, 0, 0) is None
        True
        >>> state.get_up_hand(1, 0, 0) is None
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ah')
        BoardDealing(commentary=None, cards=(Ah,))
        >>> state.get_up_hand(0, 0, 0) is None
        True
        >>> state.get_up_hand(1, 0, 0) is None
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('As')
        BoardDealing(commentary=None, cards=(As,))
        >>> str(state.get_up_hand(0, 0, 0))
        'One pair (JsTs2cAhAs)'
        >>> str(state.get_up_hand(1, 0, 0))
        'One pair (JsTs2cAhAs)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.get_up_hand(0, 0, 0) is None
        True
        >>> str(state.get_up_hand(1, 0, 0))
        'Straight flush (KsQsJsTsAs)'

        :param player_index: The player index.
        :param board_index: The board index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player.
        """
        if not self.statuses[player_index]:
            return None

        try:
            hand = self.hand_types[hand_type_index].from_game(
                self.get_up_cards(player_index),
                self.get_board_cards(board_index),
            )
        except ValueError:
            hand = None

        return hand

    def get_up_hands(
            self,
            board_index: int,
            hand_type_index: int,
    ) -> Iterator[Hand | None]:
        """Return the optional corresponding hands from up cards.

        Which hand type to evaluate must be provided through
        ``hand_type_index``. Since they may be multiple boards, so does
        ``board_index``.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_up_hands(0, 0)  # doctest: +ELLIPSIS
        <generator object State.get_up_hands at 0x...>
        >>> tuple(state.get_up_hands(0, 0))
        (None, None)

        Pre-flop.

        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad), statuse...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ks, Qs), statuse...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('JsTs2c')
        BoardDealing(commentary=None, cards=(Js, Ts, 2c))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ah')
        BoardDealing(commentary=None, cards=(Ah,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('As')
        BoardDealing(commentary=None, cards=(As,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> tuple(state.get_up_hands(0, 0))
        (JsTs2cAhAs, JsTs2cAhAs)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> tuple(state.get_up_hands(0, 0))
        (None, KsQsJsTsAs)

        :param board_index: The board index.
        :param hand_type_index: The hand type index.
        :return: The optional corresponding hands from up cards.
        """
        for i in self.player_indices:
            yield self.get_up_hand(i, board_index, hand_type_index)

    def can_win_now(self, player_index: int) -> bool:
        """Return whether if the player might win pots based on
        the available information to a player.

        This basically means that nobody has yet shown a hand that
        prevents the player from winning even a tiny portion of any
        main/side pots.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
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
        ...     (50, 100),
        ...     2,
        ... )

        Pre-flop.

        >>> state.deal_hole('KhQh')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Kh, Qh), statuse...
        >>> state.deal_hole('AcKc')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ac, Kc), statuse...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('JsTs2c')
        BoardDealing(commentary=None, cards=(Js, Ts, 2c))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ah')
        BoardDealing(commentary=None, cards=(Ah,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('As')
        BoardDealing(commentary=None, cards=(As,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Showdown.

        >>> state.can_win_now(0)
        True
        >>> state.can_win_now(1)
        True
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=0, hole_card...
        >>> state.can_win_now(0)
        True
        >>> state.can_win_now(1)
        False
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...

        :param player_index: The player index.
        :return: ``True`` if the player can win, otherwise ``False``.
        """
        for i in self.board_indices:
            for j in self.hand_type_indices:
                hands = tuple(self.get_up_hands(i, j))
                hand = self.get_hand(player_index, i, j)

                for pot in self.pots:
                    max_hand = max_or_none(
                        map(partial(getitem, hands), pot.player_indices),
                    )

                    if (
                            hand is not None
                            and (max_hand is None or max_hand <= hand)
                    ):
                        return True

        return False

    @property
    def reserved_cards(self) -> Iterator[Card]:
        """Iterate through the reserved cards.

        These are either in the burn, muck, or discards and used when
        the deck is empty.

        :return: The reserved cards.
        """
        return filterfalse(
            Card.unknown_status.__get__,
            chain(
                self.burn_cards,
                self.mucked_cards,
                chain.from_iterable(self.discarded_cards),
            ),
        )

    @property
    def cards_in_play(self) -> Iterator[Card]:
        """Iterate through the cards in play.

        These are visible by at least one player still in the pot.

        These are either in the board or holes.

        :return: The cards in play.
        """
        return filterfalse(
            Card.unknown_status.__get__,
            chain(
                chain.from_iterable(self.board_cards),
                chain.from_iterable(self.hole_cards),
            ),
        )

    @property
    def cards_not_in_play(self) -> Iterator[Card]:
        """Iterate through the cards not in play.

        These are invisible by players still in the pot.

        These are either in the deck, burns, muck, or discards.

        :return: The cards not in play.
        """
        return filterfalse(
            Card.unknown_status.__get__,
            chain(
                self.deck_cards,
                self.burn_cards,
                self.mucked_cards,
                chain.from_iterable(self.discarded_cards),
            ),
        )

    def get_dealable_cards(
            self,
            deal_count: int | None = None,
    ) -> Iterator[Card]:
        """Iterate through the available cards that can be dealt or
        burned.

        The returned cards can be thought of as representing the
        "recommended" to be dealt. If only one card is to be dealt and
        there are multiple cards in the deck still remaining, then, one
        should select one of the cards in the deck (this is returned).

        Conversely, if one wants to deal ``3`` cards but there aren't
        enough cards left, the deck and the reserve must both be
        considered since the deck will run out amid dealing them and
        will be replenished. Thus, in this scenario, the merger of the
        deck and reserve are returned.

        If any dealing is performed with cards not part of the value
        to be returned in this method, a warning is issued by PokerKit.

        :param deal_count: The number of dealt cards, maybe ``None`` to
                           denote an arbitrary number of cards.
        :return: The "recommended" dealable cards, from deck and maybe
                 reserve.
        """
        cards = tuple(self.deck_cards)

        if deal_count is None or deal_count > len(self.deck_cards):
            cards += tuple(shuffled(self.reserved_cards))

        yield from cards

    def _muck_hole_cards(self, player_index: int) -> None:
        assert self.statuses[player_index]

        self.mucked_cards.extend(self.hole_cards[player_index])

        self.statuses[player_index] = False

        self.hole_cards[player_index].clear()
        self.hole_card_statuses[player_index].clear()

    def _show_hole_cards(self, player_index: int) -> None:
        assert self.statuses[player_index]

        for i in range(len(self.hole_cards[player_index])):
            self.hole_card_statuses[player_index][i] = True

    def _produce_cards(self, cards: Iterable[Card]) -> None:
        self.deck_cards.extend(
            filterfalse(
                self.deck_cards.__contains__,
                filterfalse(Card.unknown_status.__get__, cards),
            ),
        )

    def _verify_cards_consumption(
            self,
            cards: CardsLike | int,
    ) -> tuple[Card, ...]:
        if isinstance(cards, int):
            dealable_cards = tuple(self.get_dealable_cards(cards))

            if len(dealable_cards) < cards:
                raise ValueError('There are not enough cards to be dealt.')

            cards = dealable_cards[:cards]
        else:
            cards = Card.clean(cards)
            dealable_cards = tuple(self.get_dealable_cards(len(cards)))

            for card in cards:
                if card not in dealable_cards and not card.unknown_status:
                    warn(
                        (
                            f'A card being dealt {repr(card)} is not'
                            ' recommended to be dealt. For more details,'
                            ' please consult the method'
                            ' \'pokerkit.state.State.get_dealable_cards()\''
                        ),
                    )

        return cards

    def _consume_cards(self, cards: tuple[Card, ...]) -> None:
        if set(cards) > set(self.deck_cards):
            self._produce_cards(shuffled(self.reserved_cards))

            self.mucked_cards.clear()
            self.burn_cards.clear()

            for discarded_cards in self.discarded_cards:
                discarded_cards.clear()

        for card in cards:
            if card in self.deck_cards:
                self.deck_cards.remove(card)

            if card in self.burn_cards:
                self.burn_cards.remove(card)

            if card in self.mucked_cards:
                self.mucked_cards.remove(card)

            for discarded_cards in self.discarded_cards:
                if card in discarded_cards:
                    discarded_cards.remove(card)

    def get_effective_stack(self, player_index: int) -> int:
        """Return the effective stack of the player.

        It denotes the amount the player "can possibly lose".

        For example, if the player has the largest stack, then the
        second largest stack value owned by an active player will be
        returned.

        :param player_index: The player index.
        :return: The effective stack of the player.
        """
        if self.street_index is None or not self.statuses[player_index]:
            return 0

        effective_stacks = []

        for i in self.player_indices:
            if self.statuses[i]:
                effective_stacks.append(self.bets[i] + self.stacks[i])

        assert len(effective_stacks) > 1

        effective_stacks.sort()

        return min(
            self.stacks[player_index],
            max(0, effective_stacks[-2] - self.bets[player_index]),
        )

    @property
    def pot_amounts(self) -> Iterator[int]:
        """Return the list of main and side pot amounts (if any).

        The first pot (if any) is the main pot of this game. The
        subsequent pots are side pots.

        The amounts returned are unraked.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (50, 100, 200, 1000, 200, 100),
        ...     6,
        ... )
        >>> state.pot_amounts  # doctest: +ELLIPSIS
        <generator object State.pot_amounts at 0x...>
        >>> next(state.pot_amounts)
        Traceback (most recent call last):
            ...
        StopIteration
        >>> tuple(state.pot_amounts)  # doctest: +ELLIPSIS
        ()

        Pre-flop.

        >>> state.complete_bet_or_raise_to(200)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.complete_bet_or_raise_to(1000)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: There is no reason to complete, bet, or raise since ever...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=3, amount=200)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=4, amount=200)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=5, amount=100)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=49)
        >>> tuple(state.pot_amounts)
        ()
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=98)
        >>> next(state.pot_amounts)
        300
        >>> pot_amounts = tuple(state.pot_amounts)
        >>> len(pot_amounts)
        3
        >>> pot_amounts[0]
        300
        >>> pot_amounts[1]
        250
        >>> pot_amounts[2]
        300

        Flop.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(..., ..., ...))

        Turn.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))

        River.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))

        :return: The list of main and side pot (if any) amounts.
        """
        for pot in self.pots:
            yield pot.amount

    @property
    def total_pot_amount(self) -> int:
        """Return the total pot amount (unraked).

        This value also includes the bets.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.total_pot_amount
        0

        Setup.

        >>> state.post_ante(0)
        AntePosting(commentary=None, player_index=0, amount=2)
        >>> state.total_pot_amount
        2
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(2, 0))
        >>> state.total_pot_amount
        2
        >>> state.post_blind_or_straddle(0)
        BlindOrStraddlePosting(commentary=None, player_index=0, amount=2)
        >>> state.total_pot_amount
        4
        >>> state.post_blind_or_straddle(1)
        BlindOrStraddlePosting(commentary=None, player_index=1, amount=1)
        >>> state.total_pot_amount
        5

        Pre-flop.

        >>> state.deal_hole('Ac')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac,), statuses=(...
        >>> state.deal_hole('Kc')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc,), statuses=(...
        >>> state.deal_hole('Ad')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ad,), statuses=(...
        >>> state.deal_hole('Kd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kd,), statuses=(...
        >>> state.total_pot_amount
        5
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=1)
        >>> state.total_pot_amount
        6
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(2, 2))

        Flop.

        >>> state.burn_card('2c')
        CardBurning(commentary=None, card=2c)
        >>> state.deal_board('AhKhAs')
        BoardDealing(commentary=None, cards=(Ah, Kh, As))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Turn.

        >>> state.burn_card('2d')
        CardBurning(commentary=None, card=2d)
        >>> state.deal_board('Ks')
        BoardDealing(commentary=None, cards=(Ks,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.total_pot_amount
        6
        >>> state.complete_bet_or_raise_to(10)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.total_pot_amount
        16
        >>> state.complete_bet_or_raise_to(30)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.total_pot_amount
        46
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=20)
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(30, 30))
        >>> state.total_pot_amount
        66

        River.

        >>> state.burn_card('2h')
        CardBurning(commentary=None, card=2h)
        >>> state.deal_board('2s')
        BoardDealing(commentary=None, cards=(2s,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Showdown.

        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=0, hole_card...
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...

        Teardown.

        >>> state.push_chips()  # doctest: +ELLIPSIS
        ChipsPushing(commentary=None, amounts=(66, 0), pot_index=0, board_in...
        >>> state.total_pot_amount
        66
        >>> state.pull_chips()
        ChipsPulling(commentary=None, player_index=0, amount=66)
        >>> state.total_pot_amount
        0

        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.total_pot_amount
        5
        >>> state.fold()
        Folding(commentary=None, player_index=1)
        >>> state.total_pot_amount
        0

        :return: The total pot amount.
        """
        amount = sum(self.bets)

        for pot in self.pots:
            amount += pot.amount

        return amount

    @property
    def pots(self) -> Iterator[Pot]:
        """Return the list of main and side pots (if any).

        The first pot (if any) is the main pot of this game. The
        subsequent pots are side pots.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (50, 100, 200, 1000, 200, 100),
        ...     6,
        ... )
        >>> state.pots  # doctest: +ELLIPSIS
        <generator object State.pots at 0x...>
        >>> next(state.pots)
        Traceback (most recent call last):
            ...
        StopIteration
        >>> tuple(state.pots)  # doctest: +ELLIPSIS
        ()

        Pre-flop.

        >>> state.complete_bet_or_raise_to(200)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.complete_bet_or_raise_to(1000)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: There is no reason to complete, bet, or raise since ever...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=3, amount=200)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=4, amount=200)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=5, amount=100)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=49)
        >>> tuple(state.pots)
        ()
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=98)
        >>> next(state.pots)  # doctest: +ELLIPSIS
        Pot(raked_amount=0, unraked_amount=300, player_indices=(0, 1, 2, 3, ...
        >>> pots = tuple(state.pots)
        >>> len(pots)
        3
        >>> pots[0]  # doctest: +ELLIPSIS
        Pot(raked_amount=0, unraked_amount=300, player_indices=(0, 1, 2, 3, ...
        >>> pots[1]
        Pot(raked_amount=0, unraked_amount=250, player_indices=(1, 2, 3, 4, 5))
        >>> pots[2]
        Pot(raked_amount=0, unraked_amount=300, player_indices=(2, 3, 4))

        Flop.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(..., ..., ...))

        Turn.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))

        River.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))

        :return: The list of main and side pots (if any).
        """
        if self._pots is not None:
            yield from self._pots

            return
        elif sum(self.payoffs) == -sum(self.bets):
            return

        contributions = []
        pending_contributions = []
        amount = 0

        for i in self.player_indices:
            assert self.payoffs[i] <= 0

            contributions.append(-self.payoffs[i] - self.bets[i])
            pending_contributions.append(-self.payoffs[i])

        if not self.ante_trimming_status:
            amount = 0

            for i in self.player_indices:
                ante = self.get_effective_ante(i)
                amount += ante
                contributions[i] -= ante
                pending_contributions[i] -= ante

        previous_contribution = 0
        pots = list[Pot]()

        for contribution in sorted(set(contributions)):
            player_indices = []

            for i in self.player_indices:
                if contributions[i] >= contribution:
                    amount += contribution - previous_contribution

            for i in self.player_indices:
                if (
                        pending_contributions[i] >= contribution
                        and self.statuses[i]
                ):
                    player_indices.append(i)

            while pots and pots[-1].player_indices == tuple(player_indices):
                amount += pots.pop().amount

            if amount:
                raked_amount, unraked_amount = self.rake(amount, self)
                pot = Pot(raked_amount, unraked_amount, tuple(player_indices))

                pots.append(pot)

            amount = 0
            previous_contribution = contribution

        yield from pots

    # ante posting

    ante_posting_statuses: list[bool] = field(default_factory=list, init=False)
    """The player ante posting statuses.

    Each item denotes whether a player at that index can post the ante
    (``True``) or cannot (``False``).

    Each ante posting operation swithces one ``True`` item to ``False``.
    """

    def _setup_ante_posting(self) -> None:
        assert not self.ante_posting_statuses

        for _ in range(self.player_count):
            self.ante_posting_statuses.append(False)

    def _begin_ante_posting(self) -> None:
        assert not any(self.ante_posting_statuses)

        for i in self.player_indices:
            self.ante_posting_statuses[i] = self.get_effective_ante(i) > 0

        self._update_ante_posting()

    def _update_ante_posting(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if not any(self.ante_posting_statuses):
            self._end_ante_posting()
        elif Automation.ANTE_POSTING in self.automations:
            while any(self.ante_posting_statuses):
                self.post_ante()

    def _end_ante_posting(self) -> None:
        assert not any(self.ante_posting_statuses)

        self._begin_bet_collection()

    def get_effective_ante(self, player_index: int) -> int:
        """Return the effective ante of the player.

        The "effective" ante is effective in that it considers players'
        stacks being too low to post the full ante.

        :param player_index: The player index.
        :return: The effective ante.
        """
        if self.player_count == 2:
            ante = self.antes[not player_index]
        else:
            ante = self.antes[player_index]

        return min(ante, self.starting_stacks[player_index])

    @property
    def ante_poster_indices(self) -> Iterator[int]:
        """Iterate through players who can post antes.

        The yielded indices are sorted by player indices.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.ante_poster_indices  # doctest: +ELLIPSIS
        <generator object State.ante_poster_indices at 0x...>
        >>> tuple(state.ante_poster_indices)
        (0,)

        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     2,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> tuple(state.ante_poster_indices)
        (0, 1)
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> tuple(state.ante_poster_indices)
        ()

        :return: The ante posters.
        """
        try:
            self._verify_ante_posting()
        except (ValueError, UserWarning):
            return

        for i in self.player_indices:
            if self.ante_posting_statuses[i]:
                yield i

    def _verify_ante_posting(self) -> None:
        if not any(self.ante_posting_statuses):
            raise ValueError('Nobody can post the ante.')

    def verify_ante_posting(self, player_index: int | None = None) -> int:
        """Verify the ante posting.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_ante`.

        :param player_index: The optional player index.
        :return: The anteing player index.
        :raises ValueError: If the ante posting cannot be done.
        """
        self._verify_ante_posting()

        if player_index is None:
            player_index = next(self.ante_poster_indices)

        if not self.ante_posting_statuses[player_index]:
            raise ValueError(
                f'The Player {player_index} cannot post the ante.',
            )

        return player_index

    def can_post_ante(self, player_index: int | None = None) -> bool:
        """Return whether the ante posting can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_ante`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.can_post_ante()
        True
        >>> state.can_post_ante(0)
        True
        >>> state.can_post_ante(1)
        False

        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.can_post_ante()
        False
        >>> state.can_post_ante(0)
        False
        >>> state.can_post_ante(1)
        False

        :param player_index: The optional player index.
        :return: ``True`` if the ante posting can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_ante_posting(player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def post_ante(
            self,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> AntePosting:
        """Post the ante.

        In this operation, a single player posts the ante.

        The players who can post can be iterated through with
        :attr:`pokerkit.state.State.ante_poster_indices`. The first
        player in this iterable is posted if no player is specified.

        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The ante posting.
        :raises ValueError: If the ante posting cannot be done.
        """
        player_index = self.verify_ante_posting(player_index)
        amount = self.get_effective_ante(player_index)

        assert self.ante_posting_statuses[player_index]
        assert not self.bets[player_index]
        assert 0 < amount <= self.stacks[player_index]

        self.ante_posting_statuses[player_index] = False
        self.bets[player_index] = amount
        self.stacks[player_index] -= amount
        self.payoffs[player_index] -= amount

        operation = AntePosting(player_index, amount, commentary=commentary)

        self._update_ante_posting(operation)

        return operation

    # bet collection

    bet_collection_status: bool = field(default=False, init=False)
    """The bet collection status.

    If ``True``, then bet collection is pending. The operation will set
    this to ``False``.
    """

    def _setup_bet_collection(self) -> None:
        assert not self.bet_collection_status

    def _begin_bet_collection(self) -> None:
        assert not self.bet_collection_status

        self.bet_collection_status = any(self.bets)

        self._update_bet_collection()

    def _update_bet_collection(
            self,
            operation: Operation | None = None,
    ) -> None:
        self._update(operation)

        if not self.bet_collection_status:
            self._end_bet_collection()
        elif Automation.BET_COLLECTION in self.automations:
            if self.bet_collection_status:
                self.collect_bets()

    def _end_bet_collection(self) -> None:
        assert not self.bet_collection_status

        if self.street is self.streets[-1] and self.street_return_count:
            assert self.street_return_index is not None

            self.street_index = self.street_return_index - 1
            self.street_return_count -= 1

        if sum(self.statuses) == 1:
            self._begin_chips_pushing()
        elif self.street is None:
            self._begin_blind_or_straddle_posting()
        elif self.street is self.streets[-1] or self.all_in_status:
            self._begin_showdown()
        else:
            self._begin_dealing()

    def verify_bet_collection(self) -> None:
        """Verify the bet collection.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.collect_bets`.

        :return: ``None``.
        :raises ValueError: If the bet collection cannot be done.
        """
        if not self.bet_collection_status:
            raise ValueError('The bet collection is currently prohibited.')

    def can_collect_bets(self) -> bool:
        """Return whether the bet collection can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.collect_bets`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     2,
        ... )
        >>> state.can_collect_bets()
        False
        >>> state.post_ante()
        AntePosting(commentary=None, player_index=0, amount=2)
        >>> state.can_collect_bets()
        True

        :return: ``True`` if the bet collection can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_bet_collection()
        except (ValueError, UserWarning):
            return False

        return True

    def collect_bets(self, *, commentary: str | None = None) -> BetCollection:
        """Collect the bets.

        In this operation, the outstanding bets are collected into the pot.

        Note that, when the hand is folded, the last aggressor's bet is
        returned to his/her stack. The rest of the outstanding bets are
        collected to the pot.

        :param commentary: The optional commentary.
        :return: The bet collection.
        :raises ValueError: If the bet collection cannot be done.
        """
        self.verify_bet_collection()

        assert self.bet_collection_status
        assert any(self.bets)

        self.bet_collection_status = False
        player_indices = list(self.player_indices)
        bets = self.bets.copy()

        if sum(self.statuses) == 1:
            player_index = self.statuses.index(True)
            bets[player_index] = 0

            player_indices.remove(player_index)

        if self.street is not None or self.ante_trimming_status:
            bet_cutoff = sorted(self.bets)[-2]

            for i in player_indices:
                if self.bets[i] > bet_cutoff:
                    assert self.statuses[i]

                    overbet = self.bets[i] - bet_cutoff
                    self.stacks[i] += overbet
                    self.payoffs[i] += overbet
                    bets[i] = bet_cutoff

        for i in player_indices:
            self.bets[i] = 0

        operation = BetCollection(tuple(bets), commentary=commentary)

        self._update_bet_collection(operation)

        return operation

    # blind or straddle posting

    blind_or_straddle_posting_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The player blind or straddle statuses.

    Each item denotes whether a player at that index can post the
    blind/straddle (``True``) or cannot (``False``).

    Each blind/straddle posting operation swithces one ``True`` item to
    ``False``.
    """

    def _setup_blind_or_straddle_posting(self) -> None:
        assert not self.blind_or_straddle_posting_statuses

        for _ in range(self.player_count):
            self.blind_or_straddle_posting_statuses.append(False)

    def _begin_blind_or_straddle_posting(self) -> None:
        assert not any(self.blind_or_straddle_posting_statuses)

        for i in self.player_indices:
            self.blind_or_straddle_posting_statuses[i] = (
                self.get_effective_blind_or_straddle(i) > 0
            )

        self._update_blind_or_straddle_posting()

    def _update_blind_or_straddle_posting(
            self,
            operation: Operation | None = None,
    ) -> None:
        self._update(operation)

        if not any(self.blind_or_straddle_posting_statuses):
            self._end_blind_or_straddle_posting()
        elif Automation.BLIND_OR_STRADDLE_POSTING in self.automations:
            while any(self.blind_or_straddle_posting_statuses):
                self.post_blind_or_straddle()

    def _end_blind_or_straddle_posting(self) -> None:
        assert not any(self.blind_or_straddle_posting_statuses)

        self._begin_dealing()

    def get_effective_blind_or_straddle(self, player_index: int) -> int:
        """Return the "effective" blind or straddle of the player.

        The "effective" blind/straddle is effective in that it considers
        players' stacks being too low to post the full ante.

        :param player_index: The player index.
        :return: The effective blind or straddle.
        """
        if self.player_count == 2:
            blind_or_straddle = self.blinds_or_straddles[not player_index]
        else:
            blind_or_straddle = self.blinds_or_straddles[player_index]

        return min(
            blind_or_straddle,
            self.starting_stacks[player_index]
            - self.get_effective_ante(player_index),
        )

    @property
    def blind_or_straddle_poster_indices(self) -> Iterator[int]:
        """Iterate through players who can post blinds or straddles.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     4,
        ... )
        >>> state.blind_or_straddle_poster_indices  # doctest: +ELLIPSIS
        <generator object State.blind_or_straddle_poster_indices at 0x...>
        >>> tuple(state.blind_or_straddle_poster_indices)
        ()
        >>> state.post_ante(1)
        AntePosting(commentary=None, player_index=1, amount=2)
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(0, 2, 0, 0))
        >>> tuple(state.blind_or_straddle_poster_indices)
        (0, 1)

        :return: The blind or straddle posters.
        """
        try:
            self._verify_blind_or_straddle_posting()
        except (ValueError, UserWarning):
            return

        for i in self.player_indices:
            if self.blind_or_straddle_posting_statuses[i]:
                yield i

    def _verify_blind_or_straddle_posting(self) -> None:
        if not any(self.blind_or_straddle_posting_statuses):
            raise ValueError('Nobody can post the blind or straddle.')

    def verify_blind_or_straddle_posting(
            self,
            player_index: int | None = None,
    ) -> int:
        """Verify the blind or straddle posting.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_blind_or_straddle`.

        :param player_index: The optional player index.
        :return: The blinding or straddling player index.
        :raises ValueError: If blind or straddle posting cannot be done.
        """
        self._verify_blind_or_straddle_posting()

        if player_index is None:
            player_index = next(self.blind_or_straddle_poster_indices)

        if not self.blind_or_straddle_posting_statuses[player_index]:
            raise ValueError(
                f'The Player {player_index} cannot post the blind or straddle',
            )

        return player_index

    def can_post_blind_or_straddle(
            self,
            player_index: int | None = None,
    ) -> bool:
        """Return whether the blind or straddle posting can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_blind_or_straddle`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     False,
        ...     (0, 2),
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     4,
        ... )
        >>> state.can_post_blind_or_straddle()
        False
        >>> state.post_ante(1)
        AntePosting(commentary=None, player_index=1, amount=2)
        >>> state.collect_bets()
        BetCollection(commentary=None, bets=(0, 2, 0, 0))
        >>> state.can_post_blind_or_straddle()
        True
        >>> state.can_post_blind_or_straddle(0)
        True
        >>> state.can_post_blind_or_straddle(1)
        True
        >>> state.can_post_blind_or_straddle(2)
        False
        >>> state.can_post_blind_or_straddle(3)
        False

        :param player_index: The optional player index.
        :return: ``True`` if the blind or straddle posting can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_blind_or_straddle_posting(player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def post_blind_or_straddle(
            self,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> BlindOrStraddlePosting:
        """Post the blind or straddle of the player.

        In this operation, a single player posts the blind/straddle.

        The players who can post can be iterated through with
        :attr:`pokerkit.state.State.blind_or_straddle_poster_indices`.
        The first player in this iterable is posted if no player is
        specified.

        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The blind or straddle posting.
        :raises ValueError: If the blind or straddle posting cannot be
                            done.
        """
        player_index = self.verify_blind_or_straddle_posting(player_index)
        amount = self.get_effective_blind_or_straddle(player_index)

        assert self.blind_or_straddle_posting_statuses[player_index]
        assert not self.bets[player_index]
        assert 0 < amount <= self.stacks[player_index]

        self.blind_or_straddle_posting_statuses[player_index] = False
        self.bets[player_index] = amount
        self.stacks[player_index] -= amount
        self.payoffs[player_index] -= amount

        operation = BlindOrStraddlePosting(
            player_index,
            amount,
            commentary=commentary,
        )

        self._update_blind_or_straddle_posting(operation)

        return operation

    # dealing

    card_burning_status: bool = field(default=False, init=False)
    """The card burning status.

    If ``True``, a card burning is pending.
    """
    hole_dealing_statuses: list[deque[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The hole dealing statuses.

    If an item is non-empty, hole dealings are pending for that player
    (up if ``True``, down if ``False``).
    """
    board_dealing_counts: list[int] = field(default_factory=list, init=False)
    """The board dealing counts.

    This is a list, as there may be multiple pending board dealings (due
    to multiple boards).
    """
    standing_pat_or_discarding_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The standing pat or discarding statuses.

    If an item is ``True``, then the player should perform a draw
    action (or stand pat).
    """

    def _setup_dealing(self) -> None:
        assert not self.hole_dealing_statuses
        assert not self.standing_pat_or_discarding_statuses

        for _ in range(self.player_count):
            self.hole_dealing_statuses.append(deque())
            self.standing_pat_or_discarding_statuses.append(False)

        for _ in range(self.starting_board_count):
            self.board_dealing_counts.append(0)

    def _begin_dealing(self) -> None:
        assert not self.card_burning_status
        assert not any(self.hole_dealing_statuses)
        assert not any(self.board_dealing_counts)
        assert not any(self.standing_pat_or_discarding_statuses)

        if self.street_index is None:
            self.street_index = 0
        else:
            self.street_index += 1

        assert 0 <= self.street_index < len(self.streets)
        assert self.street is not None

        self.card_burning_status = self.street.card_burning_status
        self.board_dealing_counts = (
            [self.street.board_dealing_count]
            * self.starting_board_count
        )

        for i in self.player_indices:
            if self.statuses[i]:
                self.hole_dealing_statuses[i].extend(
                    self.street.hole_dealing_statuses,
                )
                self.standing_pat_or_discarding_statuses[i] = (
                    self.street.draw_status
                )

        if (
                sum(map(len, self.hole_dealing_statuses))
                > len(tuple(self.get_dealable_cards()))
        ):
            for i in range(self.starting_board_count):
                self.board_dealing_counts[i] += (
                    len(self.street.hole_dealing_statuses)
                )

            for i in self.player_indices:
                self.hole_dealing_statuses[i].clear()

        assert (
            any(self.hole_dealing_statuses)
            or any(self.board_dealing_counts)
            or any(self.standing_pat_or_discarding_statuses)
        )

        self._update_dealing()

    def _update_dealing(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if (
                not self.card_burning_status
                and not any(self.hole_dealing_statuses)
                and not any(self.board_dealing_counts)
                and not any(self.standing_pat_or_discarding_statuses)
        ):
            self._end_dealing()
        elif not any(self.standing_pat_or_discarding_statuses):
            if (
                    Automation.CARD_BURNING in self.automations
                    and self.card_burning_status
            ):
                self.burn_card()

            if not self.card_burning_status:
                if Automation.HOLE_DEALING in self.automations:
                    while any(self.hole_dealing_statuses):
                        self.deal_hole()

                if (
                        Automation.BOARD_DEALING in self.automations
                        and any(self.board_dealing_counts)
                ):
                    self.deal_board()

    def _end_dealing(self) -> None:
        assert not self.card_burning_status
        assert not any(self.hole_dealing_statuses)
        assert not any(self.board_dealing_counts)
        assert not any(self.standing_pat_or_discarding_statuses)

        self._begin_betting()

    def verify_card_burning(
            self,
            card: CardsLike | None = None,
    ) -> Card:
        """Verify the card burning.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.burn_card`.

        :param card: The optional card.
        :return: The burn card.
        :raises ValueError: If the card burning cannot be done.
        """
        cards = self._verify_cards_consumption(
            1 if card is None else card,
        )

        if not self.card_burning_status:
            raise ValueError('No card burning is pending.')
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError(
                (
                    'Not all have stood pat or discarded as should be done'
                    ' when burning a card.'
                ),
            )
        elif len(cards) != 1:
            raise ValueError(
                (
                    f'One card must be burned, not {len(cards)} as in'
                    f' {repr(cards)}.'
                ),
            )

        card, = cards

        return card

    def can_burn_card(self, card: CardsLike | None = None) -> bool:
        """Return whether the card burning can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.burn_card`.

        :param card: The optional card.
        :return: ``True`` if the card burning can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_card_burning(card)
        except (ValueError, UserWarning):
            return False

        return True

    def burn_card(
            self,
            card: CardsLike | None = None,
            *,
            commentary: str | None = None,
    ) -> CardBurning:
        """Burn a card.

        If the ``card`` is not specified, a card is drawn from the deck.
        The deck, if empty, will be replenished from the reserve.

        If a string representation is used, only a single card must be
        described.

        :param card: The optional card.
        :param commentary: The optional commentary.
        :return: The card burning.
        :raises ValueError: If the card burning cannot be done.
        """
        card = self.verify_card_burning(card)

        assert self.card_burning_status
        assert self.street is not None
        assert (
            any(self.hole_dealing_statuses)
            or any(self.board_dealing_counts)
            or self.street.draw_status
        )

        self._consume_cards((card,))

        self.card_burning_status = False
        self.burn_cards.append(card)

        operation = CardBurning(card, commentary=commentary)

        self._update_dealing(operation)

        return operation

    @property
    def hole_dealee_index(self) -> int | None:
        """Return the hole dealee index.

        This index is that of the player in turn to be dealt the hole
        cards.

        Of course, this may be overridden in the actual operation.

        :return: The hole dealee index if applicable, otherwise
                 ``None``.
        """
        try:
            self._verify_hole_dealing()
        except (ValueError, UserWarning):
            return None

        assert self.street is not None
        assert self.street.hole_dealing_statuses or self.street.draw_status

        if self.street.hole_dealing_statuses:
            return max(
                self.player_indices,
                key=lambda i: (len(self.hole_dealing_statuses[i]), -i),
            )
        else:
            return next(
                filter(
                    partial(getitem, self.hole_dealing_statuses),
                    self.player_indices,
                ),
            )

    def _verify_hole_dealing(self) -> None:
        if self.card_burning_status:
            raise ValueError('A card must be burnt before hole dealing.')
        elif not any(self.hole_dealing_statuses):
            raise ValueError('Currently, nobody can be dealt hole cards.')
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError(
                (
                    'Not all have stood pat or discarded, as should be when'
                    ' hole dealing.'
                ),
            )

    def verify_hole_dealing(
            self,
            cards: CardsLike | int | None = None,
            player_index: int | None = None,
    ) -> tuple[tuple[Card, ...], int]:
        """Verify the hole dealing.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.deal_hole`.

        :param cards: The optional cards.
        :param player_index: The optional target dealee.
        :return: The dealt hole cards.
        :raises ValueError: If the hole dealing cannot be done.
        """
        self._verify_hole_dealing()

        cards = self._verify_cards_consumption(
            1 if cards is None else cards,
        )

        if player_index is None:
            player_index = self.hole_dealee_index

        assert player_index is not None

        if not self.hole_dealing_statuses[player_index]:
            raise ValueError(
                f'The Player {player_index} cannot be dealt any hole cards.',
            )
        elif (
                len(cards)
                not in range(
                    1,
                    len(self.hole_dealing_statuses[player_index]) + 1,
                )
        ):
            raise ValueError(
                (
                    'The number of cards dealt must be non-zero and less than'
                    ' or equal to'
                    f' {len(self.hole_dealing_statuses[player_index])}, not'
                    f' {len(cards)} as for {repr(cards)}.'
                ),
            )

        return cards, player_index

    def can_deal_hole(
            self,
            cards: CardsLike | int | None = None,
            player_index: int | None = None,
    ) -> bool:
        """Return whether the hole dealing can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.deal_hole`.

        :param cards: The optional cards.
        :param player_index: The optional target dealee.
        :return: ``True`` if the hole dealing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_hole_dealing(cards, player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def deal_hole(
            self,
            cards: CardsLike | int | None = None,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> HoleDealing:
        """Deal the hole.

        The number of dealt hole cards should be less than or equal to
        the number of pending hole dealings to the player.

        If unspecified, the cards will be drawn from the deck (and
        possibly replenished from the reserve).

        If the player is not specified, they will be automatically
        determined. The automatic dealee is available at
        :attr:`pokerkit.state.State.hole_dealee_index`.

        :param cards: The optional cards.
        :param player_index: The optional target dealee.
        :param commentary: The optional commentary.
        :return: The hole dealing.
        :raises ValueError: If the hole dealing cannot be done.
        """
        cards, player_index = self.verify_hole_dealing(cards, player_index)
        statuses = []

        assert player_index is not None
        assert self.hole_dealing_statuses[player_index]

        self._consume_cards(cards)

        for card in cards:
            status = self.hole_dealing_statuses[player_index].popleft()

            statuses.append(status)
            self.hole_cards[player_index].append(card)
            self.hole_card_statuses[player_index].append(status)

        operation = HoleDealing(
            player_index,
            cards,
            tuple(statuses),
            commentary=commentary,
        )

        self._update_dealing(operation)

        return operation

    @property
    def board_dealing_count(self) -> int | None:
        """Return the number of pending board dealings.

        :return: The number of board dealings.
        """
        try:
            self._verify_board_dealing()
        except ValueError:
            board_dealing_count = None
        else:
            board_dealing_count = next(filter(None, self.board_dealing_counts))

        return board_dealing_count

    def _verify_board_dealing(self) -> None:
        if self.card_burning_status:
            raise ValueError('A card must be burnt before board dealing.')
        elif not any(self.board_dealing_counts):
            raise ValueError('No board dealing is pending.')
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError('Not all have stood pat or discarded.')

    def verify_board_dealing(
            self,
            cards: CardsLike | int | None = None,
    ) -> tuple[Card, ...]:
        """Verify the board dealing.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.deal_board`.

        :param cards: The optional cards.
        :return: The dealt board cards.
        :raises ValueError: If the board dealing cannot be done.
        """
        self._verify_board_dealing()

        assert self.board_dealing_count is not None

        cards = self._verify_cards_consumption(
            self.board_dealing_count if cards is None else cards,
        )

        if not 0 < len(cards) <= self.board_dealing_count:
            raise ValueError(
                (
                    'The number of dealt cards must be non-zero and less than'
                    f' or equal to {self.board_dealing_count}, not'
                    f' {len(cards)} as for {repr(cards)}.'
                ),
            )

        return cards

    def can_deal_board(self, cards: CardsLike | int | None = None) -> bool:
        """Return whether the board dealing can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.deal_board`.

        :param cards: The optional cards.
        :param player_index: The optional player index.
        :return: ``True`` if the board dealing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_board_dealing(cards)
        except (ValueError, UserWarning):
            return False

        return True

    def deal_board(
            self,
            cards: CardsLike | int | None = None,
            *,
            commentary: str | None = None,
    ) -> BoardDealing:
        """Deal the board.

        The cards, if unspecified, will be drawn from the deck (and
        possibly replenished from the reserve).

        :param cards: The optional cards.
        :param commentary: The optional commentary.
        :return: The board dealing.
        :raises ValueError: If the board dealing cannot be done.
        """
        cards = self.verify_board_dealing(cards)

        assert self.board_dealing_count is not None
        assert self.street_index is not None
        assert self.street is not None

        self._consume_cards(cards)

        index = 0

        for i in range(self.street_index):
            index += self.streets[i].board_dealing_count

        index += max(
            self.street.board_dealing_count - self.board_dealing_count,
            0,
        )
        board_index = self.board_dealing_counts.index(self.board_dealing_count)
        self.board_dealing_counts[board_index] -= len(cards)

        for card in cards:
            assert index <= len(self.board_cards)

            if index == len(self.board_cards):
                self.board_cards.append([])

            self.board_cards[index].append(card)

            index += 1

        operation = BoardDealing(cards, commentary=commentary)

        self._update_dealing(operation)

        return operation

    @property
    def stander_pat_or_discarder_index(self) -> int | None:
        """Return the stander pat or discarder index.

        :return: The stander pat or discarder index if applicable,
                 otherwise ``None``.
        """
        try:
            self._verify_standing_pat_or_discarding()
        except (ValueError, UserWarning):
            return None

        return self.standing_pat_or_discarding_statuses.index(True)

    def _verify_standing_pat_or_discarding(self) -> None:
        if not any(self.standing_pat_or_discarding_statuses):
            raise ValueError('There are no pending draws.')

    def verify_standing_pat_or_discarding(
            self,
            cards: CardsLike = (),
    ) -> tuple[Card, ...]:
        """Verify the discard.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.stand_pat_or_discard`.

        :param cards: The discarded cards, defaults to empty.
        :return: The discarded cards.
        :raises ValueError: If the discard cannot be done.
        """
        self._verify_standing_pat_or_discarding()

        cards = Card.clean(cards)
        player_index = self.stander_pat_or_discarder_index

        assert player_index is not None

        if not set(cards) <= set(self.hole_cards[player_index]):
            raise ValueError(
                (
                    f'The discarded cards {repr(cards)} must be a subset of'
                    f' hole cards {repr(self.hole_cards[player_index])}, but'
                    ' it is not.'
                ),
            )

        return cards

    def can_stand_pat_or_discard(self, cards: CardsLike = ()) -> bool:
        """Return whether the discard can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.stand_pat_or_discard`.

        :param cards: The optional discarded cards, defaults to empty.
        :return: ``True`` if the discard can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_standing_pat_or_discarding(cards)
        except (ValueError, UserWarning):
            return False

        return True

    def stand_pat_or_discard(
            self,
            cards: CardsLike = (),
            *,
            commentary: str | None = None,
    ) -> StandingPatOrDiscarding:
        """Stand pat or discard hole cards.

        The specified cards (if any) should be a subset of the player's
        hole cards.

        The player currently standing pat/discarding can be accessed via
        :attr:`pokerkit.state.State.stander_pat_or_discarder_index`.

        After the standing pat or discarding is done for all pending
        players, their hole should be replenished by the subsequent hole
        dealing operations to each player.

        :param cards: The optional discarded cards.
        :param commentary: The optional commentary.
        :return: The standing pat or discarding, defaults to empty.
        :raises ValueError: If the discard cannot be done.
        """
        cards = self.verify_standing_pat_or_discarding(cards)
        player_index = self.stander_pat_or_discarder_index

        assert player_index is not None
        assert self.street_index is not None
        assert self.standing_pat_or_discarding_statuses[player_index]

        self.standing_pat_or_discarding_statuses[player_index] = False

        for card in cards:
            index = self.hole_cards[player_index].index(card)

            self.hole_dealing_statuses[player_index].append(
                self.hole_card_statuses[player_index][index],
            )
            self.hole_cards[player_index].pop(index)
            self.hole_card_statuses[player_index].pop(index)
            self.discarded_cards[self.street_index].append(card)

        operation = StandingPatOrDiscarding(
            player_index,
            cards,
            commentary=commentary,
        )

        self._update_dealing(operation)

        return operation

    # betting

    opener_index: int | None = field(default=None, init=False)
    """The opener index.

    At the beginning of a betting round, this denotes who opened the
    round. If someone bets or raises, this attribute is updated to
    reflect who opened the betting round.
    """
    bring_in_status: bool = field(default=False, init=False)
    """The bring-in status.

    If ``True``, the player should at least post a bring-in (therefore
    cannot fold).
    """
    completion_status: bool = field(default=False, init=False)
    """The completion status.

    If ``True``, the player is facing a bring-in and hence a completion
    is pending.
    """
    actor_indices: deque[int] = field(default_factory=deque, init=False)
    """The actor indices.

    The order of actors to act (i.e. turn indices). The first item
    denotes who is in action.
    """
    completion_betting_or_raising_amount: int = field(default=0, init=False)
    """The last completion, betting, or raising amount.

    This attribute is updated with each completion/bet/raises.
    """
    completion_betting_or_raising_count: int = field(default=0, init=False)
    """The number of completions, bettings, or raisings.

    This attribute is incremented with each completion/bet/raises.
    """

    def _setup_betting(self) -> None:
        pass

    def _begin_betting(self) -> None:

        def card_key(rank_order: RankOrder, card: Card) -> tuple[int, Suit]:
            return rank_order.index(card.rank), card.suit

        self.opener_index = None

        assert self.street is not None

        match self.street.opening:
            case Opening.POSITION:
                max_bet_index = max(
                    self.player_indices,
                    key=lambda i: (self.bets[i], i),
                )
                self.opener_index = (max_bet_index + 1) % self.player_count
            case Opening.LOW_CARD:
                min_up_cards = [
                    min_or_none(
                        self.get_up_cards(i),
                        key=partial(
                            card_key,
                            _HighHandOpeningLookup.rank_order,
                        ),
                    ) for i in self.player_indices
                ]
                self.opener_index = min_up_cards.index(
                    min_or_none(
                        min_up_cards,
                        key=partial(
                            card_key,
                            _HighHandOpeningLookup.rank_order,
                        ),
                    ),
                )
            case Opening.HIGH_CARD:
                max_up_cards = [
                    max_or_none(
                        self.get_up_cards(i),
                        key=partial(
                            card_key,
                            _LowHandOpeningLookup.rank_order,
                        ),
                    ) for i in self.player_indices
                ]
                self.opener_index = max_up_cards.index(
                    max_or_none(
                        max_up_cards,
                        key=partial(
                            card_key,
                            _LowHandOpeningLookup.rank_order,
                        ),
                    ),
                )
            case Opening.LOW_HAND:
                entries = [
                    self.__low_hand_opening_lookup.get_entry_or_none(
                        self.get_up_cards(i),
                    ) for i in self.player_indices
                ]
                self.opener_index = entries.index(min_or_none(entries))
            case Opening.HIGH_HAND:
                entries = [
                    self.__high_hand_opening_lookup.get_entry_or_none(
                        self.get_up_cards(i),
                    ) for i in self.player_indices
                ]
                self.opener_index = entries.index(max_or_none(entries))
            case _:  # pragma: no cover
                raise AssertionError

        assert self.opener_index is not None

        self.bring_in_status = (
            self.street is self.streets[0]
            and self.bring_in > 0
        )
        self.completion_status = self.bring_in_status
        self.actor_indices = deque(self.player_indices)

        self.actor_indices.rotate(-self.opener_index)

        for i in self.player_indices:
            if (
                    not self.statuses[i]
                    or not self.stacks[i]
                    or not self.get_effective_stack(i)
            ):
                self.actor_indices.remove(i)

        self.completion_betting_or_raising_amount = 0
        self.completion_betting_or_raising_count = 0

        self._update_betting(
            status=(
                len(self.actor_indices) == 1
                and self.bets[self.actor_indices[0]] >= max(self.bets)
            )
        )

    def _update_betting(
            self,
            operation: Operation | None = None,
            status: bool = False,
    ) -> None:
        self._update(operation)

        if not self.actor_indices or sum(self.statuses) <= 1 or status:
            self._end_betting()

    def _end_betting(self) -> None:
        self.actor_indices.clear()

        assert self.street_index is not None

        if (
                sum(self.statuses) > 1
                and not any(
                    islice(self.draw_statuses, self.street_index + 1, None),
                )
        ):
            count = 0

            for i in self.player_indices:
                if self.statuses[i] and self.stacks[i]:
                    count += 1

            if count <= 1:
                self.all_in_status = True

        if not all(self.stacks) and self.street_index == len(self.streets) - 1:
            self.all_in_status = True

        self._begin_bet_collection()

    def _pop_actor_index(self) -> int:
        return self.actor_indices.popleft()

    @property
    def actor_index(self) -> int | None:
        """Return the actor index.

        The returned index denotes the index of the current actor (in
        turn to act).

        :return: The actor index if applicable, otherwise ``None``.
        """
        if not self.actor_indices:
            return None

        assert self.stacks[self.actor_indices[0]]

        return self.actor_indices[0]

    def verify_folding(self) -> None:
        """Verify the folding.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.fold`.

        :return: ``None``.
        :raises ValueError: If the folding cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('There is no player to act.')
        elif self.bring_in_status:
            raise ValueError('The player must post a bring-in or complete.')

        player_index = self.actor_index

        assert player_index is not None

        if self.bets[player_index] >= max(self.bets):
            raise ValueError('There is no reason for this player to fold.')

    def can_fold(self) -> bool:
        """Return whether theing fold can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.fold`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (100, 100, 200),
        ...     3,
        ... )
        >>> state.can_fold()
        True
        >>> state.fold()
        Folding(commentary=None, player_index=2)
        >>> state.can_fold()
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=1)
        >>> state.can_fold()
        False
        >>> state.complete_bet_or_raise_to(4)
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=4)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> state.status
        False
        >>> state.can_fold()
        False

        :return: ``True`` if the folding can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_folding()
        except (ValueError, UserWarning):
            return False

        return True

    def fold(self, *, commentary: str | None = None) -> Folding:
        """Fold.

        This mucks the player's cards and signifies that the player
        relinquishes the right to win any of the pots.

        The actor can be accessed through
        :attr:`pokerkit.state.State.actor_index`.

        :param commentary: The optional commentary.
        :return: The folding.
        :raises ValueError: If the folding cannot be done.
        """
        self.verify_folding()

        player_index = self._pop_actor_index()

        assert self.stacks[player_index]

        self._muck_hole_cards(player_index)

        assert any(self.statuses)

        operation = Folding(player_index, commentary=commentary)

        self._update_betting(operation)

        return operation

    @property
    def checking_or_calling_amount(self) -> int | None:
        """Return the checking or calling amount.

        :return: The checking or calling amount if applicable, otherwise
                 ``None``.
        """
        try:
            self.verify_checking_or_calling()
        except (ValueError, UserWarning):
            return None

        player_index = self.actor_index

        assert player_index is not None

        return min(
            self.stacks[player_index],
            max(self.bets) - self.bets[player_index],
        )

    def verify_checking_or_calling(self) -> None:
        """Verify the checking or calling.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.check_or_call`.

        :return: ``None``.
        :raises ValueError: If the checking or calling cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('There is no player to act.')
        elif self.bring_in_status:
            raise ValueError('The player must post a bring-in or complete.')

    def can_check_or_call(self) -> bool:
        """Return whether the checking or calling can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.check_or_call`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (100, 100, 200),
        ...     3,
        ... )
        >>> state.can_check_or_call()
        True
        >>> state.fold()
        Folding(commentary=None, player_index=2)
        >>> state.can_check_or_call()
        True
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> state.status
        False
        >>> state.can_check_or_call()
        False

        :return: ``True`` if the checking or calling can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_checking_or_calling()
        except (ValueError, UserWarning):
            return False

        return True

    def check_or_call(
            self,
            *,
            commentary: str | None = None,
    ) -> CheckingOrCalling:
        """Check or call.

        This entails matching or trying to match the largest outstanding
        bet by others. If nobody has yet bet in the current betting
        round, the player is said to check.

        The actor can be accessed through
        :attr:`pokerkit.state.State.actor_index`.

        :param commentary: The optional commentary.
        :return: The checking or calling.
        :raises ValueError: If the checking or calling cannot be done.
        """
        self.verify_checking_or_calling()

        amount = self.checking_or_calling_amount
        player_index = self._pop_actor_index()

        assert self.stacks[player_index]
        assert amount is not None

        self.bets[player_index] += amount
        self.stacks[player_index] -= amount
        self.payoffs[player_index] -= amount

        operation = CheckingOrCalling(
            player_index,
            amount,
            commentary=commentary,
        )

        self._update_betting(operation)

        return operation

    @property
    def effective_bring_in_amount(self) -> int | None:
        """Return the effective bring-in.

        :return: The effective bring-in amount if applicable, otherwise
                 ``None``.
        """
        try:
            self.verify_bring_in_posting()
        except (ValueError, UserWarning):
            return None

        player_index = self.actor_index

        assert player_index is not None

        return min(self.stacks[player_index], self.bring_in)

    def verify_bring_in_posting(self) -> None:
        """Verify the bring-in posting.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_bring_in`.

        :return: ``None``.
        :raises ValueError: If the bring-in posting cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('There is no player to act.')
        elif not self.bring_in_status:
            raise ValueError('The bring-in posting is forbidden.')

    def can_post_bring_in(self) -> bool:
        """Return whether the bring-in posting can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.post_bring_in`.

        :return: ``True`` if the bring-in posting can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_bring_in_posting()
        except (ValueError, UserWarning):
            return False

        return True

    def post_bring_in(
            self,
            *,
            commentary: str | None = None,
    ) -> BringInPosting:
        """Post the bring-in.

        The actor can be accessed through
        :attr:`pokerkit.state.State.actor_index`.

        :param commentary: The optional commentary.
        :return: The bring-in posting.
        :raises ValueError: If the bring-in posting cannot be done.
        """
        self.verify_bring_in_posting()

        amount = self.effective_bring_in_amount
        player_index = self._pop_actor_index()

        assert self.stacks[player_index]
        assert amount is not None
        assert not any(self.bets)
        assert self.bring_in
        assert self.completion_status
        assert self.actor_indices

        self.bets[player_index] += amount
        self.stacks[player_index] -= amount
        self.payoffs[player_index] -= amount
        self.bring_in_status = False

        operation = BringInPosting(player_index, amount, commentary=commentary)

        self._update_betting(operation)

        return operation

    @property
    def min_completion_betting_or_raising_to_amount(self) -> int | None:
        """Return the minimum completion, betting, or raising to amount.

        :return: The minimum completion, betting, or raising to amount
                 if applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_betting_or_raising()
        except (ValueError, UserWarning):
            return None

        assert self.street is not None

        amount = max(
            self.completion_betting_or_raising_amount,
            self.street.min_completion_betting_or_raising_amount,
        )

        if not self.completion_status:
            amount += max(self.bets)

        player_index = self.actor_index

        assert player_index is not None

        return min(
            self.get_effective_stack(player_index) + self.bets[player_index],
            amount,
        )

    @property
    def pot_completion_betting_or_raising_to_amount(self) -> int | None:
        """Return the pot completion, betting, or raising to amount.

        :return: The pot completion, betting, or raising to amount if
                 applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_betting_or_raising()
        except (ValueError, UserWarning):
            return None

        player_index = self.actor_index

        assert player_index is not None
        assert self.min_completion_betting_or_raising_to_amount is not None

        return min(
            self.stacks[player_index] + self.bets[player_index],
            max(
                self.min_completion_betting_or_raising_to_amount,
                2 * max(self.bets) - self.bets[player_index]
                + self.total_pot_amount,
            )
        )

    @property
    def max_completion_betting_or_raising_to_amount(self) -> int | None:
        """Return the maximum completion, betting, or raising to amount.

        :return: The maximum completion, betting, or raising to amount
                 if applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_betting_or_raising()
        except (ValueError, UserWarning):
            return None

        assert self.actor_index is not None

        match self.betting_structure:
            case BettingStructure.FIXED_LIMIT:
                amount = self.min_completion_betting_or_raising_to_amount
            case BettingStructure.POT_LIMIT:
                amount = self.pot_completion_betting_or_raising_to_amount
            case BettingStructure.NO_LIMIT:
                amount = (
                    self.stacks[self.actor_index]
                    + self.bets[self.actor_index]
                )
            case _:  # pragma: no cover
                raise AssertionError

        assert amount is not None
        assert (
            amount
            <= self.stacks[self.actor_index] + self.bets[self.actor_index]
        )

        return amount

    def _verify_completion_betting_or_raising(self) -> None:
        if not self.actor_indices:
            raise ValueError('There is no player to act.')

        assert self.street is not None

        if (
                self.completion_betting_or_raising_count
                == self.street.max_completion_betting_or_raising_count
        ):
            raise ValueError(
                'No more completion, betting, or raising is permitted.',
            )

        player_index = self.actor_index

        assert player_index is not None

        if (
                self.stacks[player_index]
                <= max(self.bets) - self.bets[player_index]
        ):
            raise ValueError(
                (
                    'The player is already covered by a previous bet/raise.'
                    ' You most likely want to just call here with'
                    ' ``pokerkit.state.State.check_or_call()``.'
                ),
            )

        for i in self.player_indices:
            if (
                    i != player_index
                    and self.statuses[i]
                    and self.stacks[i] + self.bets[i] > max(self.bets)
            ):
                break
        else:
            raise ValueError(
                (
                    'There is no reason to complete, bet, or raise since every'
                    ' other player has either folded or gone all-in.'
                ),
            )

    def verify_completion_betting_or_raising_to(
            self,
            amount: int | None = None,
    ) -> int:
        """Verify the completion, betting, or raising to.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.complete_bet_or_raise_to`.

        :param amount: The optional completion, betting, or raising to
                       amount.
        :return: The completion, betting, or raising to amount.
        :raises ValueError: If the completion, betting, or raising
                            cannot be done.
        """
        self._verify_completion_betting_or_raising()

        assert self.min_completion_betting_or_raising_to_amount is not None
        assert self.max_completion_betting_or_raising_to_amount is not None

        if amount is None:
            amount = self.min_completion_betting_or_raising_to_amount

        if amount < self.min_completion_betting_or_raising_to_amount:
            raise ValueError(
                (
                    f'The amount {amount} is below the minimum allowed'
                    f' {self.min_completion_betting_or_raising_to_amount}.'
                ),
            )
        elif amount > self.max_completion_betting_or_raising_to_amount:
            raise ValueError(
                (
                    f'The amount {amount} is above the maximum allowed'
                    f' {self.max_completion_betting_or_raising_to_amount}.'
                ),
            )

        return amount

    def can_complete_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> bool:
        """Return whether the completion, betting, or raising can be
        done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.complete_bet_or_raise_to`.

        >>> from pokerkit import (
        ...     NoLimitTexasHoldem,
        ...     FixedLimitDeuceToSevenLowballTripleDraw,
        ... )
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     (100, 100, 200),
        ...     3,
        ... )
        >>> state.can_complete_bet_or_raise_to()
        True
        >>> state.can_complete_bet_or_raise_to(4)
        True
        >>> state.can_complete_bet_or_raise_to(200)
        True
        >>> state.can_complete_bet_or_raise_to(3)
        False
        >>> state.can_complete_bet_or_raise_to(201)
        False
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=2)
        >>> state.complete_bet_or_raise_to(100)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.fold()
        Folding(commentary=None, player_index=1)
        >>> state.can_complete_bet_or_raise_to(200)
        False
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=98)
        >>> state.status
        False
        >>> state.can_complete_bet_or_raise_to()
        False

        >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
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
        ...     6,
        ... )
        >>> state.can_complete_bet_or_raise_to()
        True
        >>> state.complete_bet_or_raise_to()
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount=4)
        >>> state.can_complete_bet_or_raise_to()
        True
        >>> state.complete_bet_or_raise_to()
        CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount=6)
        >>> state.can_complete_bet_or_raise_to()
        True
        >>> state.complete_bet_or_raise_to()
        CompletionBettingOrRaisingTo(commentary=None, player_index=4, amount=8)
        >>> state.can_complete_bet_or_raise_to()
        True
        >>> state.complete_bet_or_raise_to()  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=5, amount...
        >>> state.can_complete_bet_or_raise_to()
        False
        >>> state.complete_bet_or_raise_to()
        Traceback (most recent call last):
            ...
        ValueError: No more completion, betting, or raising is permitted.

        :param amount: The optional completion, betting, or raising to
                       amount.
        :return: ``True`` if the completion, betting, or raising can be
                 done, otherwise ``False``.
        """
        try:
            self.verify_completion_betting_or_raising_to(amount)
        except (ValueError, UserWarning):
            return False

        return True

    def complete_bet_or_raise_to(
            self,
            amount: int | None = None,
            *,
            commentary: str | None = None,
    ) -> CompletionBettingOrRaisingTo:
        """Complete, bet, or raise to an amount.

        This opens the new betting round where the active players are
        forced to try to match the new bet to stay in the pot.

        The actor can be accessed through
        :attr:`pokerkit.state.State.actor_index`.

        :param amount: The optional completion, betting, or raising to
                       amount.
        :param commentary: The optional commentary.
        :return: The completion, betting, or raising to.
        :raises ValueError: If the completion, betting, or raising
                            cannot be done.
        """
        amount = self.verify_completion_betting_or_raising_to(amount)
        player_index = self._pop_actor_index()

        completion_betting_or_raising_amount = amount - max(self.bets)
        delta = amount - self.bets[player_index]
        self.bets[player_index] = amount
        self.stacks[player_index] -= delta
        self.payoffs[player_index] -= delta
        self.bring_in_status = False
        self.completion_status = False
        self.actor_indices = deque(self.player_indices)
        self.opener_index = player_index
        self.completion_betting_or_raising_amount = max(
            self.completion_betting_or_raising_amount,
            completion_betting_or_raising_amount,
        )
        self.completion_betting_or_raising_count += 1

        self.actor_indices.rotate(-player_index)
        self.actor_indices.popleft()

        for i in self.player_indices:
            if not self.statuses[i] or not self.stacks[i]:
                if i in self.actor_indices:
                    self.actor_indices.remove(i)

        assert self.actor_indices

        operation = CompletionBettingOrRaisingTo(
            player_index,
            amount,
            commentary=commentary,
        )

        self._update_betting(operation)

        return operation

    # showdown

    runout_count_selector_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The runout-count selector statuses.

    Each element denotes whether a player at that index is pending
    runout-count selection (``True``).
    """
    runout_count: int | None = field(default=None, init=False)
    """The number of runouts.

    This attribute reflects a concensus on the number of runouts
    selected by each player.

    If no one selects a preference or the hand is never all-in by all
    those who are active, this value is ``None``. If at least one person
    expresses a preference, a concensus is established and thus this
    value is not ``None``.
    """
    runout_count_selection_flag: bool = field(default=False, init=False)
    """The runout-count selector flag.

    It is ``True`` if everyone had a chance to select the number of
    runouts.
    """
    showdown_indices: deque[int] = field(default_factory=deque, init=False)
    """The showdown indices.

    The items also reflect a showdown order.
    """

    def _setup_showdown(self) -> None:
        assert not self.runout_count_selector_statuses

        for _ in range(self.player_count):
            self.runout_count_selector_statuses.append(False)

    def _begin_showdown(self) -> None:
        assert not any(self.runout_count_selector_statuses)
        assert not self.showdown_indices
        assert self.street_index is not None

        if (
                not self.runout_count_selection_flag
                and self.mode != Mode.TOURNAMENT
        ):
            status = False

            for i in range(self.street_index + 1, self.street_count):
                if self.streets[i].board_dealing_count:
                    status = True

            if status:
                for i in self.player_indices:
                    if self.statuses[i]:
                        self.runout_count_selector_statuses[i] = True

        self.showdown_indices = deque(self.player_indices)

        if self.opener_index is not None:
            self.showdown_indices.rotate(-self.opener_index)

        for i in self.player_indices:
            if not self.statuses[i] or all(self.hole_card_statuses[i]):
                self.showdown_indices.remove(i)

        self._update_showdown()

    def _update_showdown(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if (
                not any(self.runout_count_selector_statuses)
                and not self.showdown_indices
        ):
            self._end_showdown()
        else:
            if Automation.RUNOUT_COUNT_SELECTION in self.automations:
                while any(self.runout_count_selector_statuses):
                    self.select_runout_count()

            if Automation.HOLE_CARDS_SHOWING_OR_MUCKING in self.automations:
                while self.showdown_indices:
                    self.show_or_muck_hole_cards()

    def _end_showdown(self) -> None:
        assert not any(self.runout_count_selector_statuses)
        assert not self.showdown_indices
        assert self.street_index is not None

        if not self.runout_count_selection_flag:
            self.runout_count_selection_flag = True

            if self.runout_count is not None:
                self.street_return_index = self.street_index + 1
                self.street_return_count = self.runout_count - 1

        if self.all_in_status and self.street is not self.streets[-1]:
            self._begin_dealing()
        else:
            self._begin_hand_killing()

    @property
    def runout_count_selector_indices(self) -> Iterator[int]:
        """Iterate through players who can select the runout-count.

        :return: The runout-count selectors.
        """
        try:
            self._verify_runout_count_selection()
        except (ValueError, UserWarning):
            return

        for i in self.player_indices:
            if self.runout_count_selector_statuses[i]:
                yield i

    def _verify_runout_count_selection(self) -> None:
        if not any(self.runout_count_selector_statuses):
            raise ValueError('Nobody can choose the number of runouts.')

    def verify_runout_count_selection(
            self,
            runout_count: int | None = None,
            player_index: int | None = None,
    ) -> int:
        """Verify the runout-count selection.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.select_runout_count`.

        :param runout_count: The number of runouts, defaults to
                             ``None``.
        :param player_index: The optional player index.
        :return: The selecting player index.
        :raises ValueError: If the runout-count selection cannot be
                            done.
        """
        self._verify_runout_count_selection()

        if player_index is None:
            player_index = next(self.runout_count_selector_indices)

        if not self.runout_count_selector_statuses[player_index]:
            raise ValueError(
                (
                    f'The Player {player_index} cannot choose the number of'
                    ' runouts.'
                ),
            )
        elif runout_count is not None and runout_count < 1:
            raise ValueError(
                f'The runout count {runout_count} is not positive.',
            )

        return player_index

    def can_select_runout_count(
            self,
            runout_count: int | None = None,
            player_index: int | None = None,
    ) -> bool:
        """Return whether the runout-count selection can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.select_runout_count`.

        :param runout_count: The number of runouts, defaults to
                             ``None``.
        :param player_index: The optional player index.
        :return: ``True`` if the runout-count selection can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_runout_count_selection(player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def select_runout_count(
            self,
            runout_count: int | None = None,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> RunoutCountSelection:
        """Select the runout-count.

        If the ``runout_count`` is ``None``, it is considered to be
        "no-preference".

        The runout-count selection can be performed prior to or after
        the showing/mucking of the hole cards. Both are permitted by
        PokerKit.

        If the player index is not specified, the first item of
        :attr:`pokerkit.state.State.runout_count_selector_indices` will
        be used.

        :param runout_count: The number of runouts, defaults to
                             ``None``.
        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The runout-count selection.
        :raises ValueError: If the runout-count selection cannot be
                            done.
        """
        player_index = self.verify_runout_count_selection(player_index)

        assert self.runout_count_selector_statuses[player_index]

        self.runout_count_selector_statuses[player_index] = False

        if runout_count is not None:
            if self.runout_count is None:
                self.runout_count = runout_count
            elif self.runout_count != runout_count:
                self.runout_count = 1

            assert self.runout_count == runout_count or self.runout_count == 1

        operation = RunoutCountSelection(
            player_index,
            runout_count,
            commentary=commentary,
        )

        self._update_showdown(operation)

        return operation

    @property
    def showdown_index(self) -> int | None:
        """Return the showdown index.

        The index denotes who should show/muck their cards next.

        Typically, in poker games, the showdown order is determined
        through action. The last bettor/raiser must show first.

        In practice, it is encouraged for people who know they won
        for sure to show first. This means that the "ideal" showdown
        order may deviate from the actually practiced showdown order.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     3,
        ... )

        Pre-flop.

        >>> state.deal_hole('JcJd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Jc, Jd), statuse...
        >>> state.deal_hole('KcKd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc, Kd), statuse...
        >>> state.deal_hole('QcQd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Qc, Qd), statuse...
        >>> state.complete_bet_or_raise_to(6)
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount=6)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=5)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=4)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('AcAdAh')
        BoardDealing(commentary=None, cards=(Ac, Ad, Ah))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2c')
        BoardDealing(commentary=None, cards=(2c,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2d')
        BoardDealing(commentary=None, cards=(2d,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Showdown.

        >>> state.showdown_index is None
        True
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)
        >>> state.showdown_index
        0
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=0, hole_card...
        >>> state.showdown_index
        1
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...
        >>> state.showdown_index
        2
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=2, hole_card...

        :return: The showdown index if applicable, otherwise ``None``.
        """
        try:
            self._verify_hole_cards_showing_or_mucking()
        except (ValueError, UserWarning):
            return None

        return self.showdown_indices[0]

    def _verify_hole_cards_showing_or_mucking(self) -> None:
        if not self.showdown_indices:
            raise ValueError('There is no player to showdown.')

    def verify_hole_cards_showing_or_mucking(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
            player_index: int | None = None,
    ) -> tuple[bool, tuple[Card, ...] | None, int]:
        """Verify the hole card showing or mucking.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.show_or_muck_hole_cards`.

        :param status_or_hole_cards: The optional status or hole cards.
        :param player_index: The optional player index to override the
                             showdown order.
        :return: The status, what cards are shown, and player index.
        :raises ValueError: If hole card showing or mucking cannot be
                            done.
        """
        self._verify_hole_cards_showing_or_mucking()

        if player_index is None:
            player_index = self.showdown_index

        assert player_index is not None

        if player_index not in self.showdown_indices:
            raise ValueError(
                f'The Player {player_index} cannot perform a showdown.',
            )

        if isinstance(status_or_hole_cards, bool):
            status = status_or_hole_cards
            hole_cards = None
        elif status_or_hole_cards is None:
            status = self.all_in_status or self.can_win_now(player_index)
            hole_cards = None
        else:
            status = True
            hole_cards = Card.clean(status_or_hole_cards)

            self._verify_cards_consumption(
                filterfalse(
                    self.hole_cards[player_index].__contains__,
                    hole_cards,
                ),
            )

        if not status and self.all_in_status:
            raise ValueError('The player must show in an all-in situation.')

        if hole_cards is None and status:
            hole_cards = tuple(self.hole_cards[player_index])

        if hole_cards is not None and status:
            for card in hole_cards:
                if card.unknown_status:
                    raise ValueError('An unknown card is shown.')

        return status, hole_cards, player_index

    def can_show_or_muck_hole_cards(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
            player_index: int | None = None,
    ) -> bool:
        """Return whether the hole card showing or mucking can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.show_or_muck_hole_cards`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     3,
        ... )

        Pre-flop.

        >>> state.deal_hole('JcJd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Jc, Jd), statuse...
        >>> state.deal_hole('KcKd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Kc, Kd), statuse...
        >>> state.deal_hole('QcQd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Qc, Qd), statuse...
        >>> state.complete_bet_or_raise_to(6)
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount=6)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=5)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=4)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('AcAdAh')
        BoardDealing(commentary=None, cards=(Ac, Ad, Ah))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2c')
        BoardDealing(commentary=None, cards=(2c,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2d')
        BoardDealing(commentary=None, cards=(2d,))
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.can_show_or_muck_hole_cards()
        False
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=2, amount=0)

        Showdown.

        >>> state.can_show_or_muck_hole_cards()
        True
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=0, hole_card...
        >>> state.can_show_or_muck_hole_cards(False)
        True
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...
        >>> state.can_show_or_muck_hole_cards(True)
        True
        >>> state.show_or_muck_hole_cards()  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=2, hole_card...

        :param status_or_hole_cards: The optional status or hole cards.
        :param player_index: The optional player index to override the
                             showdown order.
        :return: ``True`` if the hole crad showing or mucking can be
                 done, otherwise ``False``.
        """
        try:
            self.verify_hole_cards_showing_or_mucking(
                status_or_hole_cards,
                player_index,
            )
        except (ValueError, UserWarning):
            return False

        return True

    def show_or_muck_hole_cards(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> HoleCardsShowingOrMucking:
        """Show or muck hole cards.

        If the status is not given, the hole cards will be shown if and
        only if there is chance of winning the pot. Otherwise, the hand
        will be mucked.

        If the player index is not specified, it defaults to
        :attr:`pokerkit.state.State.showdown_index`.

        :param status_or_hole_cards: The optional status or hole cards.
        :param player_index: The optional player index to override the
                             showdown order.
        :param commentary: The optional commentary.
        :return: The hole cards showing or mucking.
        """
        status, hole_cards, player_index = (
            self.verify_hole_cards_showing_or_mucking(
                status_or_hole_cards,
                player_index,
            )
        )

        self.showdown_indices.remove(player_index)

        if status:
            assert (
                (
                    not isinstance(status_or_hole_cards, bool)
                    and status_or_hole_cards is not None
                )
                or tuple(self.hole_cards[player_index]) == hole_cards
            )

            if hole_cards is not None:
                self._produce_cards(self.hole_cards[player_index])
                self.hole_cards[player_index].clear()
                self._consume_cards(hole_cards)
                self.hole_cards[player_index].extend(hole_cards)

            self._show_hole_cards(player_index)
        else:
            self._muck_hole_cards(player_index)

        operation = HoleCardsShowingOrMucking(
            player_index,
            tuple(self.hole_cards[player_index]),
            commentary=commentary,
        )

        self._update_showdown(operation)

        return operation

    # hand killing

    hand_killing_statuses: list[bool] = field(default_factory=list, init=False)
    """The hand killing statuses."""

    def _setup_hand_killing(self) -> None:
        assert not self.hand_killing_statuses

        for _ in range(self.player_count):
            self.hand_killing_statuses.append(False)

    def _begin_hand_killing(self) -> None:
        assert not any(self.hand_killing_statuses)

        for i in self.player_indices:
            if not self.statuses[i]:
                continue

            assert self.statuses[i]

            self.hand_killing_statuses[i] = not self.can_win_now(i)

        self._update_hand_killing()

    def _update_hand_killing(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if not any(self.hand_killing_statuses):
            self._end_hand_killing()
        elif Automation.HAND_KILLING in self.automations:
            while any(self.hand_killing_statuses):
                self.kill_hand()

    def _end_hand_killing(self) -> None:
        for i in self.player_indices:
            self.hand_killing_statuses[i] = False

        self._begin_chips_pushing()

    @property
    def hand_killing_indices(self) -> Iterator[int]:
        """Iterate through players who can post antes.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     3,
        ... )

        Pre-flop.

        >>> state.deal_hole('JcJd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Jc, Jd), statuse...
        >>> state.deal_hole('QcQd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Qc, Qd), statuse...
        >>> state.deal_hole('KcKd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Kc, Kd), statuse...
        >>> state.complete_bet_or_raise_to(200)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=199)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=198)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('AcAdAh')
        BoardDealing(commentary=None, cards=(Ac, Ad, Ah))

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2c')
        BoardDealing(commentary=None, cards=(2c,))
        >>> state.hand_killing_indices  # doctest: +ELLIPSIS
        <generator object State.hand_killing_indices at 0x...>
        >>> tuple(state.hand_killing_indices)
        ()

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2d')
        BoardDealing(commentary=None, cards=(2d,))
        >>> tuple(state.hand_killing_indices)
        (0, 1)

        :return: The ante posters.
        """
        try:
            self._verify_hand_killing()
        except (ValueError, UserWarning):
            return

        for i in self.player_indices:
            if self.hand_killing_statuses[i]:
                yield i

    def _verify_hand_killing(self) -> None:
        if not any(self.hand_killing_statuses):
            raise ValueError('Nobody can kill their hand.')

    def verify_hand_killing(self, player_index: int | None = None) -> int:
        """Verify the hand killing.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.kill_hand`.

        :param player_index: The optional player index.
        :return: The hand killing index.
        :raises ValueError: If the hand killing cannot be done.
        """
        self._verify_hand_killing()

        if player_index is None:
            player_index = next(self.hand_killing_indices)

        if not self.hand_killing_statuses[player_index]:
            raise ValueError(
                f'The Player {player_index} cannot kill their hand.',
            )

        return player_index

    def can_kill_hand(self, player_index: int | None = None) -> bool:
        """Return whether the hand killing can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.kill_hand`.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     3,
        ... )

        Pre-flop.

        >>> state.deal_hole('JcJd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Jc, Jd), statuse...
        >>> state.deal_hole('QcQd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Qc, Qd), statuse...
        >>> state.deal_hole('KcKd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Kc, Kd), statuse...
        >>> state.complete_bet_or_raise_to(200)  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=199)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=198)

        Flop.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('AcAdAh')
        BoardDealing(commentary=None, cards=(Ac, Ad, Ah))

        Turn.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2c')
        BoardDealing(commentary=None, cards=(2c,))
        >>> state.can_kill_hand()
        False

        River.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('2d')
        BoardDealing(commentary=None, cards=(2d,))
        >>> state.can_kill_hand()
        True
        >>> state.can_kill_hand(0)
        True
        >>> state.can_kill_hand(1)
        True
        >>> state.can_kill_hand(2)
        False

        :param player_index: The optional player index.
        :return: ``True`` if the hand killing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_hand_killing(player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def kill_hand(
            self,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> HandKilling:
        """Kill hand.

        In real-life, this is performed by the dealer to "kill" and
        remove an irrelevant hand (i.e. cannot win anything) so that
        only the relevant hands (i.e. can win at least a portion) are
        left open prior to pushing the chips to the respective winners.

        If the player is not specified, the first item of
        :attr:`pokerkit.state.State.hand_killing_indices` will be used.

        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The hand killing.
        :raises ValueError: If the hand killing cannot be done.
        """
        player_index = self.verify_hand_killing(player_index)
        self.hand_killing_statuses[player_index] = False

        self._muck_hole_cards(player_index)

        operation = HandKilling(player_index, commentary=commentary)

        self._update_hand_killing(operation)

        return operation

    # chips pushing

    _pots: list[Pot] | None = field(default=None, init=False)
    _sub_pots: list[tuple[int, int, int, int]] = field(
        default_factory=list,
        init=False,
    )

    def _setup_chips_pushing(self) -> None:
        pass

    def _begin_chips_pushing(self) -> None:
        assert self._pots is None
        assert not self._sub_pots

        self.street_index = None
        self._pots = list(self.pots)

        if sum(self.statuses) == 1:
            for i, pot in enumerate(self._pots):
                self._sub_pots.append((pot.unraked_amount, i, -1, -1))
        elif sum(self.statuses) > 1:
            for i, pot in enumerate(self._pots):
                amount = pot.unraked_amount
                quotient, remainder = self.divmod(amount, self.board_count)

                for j in self.board_indices:
                    sub_amount = quotient

                    if not j:
                        sub_amount += remainder

                    hand_type_indices = []

                    for k in self.hand_type_indices:
                        for hand in self.get_up_hands(j, k):
                            if hand is not None:
                                hand_type_indices.append(k)

                                break

                    hand_type_count = len(hand_type_indices)
                    sub_quotient, sub_remainder = self.divmod(
                        sub_amount,
                        hand_type_count,
                    )

                    for k in hand_type_indices:
                        sub_sub_amount = sub_quotient

                        if k == hand_type_indices[0]:
                            sub_sub_amount += sub_remainder

                        if sub_sub_amount:
                            self._sub_pots.append((sub_sub_amount, i, j, k))

        self._update_chips_pushing()

    def _update_chips_pushing(
            self,
            operation: Operation | None = None,
    ) -> None:
        self._update(operation)

        if not self._sub_pots:
            self._end_chips_pushing()
        elif Automation.CHIPS_PUSHING in self.automations:
            while self._sub_pots:
                self.push_chips()

    def _end_chips_pushing(self) -> None:
        assert self._pots is not None
        assert not self._sub_pots

        self._begin_chips_pulling()

    def verify_chips_pushing(self) -> None:
        """Verify the chips pushing.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.push_chips`.

        :return: ``None``.
        :raises ValueError: If the chips pushing cannot be done.
        """
        if not self._sub_pots:
            raise ValueError('The chip pushing is not allowed.')

    def can_push_chips(self) -> bool:
        """Return whether the chips pushing can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.push_chips`.

        >>> from pokerkit import FixedLimitDeuceToSevenLowballTripleDraw
        >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     3,
        ... )
        >>> state.can_push_chips()
        False
        >>> state.fold()
        Folding(commentary=None, player_index=2)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> state.can_push_chips()
        True

        :return: ``True`` if the chips pushing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chips_pushing()
        except (ValueError, UserWarning):
            return False

        return True

    def push_chips(self, *, commentary: str | None = None) -> ChipsPushing:
        """Push chips.

        Each call of this operation will push a single split main/side
        pot.

        :param commentary: The optional commentary.
        :return: The chips pushing.
        :raises ValueError: If the chips pushing cannot be done.
        """
        self.verify_chips_pushing()

        assert self._pots is not None and self._sub_pots

        bets = self.bets.copy()
        amount, pot_index, board_index, hand_type_index = self._sub_pots.pop(0)
        pot = self._pots[pot_index]
        pot.unraked_amount -= amount

        assert pot.unraked_amount >= 0

        if sum(self.statuses) == 1:
            assert len(pot.player_indices) == 1
            assert board_index == hand_type_index == -1

            self.bets[pot.player_indices[0]] += amount
        else:
            assert 0 <= board_index < self.board_count
            assert 0 <= hand_type_index < self.hand_type_count

            hands = tuple(self.get_up_hands(board_index, hand_type_index))
            max_hand = max_or_none(
                map(partial(getitem, hands), pot.player_indices),
            )
            player_indices = [
                i for i in pot.player_indices if hands[i] == max_hand
            ]
            quotient, remainder = self.divmod(amount, len(player_indices))

            for i in player_indices:
                assert self.statuses[i]

                sub_sub_sub_amount = quotient

                if i == player_indices[0]:
                    sub_sub_sub_amount += remainder

                self.bets[i] += sub_sub_sub_amount

        operation = ChipsPushing(
            tuple(starmap(sub, zip(self.bets, bets))),
            pot_index,
            board_index,
            hand_type_index,
            commentary=commentary,
        )

        self._update_chips_pushing(operation)

        return operation

    # chips pulling

    chips_pulling_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The chips pulling statuses."""

    def _setup_chips_pulling(self) -> None:
        assert not self.chips_pulling_statuses

        for _ in range(self.player_count):
            self.chips_pulling_statuses.append(False)

    def _begin_chips_pulling(self) -> None:
        assert not any(self.chips_pulling_statuses)

        for i in self.player_indices:
            self.chips_pulling_statuses[i] = self.bets[i] > 0

        self._update_chips_pulling()

    def _update_chips_pulling(
            self,
            operation: Operation | None = None,
    ) -> None:
        self._update(operation)

        if not any(self.chips_pulling_statuses):
            self._end_chips_pulling()
        elif Automation.CHIPS_PULLING in self.automations:
            while any(self.chips_pulling_statuses):
                self.pull_chips()

    def _end_chips_pulling(self) -> None:
        for i in self.player_indices:
            self.chips_pulling_statuses[i] = False

        self._end()

    @property
    def chips_pulling_indices(self) -> Iterator[int]:
        """Iterate through players who can pull chips.

        >>> from pokerkit import FixedLimitDeuceToSevenLowballTripleDraw
        >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     3,
        ... )
        >>> state.chips_pulling_indices  # doctest: +ELLIPSIS
        <generator object State.chips_pulling_indices at 0x...>
        >>> tuple(state.chips_pulling_indices)
        ()
        >>> state.fold()
        Folding(commentary=None, player_index=2)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> tuple(state.chips_pulling_indices)
        (1,)

        :return: The chips pullers.
        """
        try:
            self._verify_chips_pulling()
        except (ValueError, UserWarning):
            return None

        for i in self.player_indices:
            if self.chips_pulling_statuses[i]:
                yield i

    def _verify_chips_pulling(self) -> None:
        if not any(self.chips_pulling_statuses):
            raise ValueError('No one can pull chips.')

    def verify_chips_pulling(self, player_index: int | None = None) -> int:
        """Verify the chips pulling.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.pull_chips`.

        :param player_index: The optional player index.
        :return: The chips pulling index.
        :raises ValueError: If the chips pulling cannot be done.
        """
        self._verify_chips_pulling()

        if player_index is None:
            player_index = next(self.chips_pulling_indices)

        if not self.chips_pulling_statuses[player_index]:
            raise ValueError('There is no chip to be pulled.')

        return player_index

    def can_pull_chips(self, player_index: int | None = None) -> bool:
        """Return whether the chips pulling can be done.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.pull_chips`.

        >>> from pokerkit import FixedLimitDeuceToSevenLowballTripleDraw
        >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_DEALING,
        ...         Automation.BOARD_DEALING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...     ),
        ...     False,
        ...     0,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     3,
        ... )
        >>> state.can_pull_chips()
        False
        >>> state.fold()
        Folding(commentary=None, player_index=2)
        >>> state.fold()
        Folding(commentary=None, player_index=0)
        >>> state.can_pull_chips()
        True
        >>> state.can_pull_chips(0)
        False
        >>> state.can_pull_chips(1)
        True
        >>> state.can_pull_chips(2)
        False

        :param player_index: The optional player index.
        :return: ``True`` if the chips pulling can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chips_pulling(player_index)
        except (ValueError, UserWarning):
            return False

        return True

    def pull_chips(
            self,
            player_index: int | None = None,
            *,
            commentary: str | None = None,
    ) -> ChipsPulling:
        """Pull chips.

        Here, the won chip in front of a player is incorporated back
        into his/her stack.

        If the player is not specified, the first item of
        :attr:`pokerkit.state.State.chips_pulling_indices` will be used.

        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The chips pulling.
        :raises ValueError: If the chips pulling cannot be done.
        """
        player_index = self.verify_chips_pulling(player_index)
        amount = self.bets[player_index]

        self.stacks[player_index] += amount
        self.payoffs[player_index] += amount
        self.bets[player_index] = 0
        self.chips_pulling_statuses[player_index] = False

        operation = ChipsPulling(player_index, amount, commentary=commentary)

        self._update_chips_pulling(operation)

        return operation

    def verify_no_operation(self) -> None:
        """Verify the no-operation.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.no_operate`.

        :return: ``None``.
        """
        pass

    def can_no_operate(self) -> bool:
        """Return whether the no-operation can be done. Always ``True``.

        For more details on this operation, please consult the method
        :attr:`pokerkit.state.State.no_operate`.

        :return: ``True``.
        """
        try:
            self.verify_no_operation()
        except (ValueError, UserWarning):
            return False

        return True

    def no_operate(
            self,
            *,
            commentary: str | None = None,
    ) -> NoOperation:
        """No-operate.

        :return: The no-operation.
        """
        self.verify_no_operation()

        operation = NoOperation(commentary=commentary)

        self._update(operation)

        return operation
