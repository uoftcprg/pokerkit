""":mod:`pokerkit.state` implements classes related to poker states."""

from collections import Counter, deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import StrEnum, unique
from functools import partial
from itertools import chain, islice
from operator import getitem
from random import shuffle

from pokerkit.hands import Hand
from pokerkit.lookups import Label, Lookup
from pokerkit.utilities import (
    Card,
    CardsLike,
    Deck,
    RankOrder,
    Suit,
    max_or_none,
    min_or_none,
)


@unique
class BettingStructure(StrEnum):
    """The enum class for betting structures.

    >>> BettingStructure.FIXED_LIMIT
    <BettingStructure.FIXED_LIMIT: 'Fixed-limit'>
    >>> BettingStructure.NO_LIMIT
    <BettingStructure.NO_LIMIT: 'No-limit'>
    """

    FIXED_LIMIT = 'Fixed-limit'
    """The fixed-limit."""
    POT_LIMIT = 'Pot-limit'
    """The pot-limit."""
    NO_LIMIT = 'No-limit'
    """The no-limit."""


@unique
class Opening(StrEnum):
    """The enum class for openings.

    >>> Opening.POSITION
    <Opening.POSITION: 'Position'>
    >>> Opening.LOW_HAND
    <Opening.LOW_HAND: 'Low hand'>
    """

    POSITION = 'Position'
    """The opener is decided by position.

    If blinds or straddles are present, they are taken account of.
    """
    LOW_CARD = 'Low card'
    """The opener is decided by having the lowest exposed card."""
    HIGH_CARD = 'High card'
    """The opener is decided by having the highest exposed card."""
    LOW_HAND = 'Low hand'
    """The opener is decided by having the lowest exposed hand, then
    position.
    """
    HIGH_HAND = 'High hand'
    """The opener is decided by having the highest exposed hand, then
    position.
    """


@dataclass
class _LowHandOpeningLookup(Lookup):
    def __post_init__(self) -> None:
        for i in range(1, 5):
            self._add_multisets(
                RankOrder.REGULAR,
                Counter({1: i}),
                (False, True),
                Label.HIGH_CARD,
            )

        for i in range(3):
            self._add_multisets(
                RankOrder.REGULAR,
                Counter({2: 1, 1: i}),
                (False,),
                Label.ONE_PAIR,
            )

        self._add_multisets(
            RankOrder.REGULAR,
            Counter({2: 2}),
            (False,),
            Label.TWO_PAIR,
        )

        for i in range(2):
            self._add_multisets(
                RankOrder.REGULAR,
                Counter({3: 1, 1: i}),
                (False,),
                Label.THREE_OF_A_KIND,
            )

        self._add_multisets(
            RankOrder.REGULAR,
            Counter({4: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )


@dataclass
class _HighHandOpeningLookup(Lookup):
    def __post_init__(self) -> None:
        for i in range(1, 5):
            self._add_multisets(
                RankOrder.STANDARD,
                Counter({1: i}),
                (False, True),
                Label.HIGH_CARD,
            )

        for i in range(3):
            self._add_multisets(
                RankOrder.STANDARD,
                Counter({2: 1, 1: i}),
                (False,),
                Label.ONE_PAIR,
            )

        self._add_multisets(
            RankOrder.STANDARD,
            Counter({2: 2}),
            (False,),
            Label.TWO_PAIR,
        )

        for i in range(2):
            self._add_multisets(
                RankOrder.STANDARD,
                Counter({3: 1, 1: i}),
                (False,),
                Label.THREE_OF_A_KIND,
            )

        self._add_multisets(
            RankOrder.STANDARD,
            Counter({4: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )


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

    >>> street = Street(
    ...     False,
    ...     (False, False),
    ...     -1,
    ...     False,
    ...     Opening.POSITION,
    ...     2,
    ...     None,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: negative number of dealt cards
    >>> street = Street(
    ...     False,
    ...     (),
    ...     0,
    ...     False,
    ...     Opening.POSITION,
    ...     2,
    ...     None,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: no dealing
    >>> street = Street(
    ...     True,
    ...     (False, False),
    ...     0,
    ...     True,
    ...     Opening.POSITION,
    ...     2,
    ...     None,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: dealing hole and standing pat or discarding
    >>> street = Street(
    ...     True,
    ...     (False, False),
    ...     0,
    ...     False,
    ...     Opening.POSITION,
    ...     0,
    ...     None,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: non-positive minimum completion, betting, or raising amount
    >>> street = Street(
    ...     True,
    ...     (False, False),
    ...     0,
    ...     False,
    ...     Opening.POSITION,
    ...     2,
    ...     -1,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: negative maximum number of completions, bettings, or raisings
    """

    card_burning_status: bool
    """Whether to burn card."""
    hole_dealing_statuses: tuple[bool, ...]
    """The statuses of dealt hole cards."""
    board_dealing_count: int
    """The number of dealt board cards."""
    draw_status: bool
    """Whether to draw cards prior to betting."""
    opening: Opening
    """The opening."""
    min_completion_betting_or_raising_amount: int
    """The minimum completion, betting, or raising amount."""
    max_completion_betting_or_raising_count: int | None
    """The maximum number of completions, bettings, or raisings."""

    def __post_init__(self) -> None:
        if self.board_dealing_count < 0:
            raise ValueError('negative number of dealt cards')
        elif (
                not self.hole_dealing_statuses
                and not self.board_dealing_count
                and not self.draw_status
        ):
            raise ValueError('no dealing')
        elif self.hole_dealing_statuses and self.draw_status:
            raise ValueError('dealing hole and standing pat or discarding')
        elif self.min_completion_betting_or_raising_amount <= 0:
            raise ValueError(
                'non-positive minimum completion, betting, or raising amount',
            )
        elif (
                self.max_completion_betting_or_raising_count is not None
                and self.max_completion_betting_or_raising_count < 0
        ):
            raise ValueError(
                'negative maximum number of completions, bettings, or '
                'raisings',
            )


@unique
class Automation(StrEnum):
    """The enum class for automation.

    >>> Automation.ANTE_POSTING
    <Automation.ANTE_POSTING: 'Ante posting'>
    >>> Automation.CARD_BURNING
    <Automation.CARD_BURNING: 'Card burning'>
    """

    ANTE_POSTING = 'Ante posting'
    """The ante posting automation."""
    BET_COLLECTION = 'Bet collection'
    """The bet collection automation."""
    BLIND_OR_STRADDLE_POSTING = 'Blind or straddle posting'
    """The blind or straddle posting automation."""
    CARD_BURNING = 'Card burning'
    """The card burning automation."""
    HOLE_DEALING = 'Hole dealing'
    """The hole dealing automation."""
    BOARD_DEALING = 'Board dealing'
    """The board dealing automation."""
    HOLE_CARDS_SHOWING_OR_MUCKING = 'Hole cards showing or mucking'
    """The hole cards showing or mucking automation."""
    HAND_KILLING = 'Hand killing'
    """The hand killing automation."""
    CHIPS_PUSHING = 'Chips pushing'
    """The chips pushing automation."""
    CHIPS_PULLING = 'Chips pulling'
    """The chips pulling automation."""


@dataclass(frozen=True)
class Pot:
    """The class for pots.

    >>> pot = Pot(100, (1, 3))
    >>> pot.amount
    100
    >>> pot.player_indices
    (1, 3)

    >>> pot = Pot(-1, (1, 3))
    Traceback (most recent call last):
        ...
    ValueError: negative pot amount
    >>> pot = Pot(10, ())
    Traceback (most recent call last):
        ...
    ValueError: empty player indices
    """

    amount: int
    """The amount."""
    player_indices: tuple[int, ...]
    """The player indices of those who contributed."""

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError('negative pot amount')
        elif not self.player_indices:
            raise ValueError('empty player indices')


@dataclass
class State:
    """The class for states.

    Below code shows an example Kuhn poker game with all non-player
    actions and showdown automated.

    >>> from pokerkit import KuhnPokerHand
    >>> state = State(
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
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    >>> state.status
    True
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.hole_cards  # doctest: +ELLIPSIS
    [[...s], [...s]]
    >>> state.check_or_call()
    State.CheckingOrCalling(player_index=0, amount=0)
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.complete_bet_or_raise_to()
    State.CompletionBettingOrRaisingTo(player_index=1, amount=1)
    >>> state.stacks
    [1, 0]
    >>> state.bets
    [0, 1]
    >>> state.fold()
    State.Folding(player_index=0)
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
    ...     (),
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    >>> state.status
    True
    >>> state.post_ante(0)
    State.AntePosting(player_index=0, amount=1)
    >>> state.post_ante(1)
    State.AntePosting(player_index=1, amount=1)
    >>> state.collect_bets()
    State.BetCollection(bets=(1, 1))
    >>> state.deal_hole('Js')
    State.HoleDealing(player_index=0, cards=(Js,), statuses=(False,))
    >>> state.deal_hole()  # doctest: +ELLIPSIS
    State.HoleDealing(player_index=1, cards=(...s,), statuses=(False,))
    >>> state.check_or_call()
    State.CheckingOrCalling(player_index=0, amount=0)
    >>> state.complete_bet_or_raise_to()
    State.CompletionBettingOrRaisingTo(player_index=1, amount=1)
    >>> state.fold()
    State.Folding(player_index=0)
    >>> state.collect_bets()
    State.BetCollection(bets=(0, 0))
    >>> state.push_chips()
    State.ChipsPushing(amounts=(0, 3))
    >>> state.pull_chips(1)
    State.ChipsPulling(player_index=1, amount=3)
    >>> state.status
    False

    >>> state = State(
    ...     Deck.KUHN_POKER,
    ...     (KuhnPokerHand,),
    ...     (),
    ...     BettingStructure.FIXED_LIMIT,
    ...     (),
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: empty streets
    >>> state = State(
    ...     Deck.KUHN_POKER,
    ...     (KuhnPokerHand,),
    ...     (
    ...         Street(
    ...             True,
    ...             (),
    ...             3,
    ...             False,
    ...             Opening.POSITION,
    ...             1,
    ...             None,
    ...         ),
    ...     ),
    ...     BettingStructure.FIXED_LIMIT,
    ...     (),
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: first street not hole dealing
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (-1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: negative antes, blinds, straddles, or bring-in
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (0,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: no antes, blinds, straddles, or bring-in
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2, 0),
    ... )
    Traceback (most recent call last):
        ...
    ValueError: non-positive starting stacks
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (0,) * 2,
    ...     (1,) * 2,
    ...     1,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: both bring-in and blinds or straddles specified
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (0,) * 2,
    ...     (0,) * 2,
    ...     1,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: bring-in must be less than the min bet
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (1,),
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: inconsistent number of players
    >>> state = State(
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
    ...     (),
    ...     True,
    ...     (1,),
    ...     (0,),
    ...     0,
    ...     (2,),
    ... )
    Traceback (most recent call last):
        ...
    ValueError: not enough players
    """

    __low_hand_opening_lookup = _LowHandOpeningLookup()
    __high_hand_opening_lookup = _HighHandOpeningLookup()
    deck: Deck
    """The deck."""
    hand_types: tuple[type[Hand], ...]
    """The hand types."""
    streets: tuple[Street, ...]
    """The streets."""
    betting_structure: BettingStructure
    """The betting structure."""
    automations: tuple[Automation, ...]
    """The automations."""
    ante_trimming_status: bool
    """The ante trimming status.

    Usually, if you want uniform antes, set this to ``True``.
    If you want non-uniform antes like big blind antes, set
    this to ``False``.
    """
    antes: tuple[int, ...]
    """The antes."""
    blinds_or_straddles: tuple[int, ...]
    """The blinds or straddles."""
    bring_in: int
    """The bring-in."""
    starting_stacks: tuple[int, ...]
    """The starting stacks."""
    deck_cards: deque[Card] = field(default_factory=deque, init=False)
    """The deck cards."""
    board_cards: list[Card] = field(default_factory=list, init=False)
    """The board cards."""
    mucked_cards: list[Card] = field(default_factory=list, init=False)
    """The mucked cards."""
    burned_cards: list[Card] = field(default_factory=list, init=False)
    """The burned cards."""
    statuses: list[bool] = field(default_factory=list, init=False)
    """The player statuses."""
    bets: list[int] = field(default_factory=list, init=False)
    """The player bets."""
    stacks: list[int] = field(default_factory=list, init=False)
    """The player stacks."""
    hole_cards: list[list[Card]] = field(default_factory=list, init=False)
    """The player hole cards."""
    hole_card_statuses: list[list[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The player hole card statuses."""
    street_index: int | None = field(default=None, init=False)
    """The street index."""
    status: bool = field(default=True, init=False)
    """The game status."""

    def __post_init__(self) -> None:
        if not self.streets:
            raise ValueError('empty streets')
        elif not self.streets[0].hole_dealing_statuses:
            raise ValueError('first street not hole dealing')
        elif (
                min(self.antes) < 0
                or min(self.blinds_or_straddles) < 0
                or self.bring_in < 0
        ):
            raise ValueError('negative antes, blinds, straddles, or bring-in')
        elif (
                not any(self.antes)
                and not any(self.blinds_or_straddles)
                and not self.bring_in
        ):
            raise ValueError('no antes, blinds, straddles, or bring-in')
        elif min(self.starting_stacks) <= 0:
            raise ValueError('non-positive starting stacks')
        elif any(self.blinds_or_straddles) and self.bring_in:
            raise ValueError('both bring-in and blinds or straddles specified')
        elif (
                self.bring_in
                >= self.streets[0].min_completion_betting_or_raising_amount
        ):
            raise ValueError('bring-in must be less than the min bet')
        elif not (
                len(self.antes)
                == len(self.blinds_or_straddles)
                == len(self.starting_stacks)
        ):
            raise ValueError('inconsistent number of players')
        elif self.player_count < 2:
            raise ValueError('not enough players')

        self._setup()
        self._begin()

    def _setup(self) -> None:
        self.deck_cards.extend(self.deck)

        shuffle(self.deck_cards)

        for i in self.player_indices:
            self.statuses.append(True)
            self.bets.append(0)
            self.stacks.append(self.starting_stacks[i])
            self.hole_cards.append([])
            self.hole_card_statuses.append([])

        self._setup_ante_posting()
        self._setup_bet_collection()
        self._setup_blind_or_straddle_posting()
        self._setup_dealing()
        self._setup_hand_killing()
        self._setup_chips_pulling()

    def _begin(self) -> None:
        self._begin_ante_posting()

    def _end(self) -> None:
        self.status = False

    @property
    def hand_type_count(self) -> int:
        """Return the number of hand types.

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
    def player_count(self) -> int:
        """Return the number of players.

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
        >>> state.player_count
        2
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (),
        ...     True,
        ...     1,
        ...     (1, 2),
        ...     2,
        ...     200,
        ...     9,
        ... )
        >>> state.player_count
        9

        :return: The number of players.
        """
        return len(self.starting_stacks)

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
        >>> state.post_ante(1)
        State.AntePosting(player_index=1, amount=2)
        >>> state.collect_bets()
        State.BetCollection(bets=(0, 2))
        >>> state.post_blind_or_straddle(0)
        State.BlindOrStraddlePosting(player_index=0, amount=2)
        >>> state.street is None
        True
        >>> state.post_blind_or_straddle(1)
        State.BlindOrStraddlePosting(player_index=1, amount=1)
        >>> state.street is state.streets[0]
        True
        >>> state.street  # doctest: +ELLIPSIS
        Street(...)
        >>> state.deal_hole('Ac')
        State.HoleDealing(player_index=0, cards=(Ac,), statuses=(False,))
        >>> state.deal_hole('Kc')
        State.HoleDealing(player_index=1, cards=(Kc,), statuses=(False,))
        >>> state.deal_hole('Ad')
        State.HoleDealing(player_index=0, cards=(Ad,), statuses=(False,))
        >>> state.deal_hole('Kd')
        State.HoleDealing(player_index=1, cards=(Kd,), statuses=(False,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.street is state.streets[0]
        True
        >>> state.collect_bets()
        State.BetCollection(bets=(2, 2))
        >>> state.street is state.streets[1]
        True
        >>> state.burn_card('2c')
        State.CardBurning(card=2c)
        >>> state.deal_board('AhKhAs')
        State.BoardDealing(cards=(Ah, Kh, As))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.street is state.streets[1]
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.street is state.streets[2]
        True
        >>> state.burn_card('2d')
        State.CardBurning(card=2d)
        >>> state.deal_board('Ks')
        State.BoardDealing(cards=(Ks,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.street is state.streets[2]
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.street is state.streets[3]
        True
        >>> state.burn_card('2h')
        State.CardBurning(card=2h)
        >>> state.deal_board('2s')
        State.BoardDealing(cards=(2s,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.street is state.streets[3]
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.street is None
        True
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=0, status=True)
        >>> state.street is None
        True
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=1, status=False)
        >>> state.street is None
        True
        >>> state.push_chips()
        State.ChipsPushing(amounts=(6, 0))
        >>> state.street is None
        True
        >>> state.pull_chips()
        State.ChipsPulling(player_index=0, amount=6)
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
        State.Folding(player_index=1)
        >>> state.street is None
        True

        :return: The street if applicable, otherwise ``None``.
        """
        if self.street_index is None:
            return None

        return self.streets[self.street_index]

    @property
    def total_pot_amount(self) -> int:
        """Return the total pot amount.

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
        >>> state.post_ante(1)
        State.AntePosting(player_index=1, amount=2)
        >>> state.total_pot_amount
        2
        >>> state.collect_bets()
        State.BetCollection(bets=(0, 2))
        >>> state.total_pot_amount
        2
        >>> state.post_blind_or_straddle(0)
        State.BlindOrStraddlePosting(player_index=0, amount=2)
        >>> state.total_pot_amount
        4
        >>> state.post_blind_or_straddle(1)
        State.BlindOrStraddlePosting(player_index=1, amount=1)
        >>> state.total_pot_amount
        5
        >>> state.deal_hole('Ac')
        State.HoleDealing(player_index=0, cards=(Ac,), statuses=(False,))
        >>> state.deal_hole('Kc')
        State.HoleDealing(player_index=1, cards=(Kc,), statuses=(False,))
        >>> state.deal_hole('Ad')
        State.HoleDealing(player_index=0, cards=(Ad,), statuses=(False,))
        >>> state.deal_hole('Kd')
        State.HoleDealing(player_index=1, cards=(Kd,), statuses=(False,))
        >>> state.total_pot_amount
        5
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.total_pot_amount
        6
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.collect_bets()
        State.BetCollection(bets=(2, 2))
        >>> state.burn_card('2c')
        State.CardBurning(card=2c)
        >>> state.deal_board('AhKhAs')
        State.BoardDealing(cards=(Ah, Kh, As))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.burn_card('2d')
        State.CardBurning(card=2d)
        >>> state.deal_board('Ks')
        State.BoardDealing(cards=(Ks,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.total_pot_amount
        6
        >>> state.complete_bet_or_raise_to(10)
        State.CompletionBettingOrRaisingTo(player_index=1, amount=10)
        >>> state.total_pot_amount
        16
        >>> state.complete_bet_or_raise_to(30)
        State.CompletionBettingOrRaisingTo(player_index=0, amount=30)
        >>> state.total_pot_amount
        46
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=20)
        >>> state.collect_bets()
        State.BetCollection(bets=(30, 30))
        >>> state.total_pot_amount
        66
        >>> state.burn_card('2h')
        State.CardBurning(card=2h)
        >>> state.deal_board('2s')
        State.BoardDealing(cards=(2s,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=0, status=True)
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=1, status=False)
        >>> state.push_chips()
        State.ChipsPushing(amounts=(66, 0))
        >>> state.total_pot_amount
        66
        >>> state.pull_chips()
        State.ChipsPulling(player_index=0, amount=66)
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
        State.Folding(player_index=1)
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
        ...     None,
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
        >>> state.complete_bet_or_raise_to(200)
        State.CompletionBettingOrRaisingTo(player_index=2, amount=200)
        >>> state.complete_bet_or_raise_to(1000)
        Traceback (most recent call last):
            ...
        ValueError: irrelevant completion, betting, or raising
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=3, amount=200)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=4, amount=200)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=5, amount=100)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=49)
        >>> tuple(state.pots)
        ()
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=98)
        >>> next(state.pots)
        Pot(amount=300, player_indices=(0, 1, 2, 3, 4, 5))
        >>> pots = tuple(state.pots)
        >>> len(pots)
        3
        >>> pots[0]
        Pot(amount=300, player_indices=(0, 1, 2, 3, 4, 5))
        >>> pots[1]
        Pot(amount=250, player_indices=(1, 2, 3, 4, 5))
        >>> pots[2]
        Pot(amount=300, player_indices=(2, 3, 4))
        >>> state.deal_board()  # doctest: +ELLIPSIS
        State.BoardDealing(cards=(..., ..., ...))
        >>> state.deal_board()  # doctest: +ELLIPSIS
        State.BoardDealing(cards=(...,))
        >>> state.deal_board()  # doctest: +ELLIPSIS
        State.BoardDealing(cards=(...,))
        >>> next(state.pots)
        Traceback (most recent call last):
            ...
        StopIteration
        >>> tuple(state.pots)
        ()

        :return: The list of main and side pots (if any).
        """
        if sum(self.stacks) + sum(self.bets) == sum(self.starting_stacks):
            return

        contributions = list(self.starting_stacks)
        pending_contributions = list(self.starting_stacks)
        previous_contribution = 0
        amount = 0

        if self.ante_trimming_status:
            for i in self.player_indices:
                assert self.stacks[i] <= self.starting_stacks[i]

                contributions[i] -= self.bets[i] + self.stacks[i]
                pending_contributions[i] -= self.stacks[i]
        else:
            total_ante = 0

            for i in self.player_indices:
                assert self.stacks[i] <= self.starting_stacks[i]

                ante = self.get_effective_ante(i)
                total_ante += ante
                contributions[i] -= ante + self.bets[i] + self.stacks[i]
                pending_contributions[i] -= ante + self.stacks[i]

            amount = total_ante

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

            yield Pot(amount, tuple(player_indices))

            previous_contribution = contribution
            amount = 0

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
        ...     None,
        ...     1,
        ...     2,
        ...     4,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.deal_hole('AcAdAh')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Ac, Ad, Ah), statuses=(Fals...
        >>> state.deal_hole('KcKdKh')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Kc, Kd, Kh), statuses=(Fals...
        >>> state.get_down_cards(0)  # doctest: +ELLIPSIS
        <generator object State.get_down_cards at 0x...>
        >>> tuple(state.get_down_cards(0))
        (Ac, Ad)
        >>> tuple(state.get_down_cards(1))
        (Kc, Kd)
        >>> state.post_bring_in()
        State.BringInPosting(player_index=1, amount=1)
        >>> state.fold()
        State.Folding(player_index=0)
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
        ...     None,
        ...     1,
        ...     2,
        ...     4,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.deal_hole('AcAdAh')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Ac, Ad, Ah), statuses=(Fals...
        >>> state.deal_hole('KcKdKh')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Kc, Kd, Kh), statuses=(Fals...
        >>> state.get_down_cards(0)  # doctest: +ELLIPSIS
        <generator object State.get_down_cards at 0x...>
        >>> tuple(state.get_up_cards(0))
        (Ah,)
        >>> tuple(state.get_up_cards(1))
        (Kh,)
        >>> state.post_bring_in()
        State.BringInPosting(player_index=1, amount=1)
        >>> state.fold()
        State.Folding(player_index=0)
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

    def get_hand(self, player_index: int, hand_type_index: int) -> Hand | None:
        """Return the corresponding hand of the player.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_hand(0, 0) is None
        True
        >>> state.get_hand(1, 0) is None
        True
        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Ac, Ad), statuses=(False, F...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Ks, Qs), statuses=(False, F...
        >>> state.get_hand(0, 0) is None
        True
        >>> state.get_hand(1, 0) is None
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.deal_board('JsTs2c')
        State.BoardDealing(cards=(Js, Ts, 2c))
        >>> state.get_hand(0, 0)
        AcAdJsTs2c
        >>> str(state.get_hand(0, 0))
        'One pair (AcAdJsTs2c)'
        >>> str(state.get_hand(1, 0))
        'High card (KsQsJsTs2c)'
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('Ah')
        State.BoardDealing(cards=(Ah,))
        >>> str(state.get_hand(0, 0))
        'Three of a kind (AcAdJsTsAh)'
        >>> str(state.get_hand(1, 0))
        'Straight (KsQsJsTsAh)'
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('As')
        State.BoardDealing(cards=(As,))
        >>> str(state.get_hand(0, 0))
        'Four of a kind (AcAdJsAhAs)'
        >>> str(state.get_hand(1, 0))
        'Straight flush (KsQsJsTsAs)'
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.get_hand(0, 0) is None
        True
        >>> str(state.get_hand(1, 0))
        'Straight flush (KsQsJsTsAs)'

        :param player_index: The player index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player if applicable,
                 otherwise ``None``.
        """
        if not self.statuses[player_index]:
            return None

        try:
            hand = self.hand_types[hand_type_index].from_game(
                self.hole_cards[player_index],
                self.board_cards,
            )
        except ValueError:
            hand = None

        return hand

    def get_up_hand(
            self,
            player_index: int,
            hand_type_index: int,
    ) -> Hand | None:
        """Return the corresponding hand of the player from up cards.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
        True
        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Ac, Ad), statuses=(False, F...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Ks, Qs), statuses=(False, F...
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.deal_board('JsTs2c')
        State.BoardDealing(cards=(Js, Ts, 2c))
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('Ah')
        State.BoardDealing(cards=(Ah,))
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
        True
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('As')
        State.BoardDealing(cards=(As,))
        >>> str(state.get_up_hand(0, 0))
        'One pair (JsTs2cAhAs)'
        >>> str(state.get_up_hand(1, 0))
        'One pair (JsTs2cAhAs)'
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.get_up_hand(0, 0) is None
        True
        >>> str(state.get_up_hand(1, 0))
        'Straight flush (KsQsJsTsAs)'

        :param player_index: The player index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player.
        """
        if not self.statuses[player_index]:
            return None

        try:
            hand = self.hand_types[hand_type_index].from_game(
                self.get_up_cards(player_index),
                self.board_cards,
            )
        except ValueError:
            hand = None

        return hand

    def get_up_hands(self, hand_type_index: int) -> Iterator[Hand | None]:
        """Return the optional corresponding hands from up cards.

        >>> from pokerkit import NoLimitTexasHoldem
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
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.get_up_hands(0)  # doctest: +ELLIPSIS
        <generator object State.get_up_hands at 0x...>
        >>> tuple(state.get_up_hands(0))
        (None, None)
        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Ac, Ad), statuses=(False, F...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Ks, Qs), statuses=(False, F...
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.deal_board('JsTs2c')
        State.BoardDealing(cards=(Js, Ts, 2c))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('Ah')
        State.BoardDealing(cards=(Ah,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('As')
        State.BoardDealing(cards=(As,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> tuple(state.get_up_hands(0))
        (JsTs2cAhAs, JsTs2cAhAs)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> tuple(state.get_up_hands(0))
        (None, KsQsJsTsAs)

        :param hand_type_index: The hand type index.
        :return: The optional corresponding hands from up cards.
        """
        for i in self.player_indices:
            yield self.get_up_hand(i, hand_type_index)

    def can_win_now(self, player_index: int) -> bool:
        """Return whether if the player might win pots based on
        the available information to a player.

        It is assumed that no more card is dealt.

        >>> from pokerkit import NoLimitTexasHoldem
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIPS_PUSHING,
        ...         Automation.CHIPS_PULLING,
        ...     ),
        ...     True,
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     (50, 100),
        ...     2,
        ... )
        >>> state.deal_hole('KhQh')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=0, cards=(Kh, Qh), statuses=(False, F...
        >>> state.deal_hole('AcKc')  # doctest: +ELLIPSIS
        State.HoleDealing(player_index=1, cards=(Ac, Kc), statuses=(False, F...
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=1)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.deal_board('JsTs2c')
        State.BoardDealing(cards=(Js, Ts, 2c))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('Ah')
        State.BoardDealing(cards=(Ah,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.deal_board('As')
        State.BoardDealing(cards=(As,))
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=0, amount=0)
        >>> state.check_or_call()
        State.CheckingOrCalling(player_index=1, amount=0)
        >>> state.can_win_now(0)
        True
        >>> state.can_win_now(1)
        True
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=0, status=True)
        >>> state.can_win_now(0)
        True
        >>> state.can_win_now(1)
        False
        >>> state.show_or_muck_hole_cards()
        State.HoleCardsShowingOrMucking(player_index=1, status=False)

        :param player_index: The player index.
        :return: ``True`` if the player can win, otherwise ``False``.
        """
        for i in self.hand_type_indices:
            hands = tuple(self.get_up_hands(i))
            hand = self.get_hand(player_index, i)

            for pot in self.pots:
                max_hand = max_or_none(
                    map(partial(getitem, hands), pot.player_indices),
                )

                if hand is not None and (max_hand is None or max_hand <= hand):
                    return True

        return False

    def _muck_hole_cards(self, player_index: int) -> None:
        assert self.statuses[player_index]

        for i, card in enumerate(self.hole_cards[player_index]):
            self.mucked_cards.append(card)

        self.statuses[player_index] = False
        self.hole_cards[player_index].clear()
        self.hole_card_statuses[player_index].clear()

    def _show_hole_cards(self, player_index: int) -> None:
        assert self.statuses[player_index]

        for i in range(len(self.hole_cards[player_index])):
            self.hole_card_statuses[player_index][i] = True

    # ante posting

    ante_posting_statuses: list[bool] = field(default_factory=list, init=False)
    """The player ante posting statuses."""

    def _setup_ante_posting(self) -> None:
        assert not self.ante_posting_statuses

        for _ in range(self.player_count):
            self.ante_posting_statuses.append(False)

    def _begin_ante_posting(self) -> None:
        assert not any(self.ante_posting_statuses)

        for i in self.player_indices:
            self.ante_posting_statuses[i] = self.get_effective_ante(i) > 0

        if not any(self.ante_posting_statuses):
            self._end_ante_posting()
        elif Automation.ANTE_POSTING in self.automations:
            while any(self.ante_posting_statuses):
                self.post_ante()

    def _end_ante_posting(self) -> None:
        assert not any(self.ante_posting_statuses)

        self._begin_bet_collection()

    @dataclass
    class AntePosting:
        """The ante posting."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    def get_effective_ante(self, player_index: int) -> int:
        """Return the effective ante of the player.

        :param player_index: The player index.
        :return: The effective ante.
        """
        return min(
            self.antes[player_index],
            self.starting_stacks[player_index],
        )

    @property
    def ante_poster_indices(self) -> Iterator[int]:
        """Iterate through players who can post antes.

        :return: The ante posters.
        """
        try:
            self._verify_ante_posting()
        except ValueError:
            return

        for i in self.player_indices:
            if self.ante_posting_statuses[i]:
                yield i

    def _verify_ante_posting(self) -> None:
        if not any(self.ante_posting_statuses):
            raise ValueError('nobody can post the ante')

    def verify_ante_posting(self, player_index: int | None = None) -> int:
        """Verify the ante posting.

        :param player_index: The optional player index.
        :return: The anteing player index.
        :raises ValueError: If the ante posting cannot be done.
        """
        self._verify_ante_posting()

        if player_index is None:
            player_index = next(self.ante_poster_indices)

        if not self.ante_posting_statuses[player_index]:
            raise ValueError('player cannot post the ante')

        return player_index

    def can_post_ante(self, player_index: int | None = None) -> bool:
        """Return whether the ante posting can be done.

        :param player_index: The optional player index.
        :return: ``True`` if the ante posting can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_ante_posting(player_index)
        except ValueError:
            return False

        return True

    def post_ante(self, player_index: int | None = None) -> AntePosting:
        """Post the ante.

        :param player_index: The optional player index.
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

        if not any(self.ante_posting_statuses):
            self._end_ante_posting()

        return self.AntePosting(player_index, amount)

    # bet collection

    bet_collection_status: bool = field(default=False, init=False)
    """The bet collection status."""

    def _setup_bet_collection(self) -> None:
        assert not self.bet_collection_status

    def _begin_bet_collection(self) -> None:
        assert not self.bet_collection_status

        self.bet_collection_status = any(self.bets)

        if not self.bet_collection_status:
            self._end_bet_collection()
        elif Automation.BET_COLLECTION in self.automations:
            self.collect_bets()

    def _end_bet_collection(self) -> None:
        assert not self.bet_collection_status

        if sum(self.statuses) == 1:
            self._begin_chips_pushing()
        elif self.street is None:
            self._begin_blind_or_straddle_posting()
        elif self.street is self.streets[-1]:
            self._begin_showdown()
        else:
            self._begin_dealing()

    @dataclass
    class BetCollection:
        """The bet collection."""

        bets: tuple[int, ...]
        """The bets."""

        @property
        def total_bets(self) -> int:
            """Return the total bets.

            :return: The total bets.
            """
            return sum(self.bets)

    def verify_bet_collection(self) -> None:
        """Verify the bet collection.

        :return: ``None``.
        :raises ValueError: If the bet collection cannot be done.
        """
        if not self.bet_collection_status:
            raise ValueError('bet collection prohibited')

    def can_collect_bets(self) -> bool:
        """Return whether the bet collection can be done.

        :return: ``True`` if the bet collection can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_bet_collection()
        except ValueError:
            return False

        return True

    def collect_bets(self) -> BetCollection:
        """Collect the bets.

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

                    self.stacks[i] += self.bets[i] - bet_cutoff
                    bets[i] = bet_cutoff

        for i in player_indices:
            self.bets[i] = 0

        self._end_bet_collection()

        return self.BetCollection(tuple(bets))

    # blind or straddle posting

    blind_or_straddle_posting_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The player blind or straddle statuses."""

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

        if not any(self.blind_or_straddle_posting_statuses):
            self._end_blind_or_straddle_posting()
        elif Automation.BLIND_OR_STRADDLE_POSTING in self.automations:
            while any(self.blind_or_straddle_posting_statuses):
                self.post_blind_or_straddle()

    def _end_blind_or_straddle_posting(self) -> None:
        assert not any(self.blind_or_straddle_posting_statuses)

        self._begin_dealing()

    @dataclass
    class BlindOrStraddlePosting:
        """The blind or straddle posting."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    def get_effective_blind_or_straddle(self, player_index: int) -> int:
        """Return the effective blind or straddle of the player.

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

        :return: The blind or straddle posters.
        """
        try:
            self._verify_blind_or_straddle_posting()
        except ValueError:
            return

        for i in self.player_indices:
            if self.blind_or_straddle_posting_statuses[i]:
                yield i

    def _verify_blind_or_straddle_posting(self) -> None:
        if not any(self.blind_or_straddle_posting_statuses):
            raise ValueError('nobody can post the blind or straddle')

    def verify_blind_or_straddle_posting(
            self,
            player_index: int | None = None,
    ) -> int:
        """Verify the blind or straddle posting.

        :param player_index: The optional player index.
        :return: The blinding or straddling player index.
        :raises ValueError: If blind or straddle posting cannot be done.
        """
        self._verify_blind_or_straddle_posting()

        if player_index is None:
            player_index = next(self.blind_or_straddle_poster_indices)

        if not self.blind_or_straddle_posting_statuses[player_index]:
            raise ValueError('player cannot post the blind or straddle')

        return player_index

    def can_post_blind_or_straddle(
            self,
            player_index: int | None = None,
    ) -> bool:
        """Return whether the blind or straddle posting can be done.

        :param player_index: The optional player index.
        :return: ``True`` if the blind or straddle posting can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_blind_or_straddle_posting(player_index)
        except ValueError:
            return False

        return True

    def post_blind_or_straddle(
            self,
            player_index: int | None = None,
    ) -> BlindOrStraddlePosting:
        """Post the blind or straddle of the player.

        :param player_index: The optional player index.
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

        if not any(self.blind_or_straddle_posting_statuses):
            self._end_blind_or_straddle_posting()

        return self.BlindOrStraddlePosting(player_index, amount)

    # dealing

    card_burning_status: bool = field(default=False, init=False)
    """The card burning status."""
    hole_dealing_statuses: list[deque[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The hole dealing statuses."""
    board_dealing_count: int = field(default=0, init=False)
    """The board dealing count."""
    standing_pat_or_discarding_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The standing pat or discarding statuses."""

    def _setup_dealing(self) -> None:
        assert not self.hole_dealing_statuses
        assert not self.standing_pat_or_discarding_statuses

        for _ in range(self.player_count):
            self.hole_dealing_statuses.append(deque())
            self.standing_pat_or_discarding_statuses.append(False)

    def _begin_dealing(self) -> None:
        assert not self.card_burning_status
        assert not any(self.hole_dealing_statuses)
        assert not self.board_dealing_count
        assert not any(self.standing_pat_or_discarding_statuses)

        if self.street_index is None:
            self.street_index = 0
        else:
            self.street_index += 1

        assert 0 <= self.street_index < len(self.streets)
        assert self.street is not None

        self.card_burning_status = self.street.card_burning_status
        self.board_dealing_count = self.street.board_dealing_count

        for i in self.player_indices:
            if self.statuses[i]:
                self.hole_dealing_statuses[i].extend(
                    self.street.hole_dealing_statuses,
                )
                self.standing_pat_or_discarding_statuses[i] = (
                    self.street.draw_status
                )

        assert (
            any(self.hole_dealing_statuses)
            or self.board_dealing_count
            or any(self.standing_pat_or_discarding_statuses)
        )

        if (
                not self.card_burning_status
                and not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
                and not any(self.standing_pat_or_discarding_statuses)
        ):
            self._end_dealing()
        else:
            if (
                    Automation.CARD_BURNING in self.automations
                    and self.card_burning_status
            ):
                self.burn_card()

            if Automation.HOLE_DEALING in self.automations:
                while any(self.hole_dealing_statuses):
                    self.deal_hole()

            if (
                    Automation.BOARD_DEALING in self.automations
                    and self.board_dealing_count
            ):
                self.deal_board()

    def _end_dealing(self) -> None:
        assert not self.card_burning_status
        assert not any(self.hole_dealing_statuses)
        assert not self.board_dealing_count
        assert not any(self.standing_pat_or_discarding_statuses)

        self._begin_betting()

    def _make_card_available(self, cards: tuple[Card, ...]) -> None:
        assert len(self.deck_cards) >= len(cards)

        for card in cards:
            assert card in self.burned_cards or card in self.deck_cards

            if card in self.burned_cards:
                self.burned_cards[self.burned_cards.index(card)] = (
                    self.deck_cards.popleft()
                )
            else:
                self.deck_cards.remove(card)

    @property
    def available_cards(self) -> Iterator[Card]:
        """Iterate through the available cards that can be dealt or
        burned.

        :return: The available cards.
        """
        if (
                self.card_burning_status
                or any(self.hole_dealing_statuses)
                or self.board_dealing_count
        ):
            yield from chain(self.deck_cards, self.burned_cards)

    def verify_card_availabilities(
            self,
            cards: CardsLike | int,
    ) -> tuple[Card, ...]:
        """Verify the card availability.

        :param cards: The optional cards.
        :return: The available cards.
        :raises ValueError: If the card is unavailable.
        """
        if isinstance(cards, int):
            cards = tuple(islice(self.available_cards, cards))
        else:
            cards = Card.clean(cards)

            for card in cards:
                if card not in tuple(self.available_cards):
                    raise ValueError('unavailable card')

        return cards

    @dataclass
    class CardBurning:
        """The card burning."""

        card: Card
        """The card."""

    def verify_card_burning(
            self,
            card: Card | str | None = None,
    ) -> Card:
        """Verify the card burning.

        :param card: The optional card.
        :return: The burned card.
        :raises ValueError: If the card burning cannot be done.
        """
        cards = self.verify_card_availabilities(1 if card is None else card)

        if len(cards) != 1:
            raise ValueError('expected one card')

        card, = cards

        if not self.card_burning_status:
            raise ValueError('no pending burns')

        return card

    def can_burn_card(self, card: Card | str | None = None) -> bool:
        """Return whether the card burning can be done.

        :param card: The optional card.
        :return: ``True`` if the card burning can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_card_burning(card)
        except ValueError:
            return False

        return True

    def burn_card(self, card: Card | str | None = None) -> CardBurning:
        """Burn a card.

        :param card: The optional card.
        :return: The card burning.
        :raises ValueError: If the card burning cannot be done.
        """
        card = self.verify_card_burning(card)

        assert self.card_burning_status
        assert self.street is not None
        assert (
            any(self.hole_dealing_statuses)
            or self.board_dealing_count
            or self.street.draw_status
        )

        self._make_card_available((card,))

        self.card_burning_status = False
        self.burned_cards.append(card)

        if (
                not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
                and not any(self.standing_pat_or_discarding_statuses)
        ):
            self._end_dealing()

        return self.CardBurning(card)

    @dataclass
    class HoleDealing:
        """The hole dealing."""

        player_index: int
        """The player index."""
        cards: tuple[Card, ...]
        """The cards."""
        statuses: tuple[bool, ...]
        """The statuses."""

    @property
    def hole_dealee_index(self) -> int | None:
        """Return the hole dealee index.

        :return: The hole dealee index if applicable, otherwise
                 ``None``.
        """
        try:
            self._verify_hole_dealing()
        except ValueError:
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
            raise ValueError('card must be burnt')
        elif not any(self.hole_dealing_statuses):
            raise ValueError('nobody can be dealt hole cards')

    def verify_hole_dealing(
            self,
            cards: CardsLike | int | None = None,
    ) -> tuple[Card, ...]:
        """Verify the hole dealing.

        :param cards: The optional cards.
        :return: The dealt hole cards.
        :raises ValueError: If the hole dealing cannot be done.
        """
        self._verify_hole_dealing()

        cards = self.verify_card_availabilities(1 if cards is None else cards)
        player_index = self.hole_dealee_index

        assert player_index is not None

        if not 0 < len(cards) <= len(self.hole_dealing_statuses[player_index]):
            raise ValueError('invalid number of cards')

        return cards

    def can_deal_hole(self, cards: CardsLike | int | None = None) -> bool:
        """Return whether the hole dealing can be done.

        :param cards: The optional cards.
        :return: ``True`` if the hole dealing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_hole_dealing(cards)
        except ValueError:
            return False

        return True

    def deal_hole(self, cards: CardsLike | int | None = None) -> HoleDealing:
        """Deal the hole.

        :param cards: The optional cards.
        :return: The hole dealing.
        :raises ValueError: If the hole dealing cannot be done.
        """
        cards = self.verify_hole_dealing(cards)
        player_index = self.hole_dealee_index
        statuses = []

        assert player_index is not None
        assert self.hole_dealing_statuses[player_index]

        self._make_card_available(cards)

        for card in cards:
            status = self.hole_dealing_statuses[player_index].popleft()

            statuses.append(status)
            self.hole_cards[player_index].append(card)
            self.hole_card_statuses[player_index].append(status)

        if (
                not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
        ):
            self._end_dealing()

        return self.HoleDealing(player_index, cards, tuple(statuses))

    @dataclass
    class BoardDealing:
        """The board dealing."""

        cards: tuple[Card, ...]
        """The cards."""

    def verify_board_dealing(
            self,
            cards: CardsLike | int | None = None,
    ) -> tuple[Card, ...]:
        """Verify the board dealing.

        :param cards: The optional cards.
        :return: The dealt board cards.
        :raises ValueError: If the board dealing cannot be done.
        """
        if self.card_burning_status:
            raise ValueError('card must be burnt')
        elif not self.board_dealing_count:
            raise ValueError('no pending board dealing')

        cards = self.verify_card_availabilities(
            self.board_dealing_count if cards is None else cards,
        )

        if not 0 < len(cards) <= self.board_dealing_count:
            raise ValueError('invalid number of cards')

        return cards

    def can_deal_board(self, cards: CardsLike | int | None = None) -> bool:
        """Return whether the board dealing can be done.

        :param cards: The optional cards.
        :param player_index: The optional player index.
        :return: ``True`` if the board dealing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_board_dealing(cards)
        except ValueError:
            return False

        return True

    def deal_board(self, cards: CardsLike | int | None = None) -> BoardDealing:
        """Deal the board.

        :param cards: The optional cards.
        :return: The board dealing.
        :raises ValueError: If the board dealing cannot be done.
        """
        cards = self.verify_board_dealing(cards)

        assert self.board_dealing_count

        self._make_card_available(cards)

        self.board_dealing_count -= len(cards)
        self.board_cards.extend(cards)

        if (
                not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
                and not any(self.standing_pat_or_discarding_statuses)
        ):
            self._end_dealing()

        return self.BoardDealing(cards)

    @dataclass
    class StandingPatOrDiscarding:
        """The standing pat or discarding."""

        player_index: int
        """The player index."""
        cards: tuple[Card, ...]
        """The cards."""

    @property
    def stander_pat_or_discarder_index(self) -> int | None:
        """Return the stander pat or discarder index.

        :return: The stander pat or discarder index if applicable,
                 otherwise ``None``.
        """
        try:
            self._verify_standing_pat_or_discarding()
        except ValueError:
            return None

        return self.standing_pat_or_discarding_statuses.index(True)

    def _verify_standing_pat_or_discarding(self) -> None:
        if not any(self.standing_pat_or_discarding_statuses):
            raise ValueError('no pending discards')

    def verify_standing_pat_or_discarding(
            self,
            cards: CardsLike = None,
    ) -> tuple[Card, ...]:
        """Verify the discard.

        :param cards: The optional discarded cards.
        :return: The discarded cards.
        :raises ValueError: If the discard cannot be done.
        """
        self._verify_standing_pat_or_discarding()

        cards = Card.clean(cards)
        player_index = self.stander_pat_or_discarder_index

        assert player_index is not None

        if not set(cards) <= set(self.hole_cards[player_index]):
            raise ValueError('discarded cards not a subset of hole cards')

        return cards

    def can_stand_pat_or_discard(self, cards: CardsLike = None) -> bool:
        """Return whether the discard can be done.

        :param cards: The optional discarded cards.
        :return: ``True`` if the discard can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_standing_pat_or_discarding(cards)
        except ValueError:
            return False

        return True

    def stand_pat_or_discard(
            self,
            cards: CardsLike = None,
    ) -> StandingPatOrDiscarding:
        """Discard hole cards.

        :param cards: The optional discarded cards.
        :return: The standing pat or discarding.
        :raises ValueError: If the discard cannot be done.
        """
        cards = self.verify_standing_pat_or_discarding(cards)
        player_index = self.stander_pat_or_discarder_index

        assert player_index is not None
        assert self.standing_pat_or_discarding_statuses[player_index]

        self.standing_pat_or_discarding_statuses[player_index] = False

        for card in cards:
            index = self.hole_cards[player_index].index(card)

            self.hole_dealing_statuses[player_index].append(
                self.hole_card_statuses[player_index][index],
            )
            self.hole_cards[player_index].pop(index)
            self.hole_card_statuses[player_index].pop(index)

        if (
                not self.card_burning_status
                and not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
                and not any(self.standing_pat_or_discarding_statuses)
        ):
            self._end_dealing()
        elif Automation.HOLE_DEALING in self.automations:
            while any(self.hole_dealing_statuses):
                self.deal_hole()

        return self.StandingPatOrDiscarding(player_index, cards)

    # betting

    opener_index: int | None = field(default=None, init=False)
    """The opener index."""
    bring_in_status: bool = field(default=False, init=False)
    """The bring-in status."""
    completion_status: bool = field(default=False, init=False)
    """The completion status."""
    actor_indices: deque[int] = field(default_factory=deque, init=False)
    """The actor indices."""
    completion_betting_or_raising_amount: int = field(default=0, init=False)
    """The last completion, betting, or raising amount."""
    completion_betting_or_raising_count: int = field(default=0, init=False)
    """The number of completions, bettings, or raisings."""

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
                        key=partial(card_key, RankOrder.STANDARD),
                    ) for i in self.player_indices
                ]
                self.opener_index = min_up_cards.index(
                    min_or_none(
                        min_up_cards,
                        key=partial(card_key, RankOrder.STANDARD),
                    ),
                )
            case Opening.HIGH_CARD:
                max_up_cards = [
                    max_or_none(
                        self.get_up_cards(i),
                        key=partial(card_key, RankOrder.REGULAR),
                    ) for i in self.player_indices
                ]
                self.opener_index = max_up_cards.index(
                    max_or_none(
                        max_up_cards,
                        key=partial(card_key, RankOrder.REGULAR),
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
            case _:
                raise ValueError('unknown opening')

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

        if (
                not self.actor_indices
                or (
                    len(self.actor_indices) == 1
                    and self.bets[self.actor_indices[0]] >= max(self.bets)
                )
        ):
            self._end_betting()

    def _end_betting(self) -> None:
        self.actor_indices.clear()

        show = False

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
                show = True

        if not all(self.stacks) and self.street_index == len(self.streets) - 1:
            show = True

        if show:
            for i in self.player_indices:
                if self.statuses[i]:
                    self._show_hole_cards(i)

        self._begin_bet_collection()

    def _pop_actor_index(self) -> int:
        return self.actor_indices.popleft()

    @property
    def actor_index(self) -> int | None:
        """Return the actor index.

        :return: The actor index if applicable, otherwise ``None``.
        """
        if not self.actor_indices:
            return None

        assert self.stacks[self.actor_indices[0]]

        return self.actor_indices[0]

    def get_effective_stack(self, player_index: int) -> int:
        """Return the effective stack of the player.

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

    @dataclass
    class Folding:
        """The folding."""

        player_index: int
        """The player index."""

    def verify_folding(self) -> None:
        """Verify the folding.

        :return: ``None``.
        :raises ValueError: If the folding cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')

        player_index = self.actor_index

        assert player_index is not None

        if self.bets[player_index] >= max(self.bets):
            raise ValueError('redundant fold')

    def can_fold(self) -> bool:
        """Return whether theing fold can be done.

        :return: ``True`` if the folding can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_folding()
        except ValueError:
            return False

        return True

    def fold(self) -> Folding:
        """Fold.

        :return: The folding.
        :raises ValueError: If the folding cannot be done.
        """
        self.verify_folding()

        player_index = self._pop_actor_index()

        assert self.stacks[player_index]

        self._muck_hole_cards(player_index)

        assert any(self.statuses)

        if not self.actor_indices or sum(self.statuses) <= 1:
            self._end_betting()

        return self.Folding(player_index)

    @dataclass
    class CheckingOrCalling:
        """The checking or calling."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    @property
    def checking_or_calling_amount(self) -> int | None:
        """Return the checking or calling amount.

        :return: The checking or calling amount if applicable, otherwise
                 ``None``.
        """
        try:
            self.verify_checking_or_calling()
        except ValueError:
            return None

        player_index = self.actor_index

        assert player_index is not None

        return min(
            self.stacks[player_index],
            max(self.bets) - self.bets[player_index],
        )

    def verify_checking_or_calling(self) -> None:
        """Verify the checking or calling.

        :return: ``None``.
        :raises ValueError: If the checking or calling cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')

    def can_check_or_call(self) -> bool:
        """Return whether the checking or calling can be done.

        :return: ``True`` if the checking or calling can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_checking_or_calling()
        except ValueError:
            return False

        return True

    def check_or_call(self) -> CheckingOrCalling:
        """Check or call.

        :return: The checking or calling.
        :raises ValueError: If the checking or calling cannot be done.
        """
        self.verify_checking_or_calling()

        amount = self.checking_or_calling_amount
        player_index = self._pop_actor_index()

        assert self.stacks[player_index]
        assert amount is not None

        self.stacks[player_index] -= amount
        self.bets[player_index] += amount

        if not self.actor_indices:
            self._end_betting()

        return self.CheckingOrCalling(player_index, amount)

    @dataclass
    class BringInPosting:
        """The bring-in posting."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    @property
    def effective_bring_in_amount(self) -> int | None:
        """Return the effective bring-in.

        :return: The effective bring-in amount if applicable, otherwise
                 ``None``.
        """
        try:
            self.verify_bring_in_posting()
        except ValueError:
            return None

        player_index = self.actor_index

        assert player_index is not None

        return min(self.stacks[player_index], self.bring_in)

    def verify_bring_in_posting(self) -> None:
        """Verify the bring-in posting.

        :return: ``None``.
        :raises ValueError: If the bring-in posting cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif not self.bring_in_status:
            raise ValueError('bring-in cannot be posted')

    def can_post_bring_in(self) -> bool:
        """Return whether the bring-in posting can be done.

        :return: ``True`` if the bring-in posting can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_bring_in_posting()
        except ValueError:
            return False

        return True

    def post_bring_in(self) -> BringInPosting:
        """Post the bring-in.

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

        self.stacks[player_index] -= amount
        self.bets[player_index] += amount
        self.bring_in_status = False

        return self.BringInPosting(player_index, amount)

    @dataclass
    class CompletionBettingOrRaisingTo:
        """The completion, betting, or raising to."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    @property
    def min_completion_betting_or_raising_to_amount(self) -> int | None:
        """Return the minimum completion, betting, or raising to amount.

        :return: The minimum completion, betting, or raising to amount
                 if applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_betting_or_raising()
        except ValueError:
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
        except ValueError:
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
        except ValueError:
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
            case _:
                raise AssertionError

        assert amount is not None
        assert (
            amount
            <= self.stacks[self.actor_index] + self.bets[self.actor_index]
        )

        return amount

    def _verify_completion_betting_or_raising(self) -> None:
        if not self.actor_indices:
            raise ValueError('no player to act')

        assert self.street is not None

        if (
                self.completion_betting_or_raising_count
                == self.street.max_completion_betting_or_raising_count
        ):
            raise ValueError(
                'no more completion, betting, or raising permitted',
            )

        player_index = self.actor_index

        assert player_index is not None

        if (
                self.stacks[player_index]
                <= max(self.bets) - self.bets[player_index]
        ):
            raise ValueError('not enough chips in stack')

        for i in self.player_indices:
            if (
                    i != player_index
                    and self.statuses[i]
                    and self.stacks[i] + self.bets[i] > max(self.bets)
            ):
                break
        else:
            raise ValueError('irrelevant completion, betting, or raising')

    def verify_completion_betting_or_raising_to(
            self,
            amount: int | None = None,
    ) -> int:
        """Verify the completion, betting, or raising to.

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
                'below min completion, betting, or raising to amount',
            )
        elif amount > self.max_completion_betting_or_raising_to_amount:
            raise ValueError(
                'above max completion, betting, or raising to amount',
            )

        return amount

    def can_complete_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> bool:
        """Return whether the completion, betting, or raising can be
        done.

        :param amount: The optional completion, betting, or raising to
                       amount.
        :return: ``True`` if the completion, betting, or raising can be
                 done, otherwise ``False``.
        """
        try:
            self.verify_completion_betting_or_raising_to(amount)
        except ValueError:
            return False

        return True

    def complete_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> CompletionBettingOrRaisingTo:
        """Complete, bet, or raise to an amount.

        :param amount: The optional completion, betting, or raising to
                       amount.
        :return: The completion, betting, or raising to.
        :raises ValueError: If the completion, betting, or raising
                            cannot be done.
        """
        amount = self.verify_completion_betting_or_raising_to(amount)
        player_index = self._pop_actor_index()

        completion_betting_or_raising_amount = amount - max(self.bets)
        self.stacks[player_index] -= amount - self.bets[player_index]
        self.bets[player_index] = amount
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

        return self.CompletionBettingOrRaisingTo(player_index, amount)

    # showdown

    showdown_indices: deque[int] = field(default_factory=deque, init=False)
    """The showdown indices."""

    def _begin_showdown(self) -> None:
        assert not self.showdown_indices

        self.street_index = None
        self.showdown_indices = deque(self.player_indices)

        if self.opener_index is not None:
            self.showdown_indices.rotate(-self.opener_index)

        for i in self.player_indices:
            if not self.statuses[i] or all(self.hole_card_statuses[i]):
                self.showdown_indices.remove(i)

        if not self.showdown_indices:
            self._end_showdown()
        elif Automation.HOLE_CARDS_SHOWING_OR_MUCKING in self.automations:
            while self.showdown_indices:
                self.show_or_muck_hole_cards()

    def _end_showdown(self) -> None:
        assert not self.showdown_indices

        self._begin_hand_killing()

    @dataclass
    class HoleCardsShowingOrMucking:
        """The hole cards showing or mucking."""

        player_index: int
        """The player index."""
        status: bool
        """The status."""

    @property
    def showdown_index(self) -> int | None:
        """Return the showdown index.

        :return: The showdown index if applicable, otherwise ``None``.
        """
        try:
            self._verify_hole_cards_showing_or_mucking()
        except ValueError:
            return None

        return self.showdown_indices[0]

    def _pop_showdown_index(self) -> int:
        return self.showdown_indices.popleft()

    def _verify_hole_cards_showing_or_mucking(self) -> None:
        if not self.showdown_indices:
            raise ValueError('no player to act')

    def verify_hole_cards_showing_or_mucking(
            self,
            status: bool | None = None,
    ) -> bool:
        """Verify the hole card showing or mucking.

        :param status: The optional status.
        :return: The status.
        :raises ValueError: If hole card showing or mucking cannot be
                            done.
        """
        self._verify_hole_cards_showing_or_mucking()

        player_index = self.showdown_index

        assert player_index is not None

        if status is None:
            status = self.can_win_now(player_index)

        return status

    def can_show_or_muck_hole_cards(self, status: bool | None = None) -> bool:
        """Return whether the hole card showing or mucking can be done.

        :param status: The optional status.
        :return: ``True`` if the hole crad showing or mucking can be
                 done, otherwise ``False``.
        """
        try:
            self.verify_hole_cards_showing_or_mucking(status)
        except ValueError:
            return False

        return True

    def show_or_muck_hole_cards(
            self,
            status: bool | None = None,
    ) -> HoleCardsShowingOrMucking:
        """Show or muck hole cards.

        If the status is not given, the hole cards will be shown if and
        only if there is chance of winning the pot. Otherwise, the hand
        will be mucked.

        :param status: The optional status.
        :return: The hole cards showing or mucking.
        """
        status = self.verify_hole_cards_showing_or_mucking(status)
        player_index = self._pop_showdown_index()

        if status:
            self._show_hole_cards(player_index)
        else:
            self._muck_hole_cards(player_index)

        if not self.showdown_indices:
            self._end_showdown()

        return self.HoleCardsShowingOrMucking(player_index, status)

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

        if not any(self.hand_killing_statuses):
            self._end_hand_killing()
        elif Automation.HAND_KILLING in self.automations:
            while any(self.hand_killing_statuses):
                self.kill_hand()

    def _end_hand_killing(self) -> None:
        for i in self.player_indices:
            self.hand_killing_statuses[i] = False

        self._begin_chips_pushing()

    @dataclass
    class HandKilling:
        """The hand killing."""

        player_index: int
        """The player index."""

    @property
    def hand_killing_indices(self) -> Iterator[int]:
        """Iterate through players who can post antes.

        :return: The ante posters.
        """
        try:
            self._verify_hand_killing()
        except ValueError:
            return

        for i in self.player_indices:
            if self.hand_killing_statuses[i]:
                yield i

    def _verify_hand_killing(self) -> None:
        if not any(self.hand_killing_statuses):
            raise ValueError('nobody can kill his or her hand')

    def verify_hand_killing(self, player_index: int | None = None) -> int:
        """Verify the hand killing.

        :param player_index: The optional player index.
        :return: The hand killing index.
        :raises ValueError: If the hand killing cannot be done.
        """
        self._verify_hand_killing()

        if player_index is None:
            player_index = next(self.hand_killing_indices)

        if not self.hand_killing_statuses[player_index]:
            raise ValueError('player cannot kill his or her hand')

        return player_index

    def can_kill_hand(self, player_index: int | None = None) -> bool:
        """Return whether the hand killing can be done.

        :param player_index: The optional player index.
        :return: ``True`` if the hand killing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_hand_killing(player_index)
        except ValueError:
            return False

        return True

    def kill_hand(self, player_index: int | None = None) -> HandKilling:
        """Kill hand.

        :param player_index: The optional player index.
        :return: The hand killing.
        :raises ValueError: If the hand killing cannot be done.
        """
        player_index = self.verify_hand_killing(player_index)
        self.hand_killing_statuses[player_index] = False

        self._muck_hole_cards(player_index)

        if not any(self.hand_killing_statuses):
            self._end_hand_killing()

        return self.HandKilling(player_index)

    # chips pushing

    chips_pushing_status: bool = field(default=False, init=False)
    """The chips pushing status."""

    def _begin_chips_pushing(self) -> None:
        assert not self.chips_pushing_status

        self.street_index = None
        self.chips_pushing_status = True

        if Automation.CHIPS_PUSHING in self.automations:
            self.push_chips()

    def _end_chips_pushing(self) -> None:
        self.chips_pushing_status = False

        self._begin_chips_pulling()

    @dataclass
    class ChipsPushing:
        """The chips pushing."""

        amounts: tuple[int, ...]
        """The amounts."""

        @property
        def total_amount(self) -> int:
            """Return the total amount.

            :return: The total amount.
            """
            return sum(self.amounts)

    def verify_chips_pushing(self) -> None:
        """Verify the chips pushing.

        :return: ``None``.
        :raises ValueError: If the chips pushing cannot be done.
        """
        if not self.chips_pushing_status:
            raise ValueError('chips push not allowed')

    def can_push_chips(self) -> bool:
        """Return whether the chips pushing can be done.

        :return: ``True`` if the chips pushing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chips_pushing()
        except ValueError:
            return False

        return True

    def push_chips(self) -> ChipsPushing:
        """Push chips.

        :return: The chips pushing.
        :raises ValueError: If the chips pushing cannot be done.
        """
        self.verify_chips_pushing()

        self.chips_pushing_status = False

        if sum(self.statuses) == 1:
            for pot in self.pots:
                assert len(pot.player_indices) == 1

                self.bets[pot.player_indices[0]] += pot.amount
        else:

            def push(player_indices: list[int], amount: int) -> None:
                player_indices.sort()

                for j, k in enumerate(player_indices):
                    assert self.statuses[k]

                    sub_amount = amount // len(player_indices)

                    if not j:
                        sub_amount += amount % len(player_indices)

                    self.bets[k] += sub_amount

            hand_type_indices = []

            for i in self.hand_type_indices:
                for hand in self.get_up_hands(i):
                    if hand is not None:
                        hand_type_indices.append(i)
                        break

            hand_type_count = len(hand_type_indices)

            for pot in self.pots:
                for i in hand_type_indices:
                    hands = tuple(self.get_up_hands(i))
                    max_hand = max_or_none(
                        map(partial(getitem, hands), pot.player_indices),
                    )
                    player_indices = [
                        j for j in pot.player_indices if hands[j] == max_hand
                    ]
                    amount = pot.amount // hand_type_count

                    if not i:
                        amount += pot.amount % hand_type_count

                    push(player_indices, amount)

        self._end_chips_pushing()

        return self.ChipsPushing(tuple(self.bets))

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

        assert any(self.chips_pulling_statuses)

        if Automation.CHIPS_PULLING in self.automations:
            while any(self.chips_pulling_statuses):
                self.pull_chips()

    def _end_chips_pulling(self) -> None:
        for i in self.player_indices:
            self.chips_pulling_statuses[i] = False

        self._end()

    @dataclass
    class ChipsPulling:
        """The chips pulling."""

        player_index: int
        """The player index."""
        amount: int
        """The amount."""

    @property
    def chips_pulling_indices(self) -> Iterator[int]:
        """Iterate through players who can pull chips.

        :return: The chips pullers.
        """
        try:
            self._verify_chips_pulling()
        except ValueError:
            return None

        for i in self.player_indices:
            if self.chips_pulling_statuses[i]:
                yield i

    def _verify_chips_pulling(self) -> None:
        if not any(self.chips_pulling_statuses):
            raise ValueError('no one can pull chips')

    def verify_chips_pulling(self, player_index: int | None = None) -> int:
        """Verify the chips pulling.

        :param player_index: The optional player index.
        :return: The chips pulling index.
        :raises ValueError: If the chips pulling cannot be done.
        """
        self._verify_chips_pulling()

        if player_index is None:
            player_index = next(self.chips_pulling_indices)

        if not self.chips_pulling_statuses[player_index]:
            raise ValueError('no chip to be pulled')

        return player_index

    def can_pull_chips(self, player_index: int | None = None) -> bool:
        """Return whether the chips pulling can be done.

        :param player_index: The optional player index.
        :return: ``True`` if the chips pulling can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chips_pulling(player_index)
        except ValueError:
            return False

        return True

    def pull_chips(self, player_index: int | None = None) -> ChipsPulling:
        """Pull chips..

        :param player_index: The optional player index.
        :return: The chips pulling.
        :raises ValueError: If the chips pulling cannot be done.
        """
        player_index = self.verify_chips_pulling(player_index)
        amount = self.bets[player_index]

        self.stacks[player_index] += amount
        self.bets[player_index] = 0
        self.chips_pulling_statuses[player_index] = False

        if not any(self.chips_pulling_statuses):
            self._end_chips_pulling()

        return self.ChipsPulling(player_index, amount)
