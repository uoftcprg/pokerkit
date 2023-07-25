""":mod:`pokerkit.state` implements classes related to poker states."""

from collections import Counter, deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, auto, unique
from functools import partial
from itertools import chain, islice
from operator import getitem

from pokerkit.hands import Hand
from pokerkit.lookups import Label, Lookup
from pokerkit.utilities import Card, RankOrder, Suit, max_or_none, min_or_none


@unique
class BettingStructure(Enum):
    """The enum class for betting structures.

    >>> BettingStructure.FIXED_LIMIT  # doctest: +ELLIPSIS
    <BettingStructure.FIXED_LIMIT: ...>
    >>> BettingStructure.NO_LIMIT  # doctest: +ELLIPSIS
    <BettingStructure.NO_LIMIT: ...>
    """

    FIXED_LIMIT = auto()
    """The fixed-limit."""
    POT_LIMIT = auto()
    """The pot-limit."""
    NO_LIMIT = auto()
    """The no-limit."""


@unique
class Opening(Enum):
    """The enum class for openings.

    >>> Opening.POSITION  # doctest: +ELLIPSIS
    <Opening.POSITION: ...>
    >>> Opening.LOW_HAND  # doctest: +ELLIPSIS
    <Opening.LOW_HAND: ...>
    """

    POSITION = auto()
    """The opener is decided by position.

    If blinds or straddles are present, they are taken account of.
    """
    LOW_CARD = auto()
    """The opener is decided by having the lowest exposed card."""
    HIGH_CARD = auto()
    """The opener is decided by having the highest exposed card."""
    LOW_HAND = auto()
    """The opener is decided by having the lowest exposed hand, then
    position.
    """
    HIGH_HAND = auto()
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
    >>> street.burn_status
    False
    >>> street.hole_deal_statuses
    (False, False)
    """

    burn_status: bool
    """Whether to burn card."""
    hole_deal_statuses: tuple[bool, ...]
    """The statuses of dealt hole cards."""
    board_deal_count: int
    """The number of dealt board cards."""
    discard_and_draw_status: bool
    """Whether to discard and draw prior to betting."""
    opening: Opening
    """The opening."""
    min_completion_bet_or_raise_amount: int
    """The minimum completion, bet, or raise amount."""
    max_completion_bet_or_raise_count: int | None
    """The maximum number of completions, bets, or raises."""

    def __post_init__(self) -> None:
        if self.board_deal_count < 0:
            raise ValueError('negative number of dealt cards')
        elif (
                not self.hole_deal_statuses
                and not self.board_deal_count
                and not self.discard_and_draw_status
        ):
            raise ValueError('no dealing')
        elif self.hole_deal_statuses and self.discard_and_draw_status:
            raise ValueError('dealing hole and discarding')
        elif self.min_completion_bet_or_raise_amount <= 0:
            raise ValueError(
                'non-positive minimum completion, bet, or raise amount',
            )
        elif (
                self.max_completion_bet_or_raise_count is not None
                and self.max_completion_bet_or_raise_count < 0
        ):
            raise ValueError(
                'negative maximum number of completions, bets, or raises',
            )


@dataclass(frozen=True)
class Pot:
    """The class for pots.

    >>> pot = Pot(100, (1, 3))
    >>> pot.amount
    100
    >>> pot.player_indices
    (1, 3)
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

    >>> from pokerkit import BadugiHand
    >>> state = State(
    ...     (BadugiHand,),
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
    ...     (1,) * 2,
    ...     (0,) * 2,
    ...     0,
    ...     (2,) * 2,
    ...     deque(Card.parse('JsQsKs')),
    ... )
    >>> state.stacks
    [2, 2]
    >>> state.bets
    [0, 0]
    >>> state.post_ante(0)
    (0, 1)
    >>> state.post_ante(1)
    (1, 1)
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [1, 1]
    >>> state.collect_bets()
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.hole_cards
    [[], []]
    >>> state.deal_hole()
    (0, (Js,))
    >>> state.hole_cards
    [[Js], []]
    >>> state.deal_hole()
    (1, (Qs,))
    >>> state.hole_cards
    [[Js], [Qs]]
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.check_or_call()
    (0, 0)
    >>> state.stacks
    [1, 1]
    >>> state.bets
    [0, 0]
    >>> state.complete_bet_or_raise_to()
    (1, 1)
    >>> state.stacks
    [1, 0]
    >>> state.bets
    [0, 1]
    >>> state.fold()
    0
    >>> state.collect_bets()
    >>> state.push_chips()
    >>> state.stacks
    [1, 0]
    >>> state.bets
    [0, 3]
    >>> state.total_pot_amount
    3
    >>> state.pull_chips(1)
    1
    >>> state.stacks
    [1, 3]
    >>> state.bets
    [0, 0]
    >>> state.total_pot_amount
    0
    """

    __low_hand_opening_lookup = _LowHandOpeningLookup()
    __high_hand_opening_lookup = _HighHandOpeningLookup()
    hand_types: tuple[type[Hand], ...]
    """The hand types."""
    streets: tuple[Street, ...]
    """The streets."""
    betting_structure: BettingStructure
    """The betting structure."""
    antes: tuple[int, ...]
    """The antes."""
    blinds_or_straddles: tuple[int, ...]
    """The blinds or straddles."""
    bring_in: int
    """The bring-in."""
    starting_stacks: tuple[int, ...]
    """The starting stacks."""
    deck: deque[Card]
    """The deck."""
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
    board_cards: list[Card] = field(default_factory=list, init=False)
    """The board cards."""
    mucked_cards: list[Card] = field(default_factory=list, init=False)
    """The mucked cards."""
    burned_cards: list[Card] = field(default_factory=list, init=False)
    """The burned cards."""
    street_index: int | None = field(default=None, init=False)
    """The street index."""
    status: bool = field(default=True, init=False)
    """The game status."""

    def __post_init__(self) -> None:
        if not self.streets:
            raise ValueError('empty streets')
        elif not self.streets[0].hole_deal_statuses:
            raise ValueError('first street not hole dealing')
        elif (
                min(self.antes) < 0
                or min(self.blinds_or_straddles) < 0
                or self.bring_in < 0
        ):
            raise ValueError('negative antes, blinds, straddles, or bring-in')
        elif min(self.starting_stacks) <= 0:
            raise ValueError('non-positive starting stacks')
        elif (
                not any(self.antes)
                and not any(self.blinds_or_straddles)
                and not self.bring_in
        ):
            raise ValueError('no antes, blinds, straddles, or bring-in')
        elif any(self.blinds_or_straddles) and self.bring_in:
            raise ValueError('both bring-in and blinds or straddles specified')
        elif (
                self.bring_in
                >= self.streets[0].min_completion_bet_or_raise_amount
        ):
            raise ValueError('bring-in must be less than the min bet amount')
        elif not (
                len(self.antes)
                == len(self.blinds_or_straddles)
                == len(self.starting_stacks)
        ):
            raise ValueError('inconsistent number of players')
        elif len(set(self.deck)) != len(self.deck):
            raise ValueError('duplicate cards in deck')
        elif self.player_count < 2:
            raise ValueError('not enough players')

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
        self._setup_chip_pulling()
        self._begin_ante_posting()

    @property
    def hand_type_count(self) -> int:
        """Return the number of hand types.

        :return: The number of hand types.
        """
        return len(self.hand_types)

    @property
    def hand_type_indices(self) -> range:
        """Return the hand type indices.

        :return: The hand type indices.
        """
        return range(self.hand_type_count)

    @property
    def discard_and_draw_statuses(self) -> Iterator[bool]:
        """Return the discard and draw statuses.

        :return: The discard and draw statuses.
        """
        for street in self.streets:
            yield street.discard_and_draw_status

    @property
    def openings(self) -> Iterator[Opening]:
        """Return the openings.

        :return: The openings.
        """
        for street in self.streets:
            yield street.opening

    @property
    def player_count(self) -> int:
        """Return the number of players.

        :return: The number of players.
        """
        return len(self.starting_stacks)

    @property
    def player_indices(self) -> range:
        """Return the player indices.

        :return: The player indices.
        """
        return range(self.player_count)

    @property
    def street(self) -> Street | None:
        """Return the current street.

        ``None`` is returned if the state is terminal or in showdown.

        :return: The street if applicable, otherwise ``None``.
        """
        if self.street_index is None:
            return None

        return self.streets[self.street_index]

    @property
    def total_pot_amount(self) -> int:
        """Return the total pot amount.

        :return: The total pot amount.
        """
        amount = sum(self.bets)

        for pot in self.pots:
            amount += pot.amount

        return amount

    @property
    def pots(self) -> Iterator[Pot]:
        """Return the list of main and side pots (if any).

        The first pot is the main pot of this game. The subsequent pots
        are side pots.

        There is always a main pot even if its amount is ``0``.

        :return: The list of main and side pots (if any).
        """
        if sum(self.stacks) + sum(self.bets) == sum(self.starting_stacks):
            return

        total_ante = 0
        contributions = list(self.starting_stacks)
        pending_contributions = list(self.starting_stacks)

        for i in self.player_indices:
            assert self.stacks[i] <= self.starting_stacks[i]

            ante = min(self.antes[i], self.starting_stacks[i])
            total_ante += ante
            contributions[i] -= ante + self.bets[i] + self.stacks[i]
            pending_contributions[i] -= ante + self.stacks[i]

        previous_contribution = 0
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

        :param player_index: The player index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player if applicable,
                 otherwise ``None``.
        """
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

        :param player_index: The player index.
        :param hand_type_index: The hand type index.
        :return: The corresponding hand of the player.
        """
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

        :param hand_type_index: The hand type index.
        :return: The optional corresponding hands from up cards.
        """
        for i in self.player_indices:
            yield self.get_up_hand(i, hand_type_index)

    def can_win(self, player_index: int) -> bool:
        """Return whether if the player can win pots based on showdowns
        so far.

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

    # Ante posting

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

    def _end_ante_posting(self) -> None:
        assert not any(self.ante_posting_statuses)

        self._begin_bet_collection()

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

    def post_ante(self, player_index: int | None = None) -> tuple[int, int]:
        """Post the ante.

        :param player_index: The optional player index.
        :return: A tuple containing the anteing player index and the
                 effective ante amount.
        :raises ValueError: If the ante posting cannot be done.
        """
        player_index = self.verify_ante_posting(player_index)
        effective_ante = self.get_effective_ante(player_index)

        assert self.ante_posting_statuses[player_index]
        assert not self.bets[player_index]
        assert 0 < effective_ante <= self.stacks[player_index]

        self.ante_posting_statuses[player_index] = False
        self.bets[player_index] = effective_ante
        self.stacks[player_index] -= effective_ante

        if not any(self.ante_posting_statuses):
            self._end_ante_posting()

        return player_index, effective_ante

    # Bet collection

    bet_collection_status: bool = field(default=False, init=False)
    """The bet collection status."""

    def _setup_bet_collection(self) -> None:
        assert not self.bet_collection_status

    def _begin_bet_collection(self) -> None:
        assert not self.bet_collection_status

        self.bet_collection_status = any(self.bets)

        if not self.bet_collection_status:
            self._end_bet_collection()

    def _end_bet_collection(self) -> None:
        assert not self.bet_collection_status

        if sum(self.statuses) == 1:
            self._begin_chip_pushing()
        elif self.street is None:
            self._begin_blind_or_straddle_posting()
        elif self.street is self.streets[-1]:
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

        :return: ``True`` if the bet collection can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_bet_collection()
        except ValueError:
            return False

        return True

    def collect_bets(self) -> None:
        """Collect the bets of the players.

        :return: ``None``.
        :raises ValueError: If the bet collection cannot be done.
        """
        self.verify_bet_collection()

        assert self.bet_collection_status
        assert any(self.bets)

        self.bet_collection_status = False
        player_indices = list(self.player_indices)

        if sum(self.statuses) == 1:
            player_indices.remove(self.statuses.index(True))

        if self.street is not None:
            bet_cutoff = sorted(self.bets)[-2]

            for i in player_indices:
                if self.bets[i] > bet_cutoff:
                    assert self.statuses[i]

                    self.stacks[i] += self.bets[i] - bet_cutoff

        for i in player_indices:
            self.bets[i] = 0

        self._end_bet_collection()

    # Blind or straddle posting

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
    ) -> tuple[int, int]:
        """Post the blind or straddle of the player.

        :param player_index: The optional player index.
        :return: A tuple containing the blinding or straddling player
                 index and the effective blind or straddle amount.
        :raises ValueError: If the blind or straddle posting cannot be
                            done.
        """
        player_index = self.verify_blind_or_straddle_posting(player_index)
        effective_blind_or_straddle = self.get_effective_blind_or_straddle(
            player_index,
        )

        assert self.blind_or_straddle_posting_statuses[player_index]
        assert not self.bets[player_index]
        assert 0 < effective_blind_or_straddle <= self.stacks[player_index]

        self.blind_or_straddle_posting_statuses[player_index] = False
        self.bets[player_index] = effective_blind_or_straddle
        self.stacks[player_index] -= effective_blind_or_straddle

        if not any(self.blind_or_straddle_posting_statuses):
            self._end_blind_or_straddle_posting()

        return player_index, effective_blind_or_straddle

    # Dealing

    burn_status: bool = field(default=False, init=False)
    """The card burn status."""
    hole_deal_statuses: list[deque[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The statuses of the cards to be dealt to holes."""
    board_deal_count: int = field(default=0, init=False)
    """The number of cards to be dealt to the board."""
    discard_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The statuses of the discards."""

    def _setup_dealing(self) -> None:
        assert not self.hole_deal_statuses
        assert not self.discard_statuses

        for _ in range(self.player_count):
            self.hole_deal_statuses.append(deque())
            self.discard_statuses.append(False)

    def _begin_dealing(self) -> None:
        assert not self.burn_status
        assert not any(self.hole_deal_statuses)
        assert not self.board_deal_count
        assert not any(self.discard_statuses)

        if self.street_index is None:
            self.street_index = 0
        else:
            self.street_index += 1

        assert 0 <= self.street_index < len(self.streets)
        assert self.street is not None

        self.burn_status = self.street.burn_status
        self.board_deal_count = self.street.board_deal_count

        for i in self.player_indices:
            if self.statuses[i]:
                self.hole_deal_statuses[i].extend(
                    self.street.hole_deal_statuses,
                )
                self.discard_statuses[i] = (
                    self.street.discard_and_draw_status
                )

        assert (
            any(self.hole_deal_statuses)
            or self.board_deal_count
            or any(self.discard_statuses)
        )

    def _end_dealing(self) -> None:
        assert not self.burn_status
        assert not any(self.hole_deal_statuses)
        assert not self.board_deal_count
        assert not any(self.discard_statuses)

        self._begin_betting()

    def _make_available(self, cards: tuple[Card, ...]) -> None:
        assert len(self.deck) >= len(cards)

        for card in cards:
            assert card in self.burned_cards or card in self.deck

            if card in self.burned_cards:
                self.burned_cards[self.burned_cards.index(card)] = (
                    self.deck.popleft()
                )
            else:
                self.deck.remove(card)

    @property
    def available_cards(self) -> Iterator[Card]:
        """Iterate through the available cards that can be dealt or
        burned.

        :return: The available cards.
        """
        if (
                self.burn_status
                or any(self.hole_deal_statuses)
                or self.board_deal_count
        ):
            yield from chain(self.burned_cards, self.deck)

    def verify_card_availabilities(
            self,
            cards: tuple[Card, ...] | Card | int,
    ) -> tuple[Card, ...]:
        """Verify the card availability.

        :param card: The optional card.
        :return: The available cards.
        :raises ValueError: If the card is unavailable.
        """
        if isinstance(cards, int):
            card_count = cards
        elif isinstance(cards, Card):
            card_count = 1
        else:
            card_count = len(cards)

        if len(self.deck) < card_count:
            raise ValueError('too many cards')

        if isinstance(cards, int):
            cards = tuple(self.deck)[:cards]
        elif isinstance(cards, Card):
            cards = (cards,)

        for card in cards:
            if card not in tuple(self.available_cards):
                raise ValueError('unavailable card')

        return cards

    def verify_card_burning(self, card: Card | None = None) -> Card:
        """Verify the card burning.

        :param card: The optional card.
        :return: The burned card.
        :raises ValueError: If the card burning cannot be done.
        """
        card, = self.verify_card_availabilities(1 if card is None else (card,))

        if not self.burn_status:
            raise ValueError('no pending burns')

        return card

    def can_burn_card(self, card: Card | None = None) -> bool:
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

    def burn_card(self, card: Card | None = None) -> Card:
        """Burn a card.

        :param card: The optional card.
        :return: The burned card.
        :raises ValueError: If the card burning cannot be done.
        """
        card = self.verify_card_burning(card)

        assert self.burn_status
        assert self.street is not None
        assert (
            any(self.hole_deal_statuses)
            or self.board_deal_count
            or self.street.discard_and_draw_status
        )
        assert not any(self.discard_statuses)

        self._make_available((card,))

        self.burn_status = False
        self.burned_cards.append(card)

        if not any(self.hole_deal_statuses) and not self.board_deal_count:
            self._end_dealing()

        return card

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
        assert (
            self.street.hole_deal_statuses
            or self.street.discard_and_draw_status
        )

        if self.street.hole_deal_statuses:
            return max(
                self.player_indices,
                key=lambda i: (len(self.hole_deal_statuses[i]), -i),
            )
        else:
            return next(
                filter(
                    partial(getitem, self.hole_deal_statuses),
                    self.player_indices,
                ),
            )

    def _verify_hole_dealing(self) -> None:
        if self.burn_status:
            raise ValueError('card must be burnt')
        elif not any(self.hole_deal_statuses):
            raise ValueError('nobody can be dealt hole cards')

    def verify_hole_dealing(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
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

        if not 0 < len(cards) <= len(self.hole_deal_statuses[player_index]):
            raise ValueError('invalid number of cards')

        return cards

    def can_deal_hole(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
    ) -> bool:
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

    def deal_hole(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
    ) -> tuple[int, tuple[Card, ...]]:
        """Deal the hole.

        :param cards: The optional cards.
        :return: A tuple containing the hole dealee index and the dealt
                 hole cards.
        :raises ValueError: If the hole dealing cannot be done.
        """
        cards = self.verify_hole_dealing(cards)
        player_index = self.hole_dealee_index

        assert player_index is not None
        assert self.hole_deal_statuses[player_index]

        self._make_available(cards)

        for card in cards:
            status = self.hole_deal_statuses[player_index].popleft()

            self.hole_cards[player_index].append(card)
            self.hole_card_statuses[player_index].append(status)

        if not any(self.hole_deal_statuses) and not self.board_deal_count:
            self._end_dealing()

        return player_index, cards

    def verify_board_dealing(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
    ) -> tuple[Card, ...]:
        """Verify the board dealing.

        :param cards: The optional cards.
        :return: The dealt board cards.
        :raises ValueError: If the board dealing cannot be done.
        """
        if self.burn_status:
            raise ValueError('card must be burnt')
        elif not self.board_deal_count:
            raise ValueError('no pending board dealing')

        cards = self.verify_card_availabilities(
            self.board_deal_count if cards is None else cards,
        )

        if not 0 < len(cards) <= self.board_deal_count:
            raise ValueError('invalid number of cards')

        return cards

    def can_deal_board(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
    ) -> bool:
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

    def deal_board(
            self,
            cards: tuple[Card, ...] | Card | int | None = None,
    ) -> tuple[Card, ...]:
        """Deal the board.

        :param cards: The optional cards.
        :return: The dealt board cards.
        :raises ValueError: If the board dealing cannot be done.
        """
        cards = self.verify_board_dealing(cards)

        assert self.board_deal_count

        self._make_available(cards)

        self.board_deal_count -= len(cards)
        self.board_cards.extend(cards)

        if (
                not any(self.hole_deal_statuses)
                and not self.board_deal_count
                and not any(self.discard_statuses)
        ):
            self._end_dealing()

        return cards

    @property
    def discarder_index(self) -> int | None:
        """Return the discarder index.

        :return: The discarder index if applicable, otherwise ``None``.
        """
        try:
            self._verify_discard()
        except ValueError:
            return None

        return self.discard_statuses.index(True)

    def _verify_discard(self) -> None:
        if not any(self.discard_statuses):
            raise ValueError('no pending discards')

    def verify_discard(
            self,
            discarded_cards: tuple[Card, ...] | None = None,
    ) -> tuple[Card, ...]:
        """Verify the discard.

        :param discarded_cards: The optional discarded cards.
        :return: The discarded cards.
        :raises ValueError: If the discard cannot be done.
        """
        self._verify_discard()

        if discarded_cards is None:
            discarded_cards = ()

        player_index = self.discarder_index

        assert player_index is not None

        if not set(discarded_cards) <= set(self.hole_cards[player_index]):
            raise ValueError('discarded cards not a subset of hole cards')

        return discarded_cards

    def can_discard(
            self,
            discarded_cards: tuple[Card, ...] | None = None,
    ) -> bool:
        """Return whether the discard can be done.

        :param discarded_cards: The optional discarded cards.
        :return: ``True`` if the discard can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_discard(discarded_cards)
        except ValueError:
            return False

        return True

    def discard(
            self,
            discarded_cards: tuple[Card, ...] | None = None,
    ) -> tuple[int, tuple[Card, ...]]:
        """Discard hole cards.

        :param discarded_cards: The optional discarded cards.
        :return: A tuple containing the discarder index and the
                 discarded cards.
        :raises ValueError: If the discard cannot be done.
        """
        discarded_cards = self.verify_discard(discarded_cards)
        player_index = self.discarder_index

        assert player_index is not None
        assert self.discard_statuses[player_index]

        self.discard_statuses[player_index] = False

        for discarded_card in discarded_cards:
            index = self.hole_cards[player_index].index(discarded_card)

            self.hole_deal_statuses[player_index].append(
                self.hole_card_statuses[player_index][index],
            )
            self.hole_cards[player_index].pop(index)
            self.hole_card_statuses[player_index].pop(index)

        if (
                not self.burn_status
                and not any(self.hole_deal_statuses)
                and not self.board_deal_count
                and not any(self.discard_statuses)
        ):
            self._end_dealing()

        return player_index, discarded_cards

    # Betting

    opener_index: int | None = field(default=None, init=False)
    """The opener index."""
    bring_in_status: bool = field(default=False, init=False)
    """The bring-in status."""
    completion_status: bool = field(default=False, init=False)
    """The completion status."""
    actor_indices: deque[int] = field(default_factory=deque, init=False)
    """The actor indices."""
    completion_bet_or_raise_amount: int = field(default=0, init=False)
    """The last completion, bet, or raise amount."""
    completion_bet_or_raise_count: int = field(default=0, init=False)
    """The number of completions, bets, or raises."""

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
            if not self.statuses[i] or not self.stacks[i]:
                self.actor_indices.remove(i)

        self.completion_bet_or_raise_amount = 0
        self.completion_bet_or_raise_count = 0

        if len(self.actor_indices) <= 1:
            self._end_betting()

    def _end_betting(self) -> None:
        show = False

        assert self.street_index is not None

        if (
                sum(self.statuses) > 1
                and not any(
                    islice(
                        self.discard_and_draw_statuses,
                        self.street_index + 1,
                        None,
                    ),
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

        # assert self.stacks[self.actor_indices[0]]  # TODO

        return self.actor_indices[0]

    def verify_fold(self) -> None:
        """Verify the fold.

        :return: ``None``.
        :raises ValueError: If the fold cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')

        actor_index = self.actor_index

        assert actor_index is not None

        if self.bets[actor_index] >= max(self.bets):
            raise ValueError('redundant fold')

    def can_fold(self) -> bool:
        """Return whether the fold can be done.

        :return: ``True`` if the fold can be done, otherwise ``False``.
        """
        try:
            self.verify_fold()
        except ValueError:
            return False

        return True

    def fold(self) -> int:
        """Fold.

        :return: The actor index.
        :raises ValueError: If the fold cannot be done.
        """
        self.verify_fold()

        actor_index = self._pop_actor_index()

        assert self.stacks[actor_index]

        self._muck_hole_cards(actor_index)

        assert any(self.statuses)

        if not self.actor_indices or sum(self.statuses) <= 1:
            self._end_betting()

        return actor_index

    @property
    def check_or_call_amount(self) -> int | None:
        """Return the check or call amount.

        :return: The check or call amount if applicable, otherwise ``None``.
        """
        try:
            self.verify_check_or_call()
        except ValueError:
            return None

        assert self.actor_index is not None

        return min(
            self.stacks[self.actor_index],
            max(self.bets) - self.bets[self.actor_index],
        )

    def verify_check_or_call(self) -> None:
        """Verify the check or call.

        :return: ``None``.
        :raises ValueError: If the check or call cannot be done.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')

    def can_check_or_call(self) -> bool:
        """Return whether the check or call can be done.

        :return: ``True`` if the check or call can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_check_or_call()
        except ValueError:
            return False

        return True

    def check_or_call(self) -> tuple[int, int]:
        """Check or call.

        :return: A tuple containing the actor index and the check or
                 call amount.
        :raises ValueError: If the check or call cannot be done.
        """
        self.verify_check_or_call()

        amount = self.check_or_call_amount
        actor_index = self._pop_actor_index()

        assert self.stacks[actor_index]
        assert amount is not None

        self.stacks[actor_index] -= amount
        self.bets[actor_index] += amount

        if not self.actor_indices:
            self._end_betting()

        return actor_index, amount

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

        assert self.actor_index is not None

        return min(self.stacks[self.actor_index], self.bring_in)

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

    def post_bring_in(self) -> tuple[int, int]:
        """Post the bring-in.

        :return: A tuple containing the poster index and the effective
                 bring-in amount.
        :raises ValueError: If the bring-in posting cannot be done.
        """
        self.verify_bring_in_posting()

        amount = self.effective_bring_in_amount
        actor_index = self._pop_actor_index()

        assert self.stacks[actor_index]
        assert amount is not None
        assert not any(self.bets)
        assert self.bring_in
        assert self.completion_status
        assert self.actor_indices

        self.stacks[actor_index] -= amount
        self.bets[actor_index] += amount
        self.bring_in_status = False

        return actor_index, amount

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
            effective_stacks[-2] - self.bets[player_index],
        )

    @property
    def min_completion_bet_or_raise_to_amount(self) -> int | None:
        """Return the minimum completion, bet, or raise to amount.

        :return: The minimum completion, bet, or raise to amount if
                 applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_bet_or_raise()
        except ValueError:
            return None

        assert self.street is not None

        amount = max(
            self.completion_bet_or_raise_amount,
            self.street.min_completion_bet_or_raise_amount,
        )

        if not self.completion_status:
            amount += max(self.bets)

        assert self.actor_index is not None

        return min(
            self.get_effective_stack(self.actor_index)
            + self.bets[self.actor_index],
            amount,
        )

    @property
    def pot_completion_bet_or_raise_to_amount(self) -> int | None:
        """Return the pot completion, bet, or raise to amount.

        :return: The pot completion, bet, or raise to amount if
                 applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_bet_or_raise()
        except ValueError:
            return None

        assert self.actor_index is not None
        assert self.min_completion_bet_or_raise_to_amount is not None

        return min(
            self.stacks[self.actor_index] + self.bets[self.actor_index],
            max(
                self.min_completion_bet_or_raise_to_amount,
                2 * max(self.bets) - self.bets[self.actor_index]
                + self.total_pot_amount,
            )
        )

    @property
    def max_completion_bet_or_raise_to_amount(self) -> int | None:
        """Return the maximum completion, bet, or raise to amount.

        :return: The maximum completion, bet, or raise to amount if
                 applicable, otherwise ``None``.
        """
        try:
            self._verify_completion_bet_or_raise()
        except ValueError:
            return None

        assert self.actor_index is not None

        match self.betting_structure:
            case BettingStructure.FIXED_LIMIT:
                amount = self.min_completion_bet_or_raise_to_amount
            case BettingStructure.POT_LIMIT:
                amount = self.pot_completion_bet_or_raise_to_amount
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

    def _verify_completion_bet_or_raise(self) -> None:
        if not self.actor_indices:
            raise ValueError('no player to act')

        assert self.street is not None

        if (
                self.completion_bet_or_raise_count
                == self.street.max_completion_bet_or_raise_count
        ):
            raise ValueError('no more completion, bet, or raise permitted')

        actor_index = self.actor_index

        assert actor_index is not None

        if self.stacks[actor_index] <= max(self.bets) - self.bets[actor_index]:
            raise ValueError('not enough chips in stack')

        for i in self.player_indices:
            if (
                    i != actor_index
                    and self.statuses[i]
                    and self.stacks[i] + self.bets[i] > max(self.bets)
            ):
                break
        else:
            raise ValueError('irrelevant completion, bet, or raise')

    def verify_completion_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> int:
        """Verify the completion, bet, or raise.

        :param amount: The optional completion, bet, or raise to amount.
        :return: The completion, bet, or raise to amount.
        :raises ValueError: If the completion, bet, or raise cannot be
                            done.
        """
        self._verify_completion_bet_or_raise()

        actor_index = self.actor_index

        assert actor_index is not None
        assert self.min_completion_bet_or_raise_to_amount is not None
        assert self.max_completion_bet_or_raise_to_amount is not None

        if amount is None:
            amount = self.min_completion_bet_or_raise_to_amount

        if amount < self.min_completion_bet_or_raise_to_amount:
            raise ValueError('below min completion, bet, or raise to amount')
        elif amount > self.max_completion_bet_or_raise_to_amount:
            raise ValueError('above max completion, bet, or raise to amount')

        return amount

    def can_complete_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> bool:
        """Return whether the completion, bet, or raise can be done.

        :param amount: The optional completion, bet, or raise to amount.
        :return: ``True`` if the completion, bet, or raise can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_completion_bet_or_raise_to(amount)
        except ValueError:
            return False

        return True

    def complete_bet_or_raise_to(
            self,
            amount: int | None = None,
    ) -> tuple[int, int]:
        """Complete, bet, or raise to an amount.

        :param amount: The optional completion, bet, or raise to amount.
        :return: A tuple containing the actor index and the completion,
                 bet, or raise to amount.
        :raises ValueError: If the completion, bet, or raise cannot be
                            done.
        """
        amount = self.verify_completion_bet_or_raise_to(amount)
        actor_index = self._pop_actor_index()

        completion_bet_or_raise_amount = amount - max(self.bets)
        self.stacks[actor_index] -= amount - self.bets[actor_index]
        self.bets[actor_index] = amount
        self.bring_in_status = False
        self.completion_status = False
        self.actor_indices = deque(self.player_indices)
        self.opener_index = actor_index
        self.completion_bet_or_raise_amount = max(
            self.completion_bet_or_raise_amount,
            completion_bet_or_raise_amount,
        )
        self.completion_bet_or_raise_count += 1

        self.actor_indices.rotate(-actor_index)
        self.actor_indices.popleft()

        for i in self.player_indices:
            if not self.statuses[i] or not self.stacks[i]:
                if i in self.actor_indices:
                    self.actor_indices.remove(i)

        assert self.actor_indices

        return actor_index, amount

    # Showdown

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

    def _end_showdown(self) -> None:
        assert not self.showdown_indices

        self._begin_hand_killing()

    @property
    def showdown_index(self) -> int | None:
        """Return the showdown index.

        :return: The showdown index if applicable, otherwise ``None``.
        """
        try:
            self._verify_hole_card_showing_or_mucking()
        except ValueError:
            return None

        return self.showdown_indices[0]

    def _pop_showdown_index(self) -> int:
        return self.showdown_indices.popleft()

    def _verify_hole_card_showing_or_mucking(self) -> None:
        if not self.showdown_indices:
            raise ValueError('no player to act')

    def verify_hole_card_showing_or_mucking(
            self,
            status: bool | None = None,
    ) -> bool:
        """Verify the hole card showing or mucking.

        :param status: The optional status.
        :return: The status.
        :raises ValueError: If hole card showing or mucking cannot be done.
        """
        self._verify_hole_card_showing_or_mucking()

        assert self.showdown_index is not None

        if status is None:
            status = self.can_win(self.showdown_index)

        return status

    def can_show_or_muck_hole_cards(self, status: bool | None = None) -> bool:
        """Return whether the hole card showing or mucking can be done.

        :param status: The optional status.
        :return: ``True`` if the hole crad showing or mucking can be done,
                 otherwise ``False``.
        """
        try:
            self.verify_hole_card_showing_or_mucking(status)
        except ValueError:
            return False

        return True

    def show_or_muck_hole_cards(self, status: bool | None = None) -> None:
        """Show or muck hole cards.

        If the status is not given, the hole cards will be shown if and
        only if there is chance of winning the pot. Otherwise, the hand
        will be mucked.

        :param status: The optional status.
        :return: A tuple containing the showdown index and the status.
        """
        status = self.verify_hole_card_showing_or_mucking(status)
        showdown_index = self._pop_showdown_index()

        if status:
            self._show_hole_cards(showdown_index)
        else:
            self._muck_hole_cards(showdown_index)

        if not self.showdown_indices:
            self._end_showdown()

    # Hand killing

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

            self.hand_killing_statuses[i] = not self.can_win(i)

        if not any(self.hand_killing_statuses):
            self._end_hand_killing()

    def _end_hand_killing(self) -> None:
        for i in self.player_indices:
            self.hand_killing_statuses[i] = False

        self._begin_chip_pushing()

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

    def kill_hand(self, player_index: int | None = None) -> int:
        """Kill hand.

        :param player_index: The optional player index.
        :return: The hand killing index.
        :raises ValueError: If the hand killing cannot be done.
        """
        player_index = self.verify_hand_killing(player_index)
        self.hand_killing_statuses[player_index] = False

        self._muck_hole_cards(player_index)

        if not any(self.hand_killing_statuses):
            self._end_hand_killing()

        return player_index

    # Chip pushing

    chip_pushing_status: bool = field(default=False, init=False)
    """The chip pushing status."""

    def _begin_chip_pushing(self) -> None:
        assert not self.chip_pushing_status

        self.street_index = None
        self.chip_pushing_status = True

    def _end_chip_pushing(self) -> None:
        self.chip_pushing_status = False

        self._begin_chip_pulling()

    def verify_chip_pushing(self) -> None:
        """Verify the chip pushing.

        :return: ``None``.
        :raises ValueError: If the chip pushing cannot be done.
        """
        if not self.chip_pushing_status:
            raise ValueError('chip push not allowed')

    def can_push_chips(self) -> bool:
        """Return whether the chip pushing can be done.

        :return: ``True`` if the chip pushing can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chip_pushing()
        except ValueError:
            return False

        return True

    def push_chips(self) -> None:
        """Push chips.

        :return: ``None``.
        :raises ValueError: If the chip pushing cannot be done.
        """
        self.verify_chip_pushing()

        self.chip_pushing_status = False

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

            for pot in self.pots:
                assert len(pot.player_indices) > 1

                for i in self.hand_type_indices:
                    hands = tuple(self.get_up_hands(i))
                    max_hand = max_or_none(hands)
                    player_indices = [
                        j for j in pot.player_indices if hands[j] == max_hand
                    ]
                    amount = pot.amount // self.hand_type_count

                    if not i:
                        amount += pot.amount % self.hand_type_count

                    push(player_indices, amount)

        self._end_chip_pushing()

    # Chip pulling

    chip_pulling_statuses: list[bool] = field(default_factory=list, init=False)
    """The chip pulling statuses."""

    def _setup_chip_pulling(self) -> None:
        assert not self.chip_pulling_statuses

        for _ in range(self.player_count):
            self.chip_pulling_statuses.append(False)

    def _begin_chip_pulling(self) -> None:
        assert not any(self.chip_pulling_statuses)

        for i in self.player_indices:
            self.chip_pulling_statuses[i] = self.bets[i] > 0

        assert any(self.chip_pulling_statuses)

    def _end_chip_pulling(self) -> None:
        for i in self.player_indices:
            self.chip_pulling_statuses[i] = False

        self.status = False

    @property
    def chip_pulling_indices(self) -> Iterator[int]:
        """Iterate through players who can pull chips.

        :return: The chip pullers.
        """
        try:
            self._verify_chip_pulling()
        except ValueError:
            return None

        for i in self.player_indices:
            if self.chip_pulling_statuses[i]:
                yield i

    def _verify_chip_pulling(self) -> None:
        if not any(self.chip_pulling_statuses):
            raise ValueError('no one can pull chips')

    def verify_chip_pulling(self, player_index: int | None = None) -> int:
        """Verify the chip pulling.

        :param player_index: The optional player index.
        :return: The chip pulling index.
        :raises ValueError: If the chip pulling cannot be done.
        """
        self._verify_chip_pulling()

        if player_index is None:
            player_index = next(self.chip_pulling_indices)

        if not self.chip_pulling_statuses[player_index]:
            raise ValueError('no chip to be pulled')

        return player_index

    def can_pull_chips(self, player_index: int | None = None) -> bool:
        """Return whether the chip pulling can be done.

        :param player_index: The optional player index.
        :return: ``True`` if the chip pulling can be done, otherwise
                 ``False``.
        """
        try:
            self.verify_chip_pulling(player_index)
        except ValueError:
            return False

        return True

    def pull_chips(self, player_index: int | None = None) -> int:
        """Pull chips..

        :param player_index: The optional player index.
        :return: The chip pulling index.
        :raises ValueError: If the chip pulling cannot be done.
        """
        player_index = self.verify_chip_pulling(player_index)

        self.stacks[player_index] += self.bets[player_index]
        self.bets[player_index] = 0
        self.chip_pulling_statuses[player_index] = False

        if not any(self.chip_pulling_statuses):
            self._end_chip_pulling()

        return player_index
