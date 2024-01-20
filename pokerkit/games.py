""":mod:`pokerkit.games` implements various poker game definitions."""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from functools import partial
from typing import ClassVar

from pokerkit.hands import (
    BadugiHand,
    EightOrBetterLowHand,
    Hand,
    OmahaEightOrBetterLowHand,
    OmahaHoldemHand,
    RegularLowHand,
    ShortDeckHoldemHand,
    StandardHighHand,
    StandardLowHand,
)
from pokerkit.state import BettingStructure, Opening, Automation, State, Street
from pokerkit.utilities import Deck, divmod, rake, RankOrder, ValuesLike


class Poker(ABC):
    """The abstract base class for poker games.

    :param automations: The automations.
    :param streets: The streets.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param raw_blinds_or_straddles: The raw blinds or straddles.
    :param bring_in: The bring-in.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    deck: ClassVar[Deck]
    """The deck."""
    hand_types: ClassVar[tuple[type[Hand], ...]]
    """The hand types."""
    betting_structure: ClassVar[BettingStructure]
    """The betting structure."""

    def __init__(
            self,
            automations: tuple[Automation, ...],
            streets: tuple[Street, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            bring_in: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        self.automations: tuple[Automation, ...] = automations
        """The automations."""
        self.streets: tuple[Street, ...] = streets
        """The streets."""
        self.ante_trimming_status: bool = ante_trimming_status
        """The ante trimming status.

        Usually, if you want uniform antes, set this to ``True``.
        If you want non-uniform antes like big blind antes, set
        this to ``False``.
        """
        self.raw_antes: ValuesLike = raw_antes
        """The raw antes."""
        self.raw_blinds_or_straddles: ValuesLike = raw_blinds_or_straddles
        """The raw blinds or straddles."""
        self.bring_in: int = bring_in
        """The bring-in."""
        self.divmod: Callable[[int, int], tuple[int, int]] = divmod
        """The divmod function."""
        self.rake: Callable[[int], tuple[int, int]] = rake
        """The rake function."""

    def __call__(
            self,
            raw_starting_stacks: ValuesLike,
            player_count: int,
    ) -> State:
        return State(
            self.automations,
            self.deck,
            self.hand_types,
            self.streets,
            self.betting_structure,
            self.ante_trimming_status,
            self.raw_antes,
            self.raw_blinds_or_straddles,
            self.bring_in,
            raw_starting_stacks,
            player_count,
            self.divmod,
            self.rake,
        )

    @property
    def button_status(self) -> bool:
        """Return the button status.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.button_status
        True

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.button_status
        False

        :return: The button status.
        """
        return any(
            street.opening == Opening.POSITION for street in self.streets
        )

    @property
    def max_hole_card_count(self) -> int:
        """Return the maximum number of hole cards.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.max_hole_card_count
        2

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.max_hole_card_count
        7

        :return: The maximum number of hole cards.
        """
        return sum(
            len(street.hole_dealing_statuses) for street in self.streets
        )

    @property
    def max_down_card_count(self) -> int:
        """Return the maximum number of down cards.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.max_down_card_count
        2

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.max_down_card_count
        3

        :return: The maximum number of down cards.
        """
        return sum(
            street.hole_dealing_statuses.count(
                False,
            ) for street in self.streets
        )

    @property
    def max_up_card_count(self) -> int:
        """Return the maximum number of up cards.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.max_up_card_count
        0

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.max_up_card_count
        4

        :return: The maximum number of up cards.
        """
        return sum(
            street.hole_dealing_statuses.count(True) for street in self.streets
        )

    @property
    def max_board_card_count(self) -> int:
        """Return the maximum number of board cards.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.max_board_card_count
        5

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.max_board_card_count
        0

        :return: The maximum number of board cards.
        """
        return sum(street.board_dealing_count for street in self.streets)

    @property
    def rank_orders(self) -> tuple[RankOrder, ...]:
        """Return the rank orders.

        >>> game = NoLimitTexasHoldem((), True, 0, (1, 2), 2)
        >>> game.rank_orders  # doctest: +ELLIPSIS
        (<RankOrder.STANDARD: (<Rank.DEUCE: '2'>, <Rank.TREY: '3'>, <Rank.FO...

        >>> game = FixedLimitRazz((), True, 1, 1, 2, 4)
        >>> game.rank_orders  # doctest: +ELLIPSIS
        (<RankOrder.REGULAR: (<Rank.ACE: 'A'>, <Rank.DEUCE: '2'>, <Rank.TREY...

        :return: The rank orders.
        """
        return tuple(
            hand_type.lookup.rank_order for hand_type in self.hand_types
        )

    @property
    def small_bet(self) -> int:
        """Return the small bet.

        :return: The small bet.
        """
        return self.streets[0].min_completion_betting_or_raising_amount

    @property
    def big_bet(self) -> int:
        """Return the big bet.

        :return: The big bet.
        """
        return self.streets[-1].min_completion_betting_or_raising_amount

    @property
    def min_bet(self) -> int:
        """Return the min bet.

        :return: The min bet.
        """
        return self.small_bet


class FixedLimitPokerMixin:
    """The mixin for fixed-limit poker games."""

    betting_structure: ClassVar[BettingStructure] = (
        BettingStructure.FIXED_LIMIT
    )
    max_completion_betting_or_raising_count: ClassVar[int | None] = 4


class PotLimitPokerMixin:
    """The mixin for pot-limit poker games."""

    betting_structure: ClassVar[BettingStructure] = BettingStructure.POT_LIMIT
    max_completion_betting_or_raising_count: ClassVar[int | None] = None


class NoLimitPokerMixin:
    """The mixin for no-limit poker games."""

    betting_structure: ClassVar[BettingStructure] = BettingStructure.NO_LIMIT
    max_completion_betting_or_raising_count: ClassVar[int | None] = None


class Holdem(Poker, ABC):
    """The abstract base class for hold'em games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param raw_blinds_or_straddles: The raw blinds or straddles.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    hole_dealing_count: ClassVar[int]
    """The number of hole dealings."""
    max_completion_betting_or_raising_count: ClassVar[int | None]
    """The maximum number of completions, bettings, or raisings."""

    def __init__(
            self,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        super().__init__(
            automations,
            (
                Street(
                    False,
                    (False,) * self.hole_dealing_count,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
            ),
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            0,
            divmod,
            rake,
        )


class UnfixedLimitHoldem(Holdem, ABC):
    """The abstract base class for unfixed-limit hold'em games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param raw_blinds_or_straddles: The raw blinds or straddles.
    :param min_bet: The minimum bet.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    max_completion_betting_or_raising_count: ClassVar[int | None] = None

    def __init__(
            self,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        super().__init__(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            min_bet,
            min_bet,
            divmod,
            rake,
        )


class TexasHoldemMixin:
    """The mixin for Texas hold'em games."""

    deck: ClassVar[Deck] = Deck.STANDARD
    hand_types: ClassVar[tuple[type[Hand], ...]] = (StandardHighHand,)
    hole_dealing_count: ClassVar[int] = 2


class FixedLimitTexasHoldem(FixedLimitPokerMixin, TexasHoldemMixin, Holdem):
    """The class for fixed-limit Texas hold'em games."""

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit Texas hold'em game.

        Below is an example hand in fixed-limit Texas hold'em.

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

        Below shows the pre-flop dealings and actions.

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

        Below show the final stacks.

        >>> state.stacks
        [204, 196]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The antes.
        :param raw_blinds_or_straddles: The blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class NoLimitTexasHoldem(
        NoLimitPokerMixin,
        TexasHoldemMixin,
        UnfixedLimitHoldem,
):
    """The class for no-limit Texas hold'em games."""

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a no-limit Texas hold'em game.

        Below shows the first televised million dollar pot between
        Tom Dwan and Phil Ivey.

        Link: https://youtu.be/GnxFohpljqM

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

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing and actions.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('Jc3d5c')
        BoardDealing(cards=(Jc, 3d, 5c))

        >>> state.complete_bet_or_raise_to(35000)  # Ivey
        CompletionBettingOrRaisingTo(player_index=0, amount=35000)
        >>> state.check_or_call()  # Dwan
        CheckingOrCalling(player_index=2, amount=35000)

        Below shows the turn dealing and actions.

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

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('Jh')
        BoardDealing(cards=(Jh,))

        Below show the final stacks.

        >>> state.stacks
        [572100, 1997500, 1109500]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The antes.
        :param raw_blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            min_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class NoLimitShortDeckHoldem(NoLimitPokerMixin, UnfixedLimitHoldem):
    """The class for no-limit short-deck hold'em games."""

    deck = Deck.SHORT_DECK_HOLDEM
    hand_types = (ShortDeckHoldemHand,)
    hole_dealing_count = 2

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a no-limit short-deck hold'em game.

        Below shows an all-in hand between Xuan and Phua.

        Link: https://youtu.be/QlgCcphLjaQ

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

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('9h6cKc')
        BoardDealing(cards=(9h, 6c, Kc))

        Below shows the turn dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('Jh')
        BoardDealing(cards=(Jh,))

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('Ts')
        BoardDealing(cards=(Ts,))

        Below show the final stacks.

        >>> state.stacks
        [489000, 226000, 684000, 400000, 0, 198000]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            min_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class OmahaHoldemMixin:
    """The mixin for Omaha hold'em games."""

    deck: ClassVar[Deck] = Deck.STANDARD
    hole_dealing_count: ClassVar[int] = 4


class PotLimitOmahaHoldem(
        PotLimitPokerMixin,
        OmahaHoldemMixin,
        UnfixedLimitHoldem,
):
    """The class for pot-limit Omaha hold'em games."""

    hand_types = (OmahaHoldemHand,)

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a pot-limit Omaha hold'em game.

        Below shows the largest online poker pot every played between
        Patrik Antonius and Viktor Blom.

        Link: https://youtu.be/UMBm66Id2AA

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
        ...     1000,
        ...     (1259450.25, 678473.5),
        ...     2,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing and actions.

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

        Below shows the turn dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('5h')
        BoardDealing(cards=(5h,))

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(card=??)
        >>> state.deal_board('9c')
        BoardDealing(cards=(9c,))

        Below show the final stacks.

        >>> state.stacks
        [1937923.75, 0.0]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            min_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
        PotLimitPokerMixin,
        OmahaHoldemMixin,
        Holdem,
):
    """The class for fixed-limit Omaha hold'em high/low-split eight or
    better low games.
    """

    hand_types = (
        OmahaHoldemHand,
        OmahaEightOrBetterLowHand,
    )

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit Omaha hold'em high/low-split eight or better
        low game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class SevenCardStud(Poker, ABC):
    """The abstract base class for seven card stud games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param bring_in: The bring-in.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    max_completion_betting_or_raising_count: ClassVar[int | None]
    """The maximum number of completions, bettings, or raisings."""
    low: ClassVar[bool]
    """The low status."""

    def __init__(
            self,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        super().__init__(
            automations,
            (
                Street(
                    False,
                    (False, False, True),
                    0,
                    False,
                    Opening.HIGH_CARD if self.low else Opening.LOW_CARD,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND if self.low else Opening.HIGH_HAND,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND if self.low else Opening.HIGH_HAND,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND if self.low else Opening.HIGH_HAND,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (False,),
                    0,
                    False,
                    Opening.LOW_HAND if self.low else Opening.HIGH_HAND,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
            ),
            ante_trimming_status,
            raw_antes,
            0,
            bring_in,
            divmod,
            rake,
        )


class FixedLimitSevenCardStud(FixedLimitPokerMixin, SevenCardStud):
    """The class for fixed-limit seven card stud games."""

    deck = Deck.STANDARD
    hand_types = (StandardHighHand,)
    low = False

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit seven card stud game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            bring_in,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class FixedLimitSevenCardStudHighLowSplitEightOrBetter(
        FixedLimitPokerMixin,
        SevenCardStud,
):
    """The class for fixed-limit seven card stud high/low-split eight or
    better low games.
    """

    deck = Deck.STANDARD
    hand_types = (
        StandardHighHand,
        EightOrBetterLowHand,
    )
    low = False

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit seven card stud high/low-split eight or
        better low game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            bring_in,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class FixedLimitRazz(FixedLimitPokerMixin, SevenCardStud):
    """The class for fixed-limit razz games."""

    deck = Deck.REGULAR
    hand_types = (RegularLowHand,)
    low = True

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit razz game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            bring_in,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class Draw(Poker, ABC):
    """The abstract base class for draw games."""

    hole_dealing_count: ClassVar[int]
    """The number of hole dealings."""
    max_completion_betting_or_raising_count: ClassVar[int | None]
    """The maximum number of completions, bettings, or raisings."""


class SingleDraw(Draw, ABC):
    """The abstract base class for single draw games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param raw_blinds_or_straddles: The raw blinds or straddles.
    :param min_bet: The min bet.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    def __init__(
            self,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        super().__init__(
            automations,
            (
                Street(
                    False,
                    (False,) * self.hole_dealing_count,
                    0,
                    False,
                    Opening.POSITION,
                    min_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    min_bet,
                    self.max_completion_betting_or_raising_count,
                ),
            ),
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            0,
            divmod,
            rake,
        )


class TripleDraw(Draw, ABC):
    """The abstract base class for triple draw games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The raw antes.
    :param raw_blinds_or_straddles: The raw blinds or straddles.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    def __init__(
            self,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        super().__init__(
            automations,
            (
                Street(
                    False,
                    (False,) * self.hole_dealing_count,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    small_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    self.max_completion_betting_or_raising_count,
                ),
            ),
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            0,
            divmod,
            rake,
        )


class DeuceToSevenLowballMixin:
    """The abstract base class for deuce-to-seven lowball games."""

    deck: ClassVar[Deck] = Deck.STANDARD
    hand_types: ClassVar[tuple[type[Hand], ...]] = (StandardLowHand,)
    hole_dealing_count: ClassVar[int] = 5


class NoLimitDeuceToSevenLowballSingleDraw(
        NoLimitPokerMixin,
        DeuceToSevenLowballMixin,
        SingleDraw,
):
    """The class for no-limit deuce-to-seven lowball single draw games.
    """

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            min_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a no-limit deuce-to-seven lowball single draw game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            min_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class FixedLimitDeuceToSevenLowballTripleDraw(
        FixedLimitPokerMixin,
        DeuceToSevenLowballMixin,
        TripleDraw,
):
    """The class for fixed-limit deuce-to-seven lowball triple draw
    games.
    """

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit deuce-to-seven lowball triple draw game.

        Below shows a bad beat between Yockey and Arieh.

        Link: https://youtu.be/pChCqb2FNxY

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

        Below shows the pre-flop dealings and actions.

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

        Below shows the first draw and actions.

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

        Below shows the second draw and actions.

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

        Below shows the third draw and actions.

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

        Below show the final stacks.

        >>> state.stacks
        [0, 4190000, 5910000, 12095000]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)


class FixedLimitBadugi(FixedLimitPokerMixin, TripleDraw):
    """The class for fixed-limit badugi games."""

    deck = Deck.REGULAR
    hand_types = (BadugiHand,)
    hole_dealing_count = 4

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            small_bet: int,
            big_bet: int,
            raw_starting_stacks: ValuesLike,
            player_count: int,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit badugi game.

        Below shows an example badugi hand from Wikipedia.

        Link: https://en.wikipedia.org/wiki/Badugi

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

        Below shows the pre-flop dealings and actions.

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

        Below shows the first draw and actions.

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

        Below shows the second draw and actions.

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

        Below shows the third draw and actions.

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

        Below show the showdown.

        >>> state.show_or_muck_hole_cards('2s4c6d9h')  # Alice
        HoleCardsShowingOrMucking(player_index=3, hole_cards=(2s, 4c, 6d, 9h))
        >>> state.show_or_muck_hole_cards('3s5d7c8h')  # Carol
        HoleCardsShowingOrMucking(player_index=1, hole_cards=(3s, 5d, 7c, 8h))

        Below show the final stacks.

        >>> state.stacks
        [196, 220, 200, 184]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The raw antes.
        :param raw_blinds_or_straddles: The raw blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The raw starting stacks.
        :param player_count: The number of players.
        :param divmod: The divmod function.
        :param rake: The rake function.
        :return: The created state.
        """
        return cls(
            automations,
            ante_trimming_status,
            raw_antes,
            raw_blinds_or_straddles,
            small_bet,
            big_bet,
            divmod,
            rake,
        )(raw_starting_stacks, player_count)
