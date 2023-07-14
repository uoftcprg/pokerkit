""":mod:`pokerkit.state` implements classes related to poker states."""

from collections import Counter, deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum, auto, unique
from functools import partial
from itertools import islice
from operator import getitem

from pokerkit.hands import Hand
from pokerkit.lookups import Label, Lookup
from pokerkit.utilities import Card, RankOrder, Suit, max_or_none, min_or_none


@unique
class BettingStructure(Enum):
    """The enum class for betting structures."""

    FIXED_LIMIT = auto()
    """The fixed-limit."""
    POT_LIMIT = auto()
    """The pot-limit."""
    NO_LIMIT = auto()
    """The no-limit."""


@unique
class Opening(Enum):
    """The enum class for openings."""

    POSITION = auto()
    """The opener is decided by position.

    If blinds/straddles are present, they are taken account of.
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


@dataclass
class _HighHandOpeningLookup(Lookup):
    def __post_init__(self) -> None:
        for i in range(1, 5):
            self._add_multisets(
                RankOrder.ROTATED,
                Counter({1: i}),
                (False, True),
                Label.HIGH_CARD,
            )

        for i in range(3):
            self._add_multisets(
                RankOrder.ROTATED,
                Counter({2: 1, 1: i}),
                (False,),
                Label.ONE_PAIR,
            )

        self._add_multisets(
            RankOrder.ROTATED,
            Counter({2: 2}),
            (False,),
            Label.TWO_PAIR,
        )

        for i in range(2):
            self._add_multisets(
                RankOrder.ROTATED,
                Counter({3: 1, 1: i}),
                (False,),
                Label.THREE_OF_A_KIND,
            )

        self._add_multisets(
            RankOrder.ROTATED,
            Counter({4: 1}),
            (False,),
            Label.FOUR_OF_A_KIND,
        )


@dataclass(frozen=True)
class Dealing:
    """The class for dealings."""

    burn_status: bool
    """Whether to burn card."""
    hole_deal_statuses: tuple[bool, ...]
    """The statuses of dealt hole cards."""
    board_deal_count: int
    """The number of dealt board cards."""
    discard_and_draw_status: bool
    """Whether to discard and draw prior to betting."""

    def __post_init__(self) -> None:
        if self.board_deal_count < 0:
            raise ValueError('negative number of dealt cards')


@dataclass(frozen=True)
class Street:
    """The class for streets."""

    dealing: Dealing
    """The dealing."""
    opening: Opening
    """The opening."""
    min_bet_or_raise_amount: int
    """The min-bet/raise amount."""
    max_bet_or_raise_count: int | None
    """The maximum number of bet/raises."""

    def __post_init__(self) -> None:
        if self.min_bet_or_raise_amount <= 0:
            raise ValueError('non-positive minimum bet/raise amount')
        elif (
                self.max_bet_or_raise_count is not None
                and self.max_bet_or_raise_count < 0
        ):
            raise ValueError('negative maximum bet/raise count')


@dataclass(frozen=True)
class Pot:
    """The class for pots."""

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
    """The class for states."""

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
    """The blinds/straddles."""
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
    ante_statuses: list[bool] = field(default_factory=list, init=False)
    """The player ante statuses."""
    blind_or_straddle_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The player blind/straddle statuses."""
    bet_collection_status: bool = field(default=False, init=False)
    """The bet collection status."""
    bet_trimming_status: bool = field(default=True, init=False)
    """The bet trimming status during bet collection."""
    burn_status: bool = field(default=False, init=False)
    """The card burn status."""
    hole_deal_statuses: list[deque[bool]] = field(
        default_factory=list,
        init=False,
    )
    """The statuses of the cards to be dealt to holes."""
    board_deal_count: int = field(default=0, init=False)
    """The number of cards to be dealt to the board."""
    discard_and_draw_statuses: list[bool] = field(
        default_factory=list,
        init=False,
    )
    """The statuses of the discard and draw."""
    bring_in_status: bool = field(default=False, init=False)
    """The bring-in status."""
    completion_status: bool = field(default=False, init=False)
    """The completion status."""
    actor_indices: deque[int] = field(default_factory=deque, init=False)
    """The actor indices."""
    opener_index: int | None = field(default=None, init=False)
    """The opener index."""
    bet_or_raise_amount: int = field(default=0, init=False)
    """The last bet/raise amount."""
    bet_or_raise_count: int | None = field(default=None, init=False)
    """The number of bet/raises."""
    kill_statuses: list[bool] = field(default_factory=list, init=False)
    """The kill statuses."""
    chip_push_status: bool = field(default=False, init=False)
    """The chip push status."""

    def __post_init__(self) -> None:
        if not self.streets:
            raise ValueError('empty streets')
        elif not self.streets[0].dealing.hole_deal_statuses:
            raise ValueError('first street not hole dealing')
        elif (
                min(self.antes) < 0
                or min(self.blinds_or_straddles) < 0
                or self.bring_in < 0
        ):
            raise ValueError('negative antes/blinds/straddles/bring-ins')
        elif min(self.starting_stacks) <= 0:
            raise ValueError('non-positive starting stacks')
        elif (
                not any(self.antes)
                and not any(self.blinds_or_straddles)
                and not self.bring_in
        ):
            raise ValueError('no antes/blinds/straddles/bring-in')
        elif any(self.blinds_or_straddles) and self.bring_in:
            raise ValueError('both blinds/straddles and bring-in')
        elif self.bring_in >= self.streets[0].min_bet_or_raise_amount:
            raise ValueError('bring-in must be less than min bet amount')
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
            self.ante_statuses.append(False)
            self.blind_or_straddle_statuses.append(False)
            self.hole_deal_statuses.append(deque())
            self.discard_and_draw_statuses.append(False)
            self.kill_statuses.append(False)

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
    def street_discard_and_draw_statuses(self) -> Iterator[bool]:
        """Return the discard/draw statuses.

        :return: The discard/draw statuses.
        """
        for street in self.streets:
            yield street.dealing.discard_and_draw_status

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

        :return: The street.
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
        if not self.status:
            assert sum(self.stacks) == sum(self.starting_stacks)

            return

        total_ante = 0
        contributions = list(self.starting_stacks)

        for i in self.player_indices:
            assert self.stacks[i] <= self.starting_stacks[i]

            ante = min(self.antes[i], self.starting_stacks[i])
            total_ante += ante
            contributions[i] -= ante + self.bets[i] + self.stacks[i]

        previous_contribution = 0
        amount = total_ante

        for contribution in sorted(set(contributions)):
            player_indices = []

            for i in self.player_indices:
                if contributions[i] >= contribution:
                    amount += contribution - previous_contribution

                    if self.statuses[i]:
                        player_indices.append(i)

            yield Pot(amount, tuple(player_indices))

            previous_contribution = contribution
            amount = 0

    @property
    def hole_dealee_index(self) -> int | None:
        """Return the hole dealee index.

        :return: The hole dealee index.
        """
        if any(self.hole_deal_statuses):
            dealee_index = None
            status_count = 0

            for i, statuses in enumerate(self.hole_deal_statuses):
                if dealee_index is None or len(statuses) > status_count:
                    dealee_index = i
                    status_count = len(statuses)

            assert dealee_index is not None
            assert status_count

            return dealee_index

        return None

    @property
    def discard_and_drawer_index(self) -> int | None:
        """Return the discarder and drawer index.

        :return: The discarder and drawer index.
        """
        if any(self.discard_and_draw_statuses):
            return self.discard_and_draw_statuses.index(True)

        return None

    @property
    def actor_index(self) -> int | None:
        """Return the actor index.

        :return: The actor index.
        """
        if not self.actor_indices:
            return None

        return self.actor_indices[0]

    @property
    def min_bet_or_raise_to_amount(self) -> int | None:
        """Return the minimum bet/raise to amount.

        :return: The minimum bet/raise to amount.
        """
        if self.actor_index is None:
            return None

        if self.completion_status:
            amount = self.bet_or_raise_amount
        else:
            amount = self.bet_or_raise_amount + max(self.bets)

        return min(
            self.get_effective_stack(self.actor_index)
            + self.bets[self.actor_index],
            amount,
        )

    @property
    def pot_bet_or_raise_to_amount(self) -> int | None:
        """Return the pot bet/raise to amount.

        :return: The pot bet/raise to amount.
        """
        if self.actor_index is None:
            return None

        return min(
            self.stacks[self.actor_index] + self.bets[self.actor_index],
            2 * max(self.bets) - self.bets[self.actor_index]
            + self.total_pot_amount,
        )

    @property
    def max_bet_or_raise_to_amount(self) -> int | None:
        """Return the maximum bet/raise to amount.

        :return: The maximum bet/raise to amount.
        """
        if self.actor_index is None:
            return None

        match self.betting_structure:
            case BettingStructure.FIXED_LIMIT:
                amount = self.min_bet_or_raise_to_amount
            case BettingStructure.POT_LIMIT:
                amount = self.pot_bet_or_raise_to_amount
            case BettingStructure.NO_LIMIT:
                amount = (
                    self.stacks[self.actor_index]
                    + self.bets[self.actor_index]
                )
            case _:
                raise AssertionError

        assert (
            amount is None
            or (
                amount
                <= self.stacks[self.actor_index] + self.bets[self.actor_index]
            )
        )

        return amount

    @property
    def kill_index(self) -> int | None:
        """Return the index of a player whose hand is to be killed.

        :return: The index of the player whose hand is to be killed.
        """
        if not any(self.kill_statuses):
            return None

        return self.kill_statuses.index(True)

    def get_effective_stack(self, player_index: int) -> int:
        """Return the effective stack of the player.

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

    def get_down_cards(self, player_index: int) -> Iterator[Card]:
        for card, status in zip(
                self.hole_cards[player_index],
                self.hole_card_statuses[player_index],
        ):
            if not status:
                yield card

    def get_up_cards(self, player_index: int) -> Iterator[Card]:
        for card, status in zip(
                self.hole_cards[player_index],
                self.hole_card_statuses[player_index],
        ):
            if status:
                yield card

    def get_hand(self, player_index: int, hand_type_index: int) -> Hand | None:
        try:
            hand = self.hand_types[hand_type_index].from_game(
                self.hole_cards[player_index],
                self.board_cards,
            )
        except ValueError:
            hand = None

        return hand

    def get_up_hands(self, hand_type_index: int) -> Iterator[Hand | None]:
        for i in self.player_indices:
            try:
                hand = self.hand_types[hand_type_index].from_game(
                    self.get_up_cards(i),
                    self.board_cards,
                )
            except ValueError:
                hand = None

            yield hand

    def can_win(self, player_index: int) -> bool:
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

    def _begin_ante_posting(self) -> None:
        assert not any(self.ante_statuses)

        for i in self.player_indices:
            self.ante_statuses[i] = self.antes[i] > 0

        if not any(self.ante_statuses):
            self._end_ante_posting()

    def post_ante(self, player_index: int) -> None:
        """Post the ante of the player.

        :return: ``None``.
        :raises ValueError: If the player cannot ante.
        """
        if not self.ante_statuses[player_index]:
            raise ValueError('player already anted or cannot ante')

        ante = min(self.antes[player_index], self.stacks[player_index])

        assert ante
        assert not self.bets[player_index]

        self.ante_statuses[player_index] = False
        self.bets[player_index] = ante
        self.stacks[player_index] -= ante

        if not any(self.ante_statuses):
            self._end_ante_posting()

    def _end_ante_posting(self) -> None:
        self._begin_bet_collection()

    def _begin_bet_collection(self) -> None:
        assert not any(self.ante_statuses)
        assert not self.bet_collection_status

        self.bet_collection_status = True
        self.bet_trimming_status = self.street is not None

        if not any(self.bets):
            self._end_bet_collection()

    def collect_bets(self) -> None:
        """Collect all the bets of the players.

        :return: ``None``.
        :raises ValueError: If the bets cannot be collected.
        """
        if not self.bet_collection_status:
            raise ValueError('bet collection prohibited')

        self.bet_collection_status = False

        if self.bet_trimming_status:
            max_bet = sorted(self.bets)[-2]

            for i in self.player_indices:
                if self.bets[i] > max_bet:
                    assert self.statuses[i]

                    self.stacks[i] += self.bets[i] - max_bet

        for i in self.player_indices:
            self.bets[i] = 0

        self._end_bet_collection()

    def _end_bet_collection(self) -> None:
        self.bet_collection_status = False
        self.bet_trimming_status = True

        if sum(self.statuses) == 1:
            self._begin_chip_push()
        elif self.street is None:
            self._begin_blind_or_straddle_posting()
        elif self.street is self.streets[-1]:
            self._begin_showdown()
        else:
            self._begin_dealing()

    def _begin_blind_or_straddle_posting(self) -> None:
        assert not any(self.ante_statuses)
        assert not self.bet_collection_status
        assert not any(self.blind_or_straddle_statuses)

        for i in self.player_indices:
            self.blind_or_straddle_statuses[i] = (
                self.blinds_or_straddles[i] > 0 and self.stacks[i] > 0
            )

        if not any(self.blind_or_straddle_statuses):
            self._end_blind_or_straddle_posting()

    def post_blind_or_straddle(self, player_index: int) -> None:
        """Post the blind or straddle of the player.

        :return: ``None``.
        :raises ValueError: If the player cannot post blind or straddle.
        """
        if not self.blind_or_straddle_statuses[player_index]:
            raise ValueError('player cannot be blinded/straddled')

        if self.player_count == 2:
            blind_or_straddle = self.blinds_or_straddles[not player_index]
        else:
            blind_or_straddle = self.blinds_or_straddles[player_index]

        blind_or_straddle = min(blind_or_straddle, self.stacks[player_index])

        assert blind_or_straddle
        assert not self.bets[player_index]

        self.blind_or_straddle_statuses[player_index] = False
        self.bets[player_index] = blind_or_straddle
        self.stacks[player_index] -= blind_or_straddle

        if not any(self.blind_or_straddle_statuses):
            self._end_blind_or_straddle_posting()

    def _end_blind_or_straddle_posting(self) -> None:
        for i in self.player_indices:
            self.blind_or_straddle_statuses[i] = False

        if not any(self.hole_deal_statuses):
            self._begin_dealing()

    def _begin_dealing(self) -> None:
        assert not any(self.hole_deal_statuses)
        assert not self.board_deal_count
        assert not any(self.discard_and_draw_statuses)

        if self.street_index is None:
            self.street_index = 0
        else:
            self.street_index += 1

        assert self.street is not None

        self.burn_status = self.street.dealing.burn_status

        for i in self.player_indices:
            if self.statuses[i]:
                self.hole_deal_statuses[i].extend(
                    self.street.dealing.hole_deal_statuses,
                )
                self.discard_and_draw_statuses[i] = (
                    self.street.dealing.discard_and_draw_status
                )

        self.board_deal_count = self.street.dealing.board_deal_count

        assert (
            any(self.hole_deal_statuses)
            or self.board_deal_count
            or any(self.discard_and_draw_statuses)
        )

    def burn_card(self) -> None:
        """Burn a card.

        :return: ``None``.
        :raises ValueError: If a card cannot be burnt.
        """
        if not self.burn_status:
            raise ValueError('no pending burns')

        assert self.deck

        card = self.deck.popleft()
        self.burn_status = False

        self.burned_cards.append(card)

    def deal_hole(self) -> None:
        """Deal the hole card of the next player to be dealt.

        :return: ``None``.
        :raises ValueError: If the hole card cannot be dealt.
        """
        if not any(self.hole_deal_statuses):
            raise ValueError('no pending hole deals')
        elif self.burn_status:
            raise ValueError('card not burnt')

        player_index = self.hole_dealee_index

        assert player_index is not None
        assert (
            len(self.hole_deal_statuses[player_index])
            == max(map(len, self.hole_deal_statuses))
        )
        assert self.deck

        status = self.hole_deal_statuses[player_index].popleft()
        card = self.deck.popleft()

        self.hole_cards[player_index].append(card)
        self.hole_card_statuses[player_index].append(status)

        if (
                not any(self.hole_deal_statuses)
                and not self.board_deal_count
                and not any(self.discard_and_draw_statuses)
        ):
            self._end_dealing()

    def deal_board(self) -> None:
        """Deal card(s) to the board.

        :return: ``None``.
        :raises ValueError: If a card cannot be dealt to the board.
        """
        if not self.board_deal_count:
            raise ValueError('no pending board deals')
        elif self.burn_status:
            raise ValueError('card not burnt')

        assert len(self.deck) >= self.board_deal_count

        for _ in range(self.board_deal_count):
            self.board_cards.append(self.deck.popleft())

        self.board_deal_count = 0

        if (
                not any(self.hole_deal_statuses)
                and not any(self.discard_and_draw_statuses)
        ):
            self._end_dealing()

    def discard_and_draw(
            self,
            discarded_cards: list[Card],
    ) -> None:
        """Discard and draw some cards.

        :return: ``None``.
        :raises ValueError: If no player can discard and draw.
        """
        if not any(self.discard_and_draw_statuses):
            raise ValueError('no pending draws')
        elif self.burn_status:
            raise ValueError('card not burnt')

        player_index = self.discard_and_drawer_index

        assert player_index is not None
        assert self.discard_and_draw_statuses[player_index]
        assert len(self.deck) >= len(discarded_cards)

        if not set(discarded_cards) <= set(self.hole_cards[player_index]):
            raise ValueError('discarded cards not a subset of hole cards')

        self.discard_and_draw_statuses[player_index] = False

        for discarded_card in discarded_cards:
            index = self.hole_cards[player_index].index(discarded_card)
            self.hole_cards[player_index][index] = self.deck.popleft()

        if (
                not any(self.hole_deal_statuses)
                and not self.board_deal_count
                and not any(self.discard_and_draw_statuses)
        ):
            self._end_dealing()

    def _end_dealing(self) -> None:
        self.burn_status = False
        self.board_deal_count = 0

        for i in self.player_indices:
            self.hole_deal_statuses[i].clear()
            self.discard_and_draw_statuses[i] = False

        self._begin_betting()

    def _begin_betting(self) -> None:

        def card_key(rank_order: RankOrder, card: Card) -> tuple[int, Suit]:
            return rank_order.index(card.rank), card.suit

        assert not self.bring_in_status
        assert not self.completion_status
        assert not self.actor_indices
        assert self.street is not None

        self.opener_index = None

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
                        key=partial(card_key, RankOrder.ROTATED),
                    ) for i in self.player_indices
                ]
                self.opener_index = min_up_cards.index(
                    min_or_none(
                        min_up_cards,
                        key=partial(card_key, RankOrder.ROTATED),
                    ),
                )
            case Opening.HIGH_CARD:
                max_up_cards = [
                    max_or_none(
                        self.get_up_cards(i),
                        key=partial(card_key, RankOrder.STANDARD),
                    ) for i in self.player_indices
                ]
                self.opener_index = max_up_cards.index(
                    max_or_none(
                        max_up_cards,
                        key=partial(card_key, RankOrder.STANDARD),
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

        self.bet_or_raise_amount = self.street.min_bet_or_raise_amount
        self.bet_or_raise_count = self.street.max_bet_or_raise_count

        if len(self.actor_indices) <= 1:
            self._end_betting()

    def fold(self) -> None:
        """Fold.

        :return: ``None``.
        """
        if self.street is None:
            raise ValueError('in showdown')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None
        assert self.stacks[actor_index]

        if self.bets[actor_index] >= max(self.bets):
            raise ValueError('redundant fold')

        self.actor_indices.popleft()
        self._muck_hole_cards(actor_index)

        assert any(self.statuses)

        if not self.actor_indices or sum(self.statuses) == 1:
            self._end_betting()

    def check_or_call(self) -> None:
        """Check/call.

        :return: ``None``.
        """
        if self.street is None:
            raise ValueError('in showdown')
        elif self.bring_in_status:
            raise ValueError('bring-in not posted')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None
        assert self.stacks[actor_index]

        self.actor_indices.popleft()

        amount = min(
            self.stacks[actor_index],
            max(self.bets) - self.bets[actor_index],
        )
        self.stacks[actor_index] -= amount
        self.bets[actor_index] += amount

        if not self.actor_indices:
            self._end_betting()

    def post_bring_in(self) -> None:
        """Post bring-in.

        :return: ``None``.
        """
        if self.street is None:
            raise ValueError('in showdown')
        elif not self.bring_in_status:
            raise ValueError('bring-in cannot be posted')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None
        assert self.stacks[actor_index]
        assert not any(self.bets)
        assert self.bring_in
        assert self.completion_status

        amount = min(
            self.stacks[actor_index],
            self.bring_in,
        )
        self.stacks[actor_index] -= amount
        self.bets[actor_index] += amount
        self.bring_in_status = False

        self.actor_indices.popleft()

        assert self.actor_indices

    def complete_bet_or_raise_to(self, amount: int | None = None) -> None:
        """Complete, bet, or raise to an amount.

        :return: ``None``.
        """
        if self.street is None:
            raise ValueError('in showdown')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None
        assert self.stacks[actor_index]

        if amount is None:
            amount = self.min_bet_or_raise_to_amount

        assert amount is not None
        assert self.min_bet_or_raise_to_amount is not None
        assert self.max_bet_or_raise_to_amount is not None

        if amount < self.min_bet_or_raise_to_amount:
            raise ValueError('below min bet/raise to amount')
        elif amount > self.max_bet_or_raise_to_amount:
            raise ValueError('above max bet/raise to amount')
        elif self.bet_or_raise_count == 0:
            raise ValueError('no more bet/raises permitted')

        for i in self.player_indices:
            if (
                    i != actor_index
                    and self.statuses[i]
                    and self.stacks[i] + self.bets[i] > max(self.bets)
            ):
                break
        else:
            raise ValueError('irrelevant bet/raise')

        self.actor_indices.popleft()

        bet_or_raise_amount = amount - max(self.bets)
        self.stacks[actor_index] -= amount - self.bets[actor_index]
        self.bets[actor_index] = amount
        self.actor_indices = deque(self.player_indices)
        self.bring_in_status = False
        self.completion_status = False

        self.actor_indices.rotate(-actor_index)
        self.actor_indices.popleft()

        for i in self.player_indices:
            if not self.statuses[i] or not self.stacks[i]:
                if i in self.actor_indices:
                    self.actor_indices.remove(i)

        self.opener_index = actor_index
        self.bet_or_raise_amount = max(
            self.bet_or_raise_amount,
            bet_or_raise_amount,
        )

        if self.bet_or_raise_count is not None:
            self.bet_or_raise_count -= 1

        assert self.actor_indices

    def _end_betting(self) -> None:
        assert sum(self.statuses) >= 1

        self.bring_in_status = False
        self.completion_status = False

        self.actor_indices.clear()

        show = False

        assert self.street_index is not None

        if (
                sum(self.statuses) > 1
                and not any(
                    islice(
                        self.street_discard_and_draw_statuses,
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

    def _begin_showdown(self) -> None:
        assert not self.actor_indices

        self.street_index = None
        self.actor_indices = deque(self.player_indices)

        if self.opener_index is not None:
            self.actor_indices.rotate(-self.opener_index)

        for i in self.player_indices:
            if not self.statuses[i] or all(self.hole_card_statuses[i]):
                self.actor_indices.remove(i)

        if not self.actor_indices:
            self._end_showdown()

    def show_hole_cards(self) -> None:
        """Show hole cards.

        :return: ``None``.
        """
        if self.street is not None:
            raise ValueError('not in showdown')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None

        self.actor_indices.popleft()
        self._show_hole_cards(actor_index)

        if not self.actor_indices:
            self._end_showdown()

    def muck_hole_cards(self) -> None:
        """Muck hole cards.

        :return: ``None``.
        """
        if self.street is not None:
            raise ValueError('not in showdown')
        elif not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None

        self.actor_indices.popleft()
        self._muck_hole_cards(actor_index)

        if not self.actor_indices:
            self._end_showdown()

    def show_or_muck_hole_cards(self) -> None:
        """Show or muck hole cards.

        The hole cards will be shown if and only if there is chance of
        winning the pot. Otherwise, the hand will be mucked.

        :return: ``None``.
        """
        if not self.actor_indices:
            raise ValueError('no player to act')

        actor_index = self.actor_index

        assert actor_index is not None

        if self.can_win(actor_index):
            self.show_hole_cards()
        else:
            self.muck_hole_cards()

    def _end_showdown(self) -> None:
        self.actor_indices.clear()
        self._begin_hand_killing()

    def _begin_hand_killing(self) -> None:
        assert not any(self.kill_statuses)
        assert self.street is None

        for i in self.player_indices:
            if not self.statuses[i]:
                continue

            assert self.statuses[i]

            self.kill_statuses[i] = not self.can_win(i)

        if not any(self.kill_statuses):
            self._end_hand_killing()

    def kill_hand(self) -> None:
        """Kill hand.

        :return: ``None``.
        """
        if not any(self.kill_statuses):
            raise ValueError('no hand to be killed')

        player_index = self.kill_index

        assert player_index is not None

        self.kill_statuses[player_index] = False
        self._muck_hole_cards(player_index)

        if not any(self.kill_statuses):
            self._end_hand_killing()

    def _end_hand_killing(self) -> None:
        for i in self.player_indices:
            self.kill_statuses[i] = False

        self._begin_chip_push()

    def _begin_chip_push(self) -> None:
        assert not self.chip_push_status

        self.street_index = None
        self.chip_push_status = True

    def push_chips(self) -> None:
        """Push chips.

        :return: ``None``.
        """
        if not self.chip_push_status:
            raise ValueError('chip push not allowed')

        self.chip_push_status = False

        if sum(self.statuses) == 1:
            for pot in self.pots:
                assert len(pot.player_indices) == 1

                self.stacks[pot.player_indices[0]] += pot.amount
        else:

            def push(player_indices: list[int], amount: int) -> None:
                player_indices.sort()

                for j, k in enumerate(player_indices):
                    assert self.statuses[k]

                    sub_amount = amount // len(player_indices)

                    if not j:
                        sub_amount += amount % len(player_indices)

                    self.stacks[k] += sub_amount

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

        self._end_chip_push()

    def _end_chip_push(self) -> None:
        self.chip_push_status = False
        self.status = False

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
