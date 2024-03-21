""":mod:`pokerkit.state` implements classes related to poker states."""

from abc import ABC
from collections.abc import Callable, Iterable, Iterator
from collections import Counter, deque
from dataclasses import InitVar, dataclass, field, KW_ONLY
from enum import StrEnum, unique
from functools import partial
from itertools import chain, filterfalse, islice, starmap
from operator import getitem, sub
from random import shuffle
from typing import Any
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
                (
                    'negative maximum number of completions, bettings, or '
                    'raisings'
                ),
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
    """

    amount: int
    """The amount."""
    player_indices: tuple[int, ...]
    """The player indices of those who contributed."""

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError('negative pot amount')


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
    rake: int
    """The rake."""

    @property
    def total_amount(self) -> int:
        """Return the total amount.

        >>> chips_pushing = ChipsPushing((1, 2, 3), 0)
        >>> chips_pushing.total_amount
        6

        :return: The total amount.
        """
        return sum(self.amounts) + self.rake


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
    >>> state.push_chips()
    ChipsPushing(commentary=None, amounts=(0, 2), rake=0)
    >>> state.pull_chips(1)
    ChipsPulling(commentary=None, player_index=1, amount=3)

    The game has terminated.

    >>> state.status
    False

    >>> state = State(
    ...     (),
    ...     Deck.KUHN_POKER,
    ...     (KuhnPokerHand,),
    ...     (),
    ...     BettingStructure.FIXED_LIMIT,
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: empty streets
    >>> state = State(
    ...     (),
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
    ...     True,
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: first street not hole dealing
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
    ...     (-1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: negative antes, blinds, straddles, or bring-in
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
    ...     (0,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: no antes, blinds, straddles, or bring-in
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
    ...     (2, 0),
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: non-positive starting stacks
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
    ...     (0,) * 2,
    ...     (1,) * 2,
    ...     1,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: both bring-in and blinds or straddles specified
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
    ...     (0,) * 2,
    ...     (0,) * 2,
    ...     1,
    ...     (2,) * 2,
    ...     2,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: bring-in must be less than the min bet
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
    ...     (1,),
    ...     (0,),
    ...     0,
    ...     (2,),
    ...     1,
    ... )
    Traceback (most recent call last):
        ...
    ValueError: not enough players
    """

    __low_hand_opening_lookup = _LowHandOpeningLookup()
    __high_hand_opening_lookup = _HighHandOpeningLookup()
    automations: tuple[Automation, ...]
    """The automations."""
    deck: Deck
    """The deck."""
    hand_types: tuple[type[Hand], ...]
    """The hand types."""
    streets: tuple[Street, ...]
    """The streets."""
    betting_structure: BettingStructure
    """The betting structure."""
    ante_trimming_status: bool
    """The ante trimming status.

    Usually, if you want uniform antes, set this to ``True``.
    If you want non-uniform antes like big blind antes, set
    this to ``False``.
    """
    raw_antes: InitVar[ValuesLike]
    """The raw antes."""
    raw_blinds_or_straddles: InitVar[ValuesLike]
    """The raw blinds or straddles."""
    bring_in: int
    """The bring-in."""
    raw_starting_stacks: InitVar[ValuesLike]
    """The raw starting stacks."""
    player_count: int
    """The number of players."""
    divmod: Callable[[int, int], tuple[int, int]] = field(default=divmod)
    """The divmod function."""
    rake: Callable[[int], tuple[Any, int]] = field(
        default=partial(rake, rake=0),
    )
    """The rake function."""
    antes: tuple[int, ...] = field(init=False)
    """The antes."""
    blinds_or_straddles: tuple[int, ...] = field(init=False)
    """The blinds or straddles."""
    starting_stacks: tuple[int, ...] = field(init=False)
    """The starting stacks."""
    deck_cards: deque[Card] = field(default_factory=deque, init=False)
    """The deck cards."""
    board_cards: list[Card] = field(default_factory=list, init=False)
    """The board cards."""
    mucked_cards: list[Card] = field(default_factory=list, init=False)
    """The mucked cards."""
    burn_cards: list[Card] = field(default_factory=list, init=False)
    """The burn cards."""
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
    discarded_cards: list[list[Card]] = field(
        default_factory=list,
        init=False,
    )
    """The discards."""
    street_index: int | None = field(default=None, init=False)
    """The street index."""
    all_in_show_status: bool = field(default=False, init=False)
    """The all-in show status."""
    status: bool = field(default=True, init=False)
    """The game status."""
    operations: list[Operation] = field(default_factory=list, init=False)
    """The operations."""

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

        >>> state.push_chips()
        ChipsPushing(commentary=None, amounts=(6, 0), rake=0)
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

    def get_hand(self, player_index: int, hand_type_index: int) -> Hand | None:
        """Return the corresponding hand of the player.

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
        >>> state.get_hand(0, 0) is None
        True
        >>> state.get_hand(1, 0) is None
        True

        Pre-flop.

        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad), statuse...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ks, Qs), statuse...
        >>> state.get_hand(0, 0) is None
        True
        >>> state.get_hand(1, 0) is None
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
        >>> state.get_hand(0, 0)
        AcAdJsTs2c
        >>> str(state.get_hand(0, 0))
        'One pair (AcAdJsTs2c)'
        >>> str(state.get_hand(1, 0))
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
        >>> str(state.get_hand(0, 0))
        'Three of a kind (AcAdJsTsAh)'
        >>> str(state.get_hand(1, 0))
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
        >>> str(state.get_hand(0, 0))
        'Four of a kind (AcAdJsAhAs)'
        >>> str(state.get_hand(1, 0))
        'Straight flush (KsQsJsTsAs)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
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
        except (KeyError, ValueError):
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
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
        True

        Pre-flop.

        >>> state.deal_hole('AcAd')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, Ad), statuse...
        >>> state.deal_hole('KsQs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ks, Qs), statuse...
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
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
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
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
        >>> state.get_up_hand(0, 0) is None
        True
        >>> state.get_up_hand(1, 0) is None
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
        >>> str(state.get_up_hand(0, 0))
        'One pair (JsTs2cAhAs)'
        >>> str(state.get_up_hand(1, 0))
        'One pair (JsTs2cAhAs)'
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
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
        >>> state.get_up_hands(0)  # doctest: +ELLIPSIS
        <generator object State.get_up_hands at 0x...>
        >>> tuple(state.get_up_hands(0))
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
        >>> tuple(state.get_up_hands(0))
        (JsTs2cAhAs, JsTs2cAhAs)
        >>> state.check_or_call()
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
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

        self.mucked_cards.extend(self.hole_cards[player_index])

        self.statuses[player_index] = False

        self.hole_cards[player_index].clear()
        self.hole_card_statuses[player_index].clear()

    def _show_hole_cards(self, player_index: int) -> None:
        assert self.statuses[player_index]

        for i in range(len(self.hole_cards[player_index])):
            self.hole_card_statuses[player_index][i] = True

    @property
    def _backup_cards(self) -> tuple[Card, ...]:
        return tuple(
            filterfalse(
                Card.unknown_status.__get__,
                chain(
                    self.burn_cards,
                    self.mucked_cards,
                    chain.from_iterable(self.discarded_cards),
                ),
            ),
        )

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
            dealable_cards = self.get_dealable_cards(cards)

            if len(dealable_cards) < cards:
                raise ValueError('not enough cards in deck')

            cards = dealable_cards[:cards]
        else:
            cards = Card.clean(cards)
            dealable_cards = self.get_dealable_cards(len(cards))

            for card in cards:
                if card not in dealable_cards and not card.unknown_status:
                    warn(f'dealing {card} that is not recommended to be dealt')

        return cards

    def _consume_cards(self, cards: tuple[Card, ...]) -> None:
        if set(cards) > set(self.deck_cards):
            self._produce_cards(shuffled(self._backup_cards))

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

    def get_dealable_cards(
            self,
            deal_count: int | None = None,
    ) -> tuple[Card, ...]:
        """Iterate through the available cards that can be dealt or
        burned.

        :param deal_count: The number of dealt cards.
        :return: The recommended dealable cards, from deck and backup.
        """
        cards = tuple(self.deck_cards)

        if deal_count is None or deal_count > len(self.deck_cards):
            cards += tuple(shuffled(self._backup_cards))

        return cards

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

        operation = AntePosting(player_index, amount, commentary=commentary)

        self._update_ante_posting(operation)

        return operation

    # bet collection

    bet_collection_status: bool = field(default=False, init=False)
    """The bet collection status."""

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

        if sum(self.statuses) == 1:
            self._begin_chips_pushing()
        elif self.street is None:
            self._begin_blind_or_straddle_posting()
        elif self.street is self.streets[-1] or self.all_in_show_status:
            self._begin_showdown()
        else:
            self._begin_dealing()

    def verify_bet_collection(self) -> None:
        """Verify the bet collection.

        :return: ``None``.
        :raises ValueError: If the bet collection cannot be done.
        """
        if not self.bet_collection_status:
            raise ValueError('bet collection prohibited')

    def can_collect_bets(self) -> bool:
        """Return whether the bet collection can be done.

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

                    self.stacks[i] += self.bets[i] - bet_cutoff
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

        operation = BlindOrStraddlePosting(
            player_index,
            amount,
            commentary=commentary,
        )

        self._update_blind_or_straddle_posting(operation)

        return operation

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

        if (
                sum(map(len, self.hole_dealing_statuses))
                > len(self.get_dealable_cards())
        ):
            self.board_dealing_count += len(self.street.hole_dealing_statuses)

            for i in self.player_indices:
                self.hole_dealing_statuses[i].clear()

        assert (
            any(self.hole_dealing_statuses)
            or self.board_dealing_count
            or any(self.standing_pat_or_discarding_statuses)
        )

        self._update_dealing()

    def _update_dealing(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if (
                not self.card_burning_status
                and not any(self.hole_dealing_statuses)
                and not self.board_dealing_count
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
                        and self.board_dealing_count
                ):
                    self.deal_board()

    def _end_dealing(self) -> None:
        assert not self.card_burning_status
        assert not any(self.hole_dealing_statuses)
        assert not self.board_dealing_count
        assert not any(self.standing_pat_or_discarding_statuses)

        self._begin_betting()

    def verify_card_burning(
            self,
            card: Card | str | None = None,
    ) -> Card:
        """Verify the card burning.

        :param card: The optional card.
        :return: The burn card.
        :raises ValueError: If the card burning cannot be done.
        """
        cards = self._verify_cards_consumption(
            1 if card is None else card,
        )

        if not self.card_burning_status:
            raise ValueError('no pending burns')
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError('not all have stood pat or discarded')
        elif len(cards) != 1:
            raise ValueError('expected one card')

        card, = cards

        return card

    def can_burn_card(self, card: Card | str | None = None) -> bool:
        """Return whether the card burning can be done.

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
            card: Card | str | None = None,
            *,
            commentary: str | None = None,
    ) -> CardBurning:
        """Burn a card.

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
            or self.board_dealing_count
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
            raise ValueError('card must be burnt')
        elif not any(self.hole_dealing_statuses):
            raise ValueError('nobody can be dealt hole cards')
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError('not all have stood pat or discarded')

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

        cards = self._verify_cards_consumption(
            1 if cards is None else cards,
        )
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
        except (ValueError, UserWarning):
            return False

        return True

    def deal_hole(
            self,
            cards: CardsLike | int | None = None,
            *,
            commentary: str | None = None,
    ) -> HoleDealing:
        """Deal the hole.

        :param cards: The optional cards.
        :param commentary: The optional commentary.
        :return: The hole dealing.
        :raises ValueError: If the hole dealing cannot be done.
        """
        cards = self.verify_hole_dealing(cards)
        player_index = self.hole_dealee_index
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
        elif any(self.standing_pat_or_discarding_statuses):
            raise ValueError('not all have stood pat or discarded')

        cards = self._verify_cards_consumption(
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

        :param cards: The optional cards.
        :param commentary: The optional commentary.
        :return: The board dealing.
        :raises ValueError: If the board dealing cannot be done.
        """
        cards = self.verify_board_dealing(cards)

        assert self.board_dealing_count

        self._consume_cards(cards)

        self.board_dealing_count -= len(cards)
        self.board_cards.extend(cards)

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
            raise ValueError('no pending discards')

    def verify_standing_pat_or_discarding(
            self,
            cards: CardsLike = (),
    ) -> tuple[Card, ...]:
        """Verify the discard.

        :param cards: The discarded cards, defaults to empty.
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

    def can_stand_pat_or_discard(self, cards: CardsLike = ()) -> bool:
        """Return whether the discard can be done.

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
        """Discard hole cards.

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
                raise NotImplementedError

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
                self.all_in_show_status = True

        if not all(self.stacks) and self.street_index == len(self.streets) - 1:
            self.all_in_show_status = True

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

        :return: ``None``.
        :raises ValueError: If the checking or calling cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')

    def can_check_or_call(self) -> bool:
        """Return whether the checking or calling can be done.

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

        :param commentary: The optional commentary.
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
        except (ValueError, UserWarning):
            return False

        return True

    def post_bring_in(
            self,
            *,
            commentary: str | None = None,
    ) -> BringInPosting:
        """Post the bring-in.

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

        self.stacks[player_index] -= amount
        self.bets[player_index] += amount
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
                raise NotImplementedError

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
        ValueError: no more completion, betting, or raising permitted

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

        operation = CompletionBettingOrRaisingTo(
            player_index,
            amount,
            commentary=commentary,
        )

        self._update_betting(operation)

        return operation

    # showdown

    showdown_indices: deque[int] = field(default_factory=deque, init=False)
    """The showdown indices."""

    def _setup_showdown(self) -> None:
        pass

    def _begin_showdown(self) -> None:
        assert not self.showdown_indices

        self.showdown_indices = deque(self.player_indices)

        if self.opener_index is not None:
            self.showdown_indices.rotate(-self.opener_index)

        for i in self.player_indices:
            if not self.statuses[i] or all(self.hole_card_statuses[i]):
                self.showdown_indices.remove(i)

        self._update_showdown()

    def _update_showdown(self, operation: Operation | None = None) -> None:
        self._update(operation)

        if not self.showdown_indices:
            self._end_showdown()
        elif Automation.HOLE_CARDS_SHOWING_OR_MUCKING in self.automations:
            while self.showdown_indices:
                self.show_or_muck_hole_cards()

    def _end_showdown(self) -> None:
        assert not self.showdown_indices

        if self.all_in_show_status and self.street is not self.streets[-1]:
            self._begin_dealing()
        else:
            self._begin_hand_killing()

    @property
    def showdown_index(self) -> int | None:
        """Return the showdown index.

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

    def _pop_showdown_index(self) -> int:
        return self.showdown_indices.popleft()

    def _verify_hole_cards_showing_or_mucking(self) -> None:
        if not self.showdown_indices:
            raise ValueError('no player to act')

    def verify_hole_cards_showing_or_mucking(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
    ) -> tuple[bool, tuple[Card, ...] | None]:
        """Verify the hole card showing or mucking.

        :param status_or_hole_cards: The optional status or hole cards.
        :return: The status.
        :raises ValueError: If hole card showing or mucking cannot be
                            done.
        """
        self._verify_hole_cards_showing_or_mucking()

        player_index = self.showdown_index

        assert player_index is not None

        if isinstance(status_or_hole_cards, bool):
            status = status_or_hole_cards
            hole_cards = None
        elif status_or_hole_cards is None:
            status = self.all_in_show_status or self.can_win_now(player_index)
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

        if not status and self.all_in_show_status:
            raise ValueError('must show hole cards in all-in pots')

        if hole_cards is None and status:
            hole_cards = tuple(self.hole_cards[player_index])

        if hole_cards is not None and status:
            for card in hole_cards:
                if card.unknown_status:
                    raise ValueError('unknown card shown')

        return status, hole_cards

    def can_show_or_muck_hole_cards(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
    ) -> bool:
        """Return whether the hole card showing or mucking can be done.

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
        :return: ``True`` if the hole crad showing or mucking can be
                 done, otherwise ``False``.
        """
        try:
            self.verify_hole_cards_showing_or_mucking(status_or_hole_cards)
        except (ValueError, UserWarning):
            return False

        return True

    def show_or_muck_hole_cards(
            self,
            status_or_hole_cards: bool | CardsLike | None = None,
            *,
            commentary: str | None = None,
    ) -> HoleCardsShowingOrMucking:
        """Show or muck hole cards.

        If the status is not given, the hole cards will be shown if and
        only if there is chance of winning the pot. Otherwise, the hand
        will be mucked.

        :param status_or_hole_cards: The optional status or hole cards.
        :param commentary: The optional commentary.
        :return: The hole cards showing or mucking.
        """
        status, hole_cards = self.verify_hole_cards_showing_or_mucking(
            status_or_hole_cards,
        )
        player_index = self._pop_showdown_index()

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
            raise ValueError('nobody can kill their hand')

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
            raise ValueError('player cannot kill their hand')

        return player_index

    def can_kill_hand(self, player_index: int | None = None) -> bool:
        """Return whether the hand killing can be done.

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

    def _setup_chips_pushing(self) -> None:
        pass

    def _begin_chips_pushing(self) -> None:
        assert self._pots is None

        self.street_index = None
        self._pots = list(self.pots)

        self._update_chips_pushing()

    def _update_chips_pushing(
            self,
            operation: Operation | None = None,
    ) -> None:
        self._update(operation)

        if not self._pots:
            self._end_chips_pushing()
        elif Automation.CHIPS_PUSHING in self.automations:
            while self._pots:
                self.push_chips()

    def _end_chips_pushing(self) -> None:
        assert not self._pots

        self._begin_chips_pulling()

    @property
    def pot_amounts(self) -> Iterator[int]:
        """Return the list of main and side pot amounts (if any).

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
        >>> state.complete_bet_or_raise_to(1000)
        Traceback (most recent call last):
            ...
        ValueError: irrelevant completion, betting, or raising
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
        >>> next(state.pot_amounts)
        Traceback (most recent call last):
            ...
        StopIteration
        >>> tuple(state.pot_amounts)
        ()

        :return: The list of main and side pots (if any).
        """
        for pot in self.pots:
            yield pot.amount

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

        >>> state.push_chips()
        ChipsPushing(commentary=None, amounts=(66, 0), rake=0)
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
        >>> state.complete_bet_or_raise_to(1000)
        Traceback (most recent call last):
            ...
        ValueError: irrelevant completion, betting, or raising
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

        Flop.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(..., ..., ...))

        Turn.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))

        River.

        >>> state.deal_board()  # doctest: +ELLIPSIS
        BoardDealing(commentary=None, cards=(...,))
        >>> next(state.pots)
        Traceback (most recent call last):
            ...
        StopIteration
        >>> tuple(state.pots)
        ()

        :return: The list of main and side pots (if any).
        """
        if self._pots is not None:
            yield from self._pots

            return
        elif sum(self.stacks) + sum(self.bets) == sum(self.starting_stacks):
            return

        contributions = list(self.starting_stacks)
        pending_contributions = list(self.starting_stacks)
        amount = 0

        for i in self.player_indices:
            assert self.stacks[i] <= self.starting_stacks[i]

            contributions[i] -= self.bets[i] + self.stacks[i]
            pending_contributions[i] -= self.stacks[i]

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
                pots.append(Pot(amount, tuple(player_indices)))

            amount = 0
            previous_contribution = contribution

        yield from pots

    def verify_chips_pushing(self) -> None:
        """Verify the chips pushing.

        :return: ``None``.
        :raises ValueError: If the chips pushing cannot be done.
        """
        if not self._pots:
            raise ValueError('chips push not allowed')

    def can_push_chips(self) -> bool:
        """Return whether the chips pushing can be done.

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

        :param commentary: The optional commentary.
        :return: The chips pushing.
        :raises ValueError: If the chips pushing cannot be done.
        """
        self.verify_chips_pushing()

        assert self._pots is not None and self._pots

        pot = self._pots.pop()
        raked_amount, pushed_amount = self.rake(pot.amount)
        bets = self.bets.copy()

        if sum(self.statuses) == 1:
            assert len(pot.player_indices) == 1

            self.bets[pot.player_indices[0]] += pushed_amount
        else:

            def push(player_indices: list[int], amount: int) -> None:
                player_indices.sort()

                for j, k in enumerate(player_indices):
                    assert self.statuses[k]

                    quotient, remainder = self.divmod(
                        amount,
                        len(player_indices),
                    )
                    sub_amount = quotient

                    if not j:
                        sub_amount += remainder

                    self.bets[k] += sub_amount

            hand_type_indices = []

            for i in self.hand_type_indices:
                for hand in self.get_up_hands(i):
                    if hand is not None:
                        hand_type_indices.append(i)

                        break

            hand_type_count = len(hand_type_indices)

            for i in hand_type_indices:
                hands = tuple(self.get_up_hands(i))
                max_hand = max_or_none(
                    map(partial(getitem, hands), pot.player_indices),
                )
                player_indices = [
                    j for j in pot.player_indices if hands[j] == max_hand
                ]
                quotient, remainder = self.divmod(
                    pushed_amount,
                    hand_type_count,
                )
                amount = quotient

                if not i:
                    amount += remainder

                push(player_indices, amount)

        operation = ChipsPushing(
            tuple(starmap(sub, zip(self.bets, bets))),
            raked_amount,
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

        :param player_index: The optional player index.
        :param commentary: The optional commentary.
        :return: The chips pulling.
        :raises ValueError: If the chips pulling cannot be done.
        """
        player_index = self.verify_chips_pulling(player_index)
        amount = self.bets[player_index]

        self.stacks[player_index] += amount
        self.bets[player_index] = 0
        self.chips_pulling_statuses[player_index] = False

        operation = ChipsPulling(player_index, amount, commentary=commentary)

        self._update_chips_pulling(operation)

        return operation

    def verify_no_operation(self) -> None:
        """Verify the no-operation.

        :return: ``None``.
        """
        pass

    def can_no_operate(self) -> bool:
        """Return whether the no-operation can be done. Always ``True``.

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
