""":mod:`pokerkit.games` implements various poker game definitions.

The classes here allow users to "save" certain configurations to create
poker states in a simple manner. This is crucial, as poker states require
tons of parameters to be specified.
"""

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
from pokerkit.state import (
    Automation,
    BettingStructure,
    Mode,
    Opening,
    State,
    Street,
)
from pokerkit.utilities import Deck, divmod, rake, RankOrder, ValuesLike


class Poker(ABC):
    """The abstract base class for poker games.

    The instances of this class serves two purposes. First, it allows
    the users to save state initialization parameters so they do not
    have to be specified each time a new state is created. Second, the
    number and complexities of parameters that has to be specified to
    initialize the state is reduced.

    :param automations: The automations.
    :param streets: The streets.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The "raw" antes.
    :param raw_blinds_or_straddles: The "raw" blinds or straddles.
    :param bring_in: The bring-in.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
    :param divmod: The divmod function.
    :param rake: The rake function.
    """

    deck: ClassVar[Deck]
    """The deck.

    Different variants use different decks, which must be specified.
    """
    hand_types: ClassVar[tuple[type[Hand], ...]]
    """The hand types.

    While most poker games use just a single hand type, there exists
    variants where multiple hand types should be considered when
    evaluating hand strengths, namely in high/low-split contexts.

    In PokerKit, each concept of high and low hands are separately
    considered, through the use of multiple hand types.
    """
    betting_structure: ClassVar[BettingStructure]
    """The betting structure.

    This class attribute determines the betting limits of a particular
    game (e.g. no-limit, pot-limit, or fixed-limit).
    """

    def __init__(
            self,
            automations: tuple[Automation, ...],
            streets: tuple[Street, ...],
            ante_trimming_status: bool,
            raw_antes: ValuesLike,
            raw_blinds_or_straddles: ValuesLike,
            bring_in: int,
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> None:
        self.automations: tuple[Automation, ...] = automations
        """The automations.

        Allows the user to specify what steps they do not care about and
        therefore should be automatically handled by PokerKit.
        """
        self.streets: tuple[Street, ...] = streets
        """The streets.

        Each street contains information about the corresponding betting
        round and corresponding dealing/draw stage before it occurs.
        """
        self.ante_trimming_status: bool = ante_trimming_status
        """The ante trimming status.

        It denotes whether or not to activate the ``trimming`` behavior
        during bet collection immediately after the antes are posted.

        Usually, if you want uniform antes, set this to ``True``.  If
        you want non-uniform antes like big blind antes, set this to
        ``False``.
        """
        self.raw_antes: ValuesLike = raw_antes
        """The "raw" antes.

        In PokerKit, the term ``raw`` is used to denote the fact that
        they can be supplied in many forms and will be "parsed" or
        "evaluated" further to convert them into a more ideal form.

        For instance, ``0`` will be interpreted as no ante for all
        players. Another value will be interpreted as that value as the
        antes for all. ``[0, 2]`` and ``{1: 2} will be considered as the
        big blind ante whereas ``{-1: 2}`` will be considered as the
        button ante.
        """
        self.raw_blinds_or_straddles: ValuesLike = raw_blinds_or_straddles
        """The "raw" blinds or straddles.

        Just like for the antes, the blinds/straddles are also
        "interpreted" by PokerKit in the same fashion.
        """
        self.bring_in: int = bring_in
        """The bring-in.

        Some poker games do not have the bring-in, in which case ``0``
        should be its value.
        """
        self.mode: Mode = mode
        """The mode.

        There are two modes available to be set: the tournament and
        cash-game mode. Tournaments use a stricter rule-set than typical
        cash-games. For more details, please consult
        :class:`pokerkit.state.Mode`.
        """
        self.starting_board_count: int = starting_board_count
        """The starting board count.

        For most poker games, it should be ``1``. Of course, for double
        board games, it should be ``2``. Triple/Quadruple/etc. board
        games are almost unheard of. Therefore, this value should mostly
        be ``1`` or sometimes ``2``.
        """
        self.divmod: Callable[[int, int], tuple[int, int]] = divmod
        """The divmod function.

        This is used to denote how pots are divided up (for multiple
        boards, multiple winners, multiple hand types, etc.).
        """
        self.rake: Callable[[int], tuple[int, int]] = rake
        """The rake function.

        Rake functions are used in PokerKit to denote how the rakes are
        collected from the pot. Multiple pots may exist (side-pots) in
        which case the method is called for each pot.
        """

    def __call__(
            self,
            raw_starting_stacks: ValuesLike,
            player_count: int,
    ) -> State:
        """Create the poker state based on the game definition's
        attributes and the desired starting stacks.

        Similar to "raw" antes and "raw" blinds/straddles, the starting
        stacks can be represented in different ways which PokerKit
        interprets when creating the games. Not all representations
        explicitly express the number of players and therefore this
        value is accepted as a separate parameter ``player_count``.

        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :return: The created poker game.
        """
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
            mode=self.mode,
            starting_board_count=self.starting_board_count,
            divmod=self.divmod,
            rake=self.rake,
        )

    @property
    def button_status(self) -> bool:
        """Return whether this game is a button game (i.e. has a rotating
        button).

        We deem that a variant is a button game if it has betting round
        whose opener is decided based on position (not up card/hand like
        in stud).

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
        """Return the maximum number of hole cards a single player can
        have.

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
        """Return the maximum number of down cards a single player can
        have.

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
        """Return the maximum number of up cards a single player can
        have.

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
        """Return the maximum number of board cards that can be dealt.

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
        """Return the rank orders for each hand type used.

        A hand type may use different rank orderings (deuce-low,
        ace-low, etc.).

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

        This is the min-bet amount of the first street.

        It may be different from the big bet (primarily in fixed-limit
        games).

        :return: The small bet.
        """
        return self.streets[0].min_completion_betting_or_raising_amount

    @property
    def big_bet(self) -> int:
        """Return the big bet.

        This is the min-bet amount of the last street.

        It may be different from the small bet (primarily in fixed-limit
        games).

        :return: The big bet.
        """
        return self.streets[-1].min_completion_betting_or_raising_amount

    @property
    def min_bet(self) -> int:
        """Return the min bet.

        :return: The min bet.
        :raises ValueError: If the small and big bets are not identical.
        """
        if self.small_bet != self.big_bet:
            raise ValueError(
                (
                    f'This variant has unequal small bet ({self.small_bet})'
                    f' and big bet ({self.big_bet}) amounts and therefore the'
                    ' concept of min-bet cannot apply here.'
                ),
            )

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
    :param raw_antes: The "raw" antes.
    :param raw_blinds_or_straddles: The "raw" blinds or straddles.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
        )


class UnfixedLimitHoldem(Holdem, ABC):
    """The abstract base class for unfixed-limit hold'em games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The "raw" antes.
    :param raw_blinds_or_straddles: The "raw" blinds or straddles.
    :param min_bet: The minimum bet.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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

        >>> state.deal_hole('AcAs')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, As), statuse...
        >>> state.deal_hole('7h6h')  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(7h, 6h), statuse...

        >>> state.complete_bet_or_raise_to()
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=4)
        >>> state.complete_bet_or_raise_to()
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount=6)
        >>> state.fold()
        Folding(commentary=None, player_index=1)

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
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a no-limit Texas hold'em game.

        Below shows the 4-runout hand between Phil Hellmuth and the
        Loose Cannon Ernest Wiggins.

        Link: https://youtu.be/cnjJv7x0HMY?si=4l05Ez7lQVczt8DI&t=638

        >>> from pokerkit import Automation, Mode, NoLimitTexasHoldem
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
        ...     False,
        ...     {-1: 600},
        ...     (200, 400, 800),
        ...     400,
        ...     (999999, 116400, 86900, 999999, 50000, 999999),
        ...     6,
        ...     mode=Mode.CASH_GAME,
        ... )

        Below are the pre-flop dealings and actions.

        >>> state.deal_hole('JsTh')  # Tony G  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Js, Th), statuse...
        >>> state.deal_hole('Ah9d')  # Hellmuth  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Ah, 9d), statuse...
        >>> state.deal_hole('KsKc')  # Wiggins  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Ks, Kc), statuse...
        >>> state.deal_hole('5c2h')  # Negreanu  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(5c, 2h), statuse...
        >>> state.deal_hole('6h5h')  # Brunson  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=4, cards=(6h, 5h), statuse...
        >>> state.deal_hole('6s3s')  # Laak  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=5, cards=(6s, 3s), statuse...
        >>> state.fold()  # Negreanu
        Folding(commentary=None, player_index=3)
        >>> state.complete_bet_or_raise_to(
        ...     2800,
        ... )  # Brunson  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=4, amount...
        >>> state.fold()  # Laak
        Folding(commentary=None, player_index=5)
        >>> state.check_or_call()  # Tony G
        CheckingOrCalling(commentary=None, player_index=0, amount=2600)
        >>> state.complete_bet_or_raise_to(
        ...     12600,
        ... )  # Hellmuth  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.check_or_call()  # Wiggins
        CheckingOrCalling(commentary=None, player_index=2, amount=11800)
        >>> state.check_or_call()  # Brunson
        CheckingOrCalling(commentary=None, player_index=4, amount=9800)
        >>> state.check_or_call()  # Tony G
        CheckingOrCalling(commentary=None, player_index=0, amount=9800)

        Below are the flop dealing and actions.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('9hTs9s')
        BoardDealing(commentary=None, cards=(9h, Ts, 9s))
        >>> state.check_or_call()  # Tony G
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.complete_bet_or_raise_to(
        ...     17000,
        ... )  # Hellmuth  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.complete_bet_or_raise_to(
        ...     36000,
        ... )  # Wiggins  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.fold()  # Brunson
        Folding(commentary=None, player_index=4)
        >>> state.fold()  # Tony G
        Folding(commentary=None, player_index=0)
        >>> state.complete_bet_or_raise_to(
        ...     103800,
        ... )  # Hellmuth  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.check_or_call()  # Wiggins
        CheckingOrCalling(commentary=None, player_index=2, amount=38300)

        Below is selecting the number of runouts.

        >>> state.select_runout_count(4)  # Hellmuth
        RunoutCountSelection(commentary=None, player_index=1, runout_count=4)
        >>> state.select_runout_count(None)  # Wiggins  # doctest: +ELLIPSIS
        RunoutCountSelection(commentary=None, player_index=2, runout_count=N...

        Below is the first runout.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Jh')  # Turn
        BoardDealing(commentary=None, cards=(Jh,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ad')  # River
        BoardDealing(commentary=None, cards=(Ad,))

        Below is the second runout.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Kh')  # Turn
        BoardDealing(commentary=None, cards=(Kh,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('3c')  # River
        BoardDealing(commentary=None, cards=(3c,))

        Below is the third runout.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('7s')  # Turn
        BoardDealing(commentary=None, cards=(7s,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('8s')  # River
        BoardDealing(commentary=None, cards=(8s,))

        Below is the fourth runout.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Qc')  # Turn
        BoardDealing(commentary=None, cards=(Qc,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Kd')  # River
        BoardDealing(commentary=None, cards=(Kd,))

        Below are the final stacks.

        >>> state.stacks
        [987399, 79400, 149700, 999999, 37400, 999399]

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

        >>> state.deal_hole('Ac2d')  # Ivey  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Ac, 2d), statuse...
        >>> state.deal_hole('????')  # Antonius  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(??, ??), statuse...
        >>> state.deal_hole('7h6h')  # Dwan  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(7h, 6h), statuse...

        >>> state.complete_bet_or_raise_to(7000)  # Dwan  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.complete_bet_or_raise_to(23000)  # Ivey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.fold()  # Antonius
        Folding(commentary=None, player_index=1)
        >>> state.check_or_call()  # Dwan
        CheckingOrCalling(commentary=None, player_index=2, amount=16000)

        Below shows the flop dealing and actions.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Jc3d5c')
        BoardDealing(commentary=None, cards=(Jc, 3d, 5c))

        >>> state.complete_bet_or_raise_to(35000)  # Ivey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Dwan
        CheckingOrCalling(commentary=None, player_index=2, amount=35000)

        Below shows the turn dealing and actions.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('4h')
        BoardDealing(commentary=None, cards=(4h,))

        >>> state.complete_bet_or_raise_to(90000)  # Ivey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.complete_bet_or_raise_to(
        ...     232600,
        ... )  # Dwan  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.complete_bet_or_raise_to(
        ...     1067100,
        ... )  # Ivey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Dwan
        CheckingOrCalling(commentary=None, player_index=2, amount=262400)

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Jh')
        BoardDealing(commentary=None, cards=(Jh,))

        Below shows the final stacks.

        >>> state.stacks
        [572100, 1997500, 1109500]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The antes.
        :param raw_blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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

        >>> state.deal_hole('Th8h')  # Badziakouski  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(Th, 8h), statuse...
        >>> state.deal_hole('QsJd')  # Zhong  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(Qs, Jd), statuse...
        >>> state.deal_hole('QhQd')  # Xuan  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(Qh, Qd), statuse...
        >>> state.deal_hole('8d7c')  # Jun  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(8d, 7c), statuse...
        >>> state.deal_hole('KhKs')  # Phua  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=4, cards=(Kh, Ks), statuse...
        >>> state.deal_hole('8c7h')  # Koon  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=5, cards=(8c, 7h), statuse...

        >>> state.check_or_call()  # Badziakouski
        CheckingOrCalling(commentary=None, player_index=0, amount=3000)
        >>> state.check_or_call()  # Zhong
        CheckingOrCalling(commentary=None, player_index=1, amount=3000)
        >>> state.complete_bet_or_raise_to(35000)  # Xuan  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
        >>> state.fold()  # Jun
        Folding(commentary=None, player_index=3)
        >>> state.complete_bet_or_raise_to(
        ...     298000,
        ... )  # Phua  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=4, amount...
        >>> state.fold()  # Koon
        Folding(commentary=None, player_index=5)
        >>> state.fold()  # Badziakouski
        Folding(commentary=None, player_index=0)
        >>> state.fold()  # Zhong
        Folding(commentary=None, player_index=1)
        >>> state.check_or_call()  # Xuan
        CheckingOrCalling(commentary=None, player_index=2, amount=263000)

        Below shows the flop dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('9h6cKc')
        BoardDealing(commentary=None, cards=(9h, 6c, Kc))

        Below shows the turn dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Jh')
        BoardDealing(commentary=None, cards=(Jh,))

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('Ts')
        BoardDealing(commentary=None, cards=(Ts,))

        Below show the final stacks.

        >>> state.stacks
        [489000, 226000, 684000, 400000, 0, 198000]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
        HoleDealing(commentary=None, player_index=0, cards=(Ah, 3s, Ks, Kh),...
        >>> state.deal_hole('6d9s7d8h')  # Blom  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(6d, 9s, 7d, 8h),...

        >>> state.complete_bet_or_raise_to(3000)  # Blom  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.complete_bet_or_raise_to(
        ...     9000,
        ... )  # Antonius  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.complete_bet_or_raise_to(27000)  # Blom  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.complete_bet_or_raise_to(
        ...     81000,
        ... )  # Antonius  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Blom
        CheckingOrCalling(commentary=None, player_index=1, amount=54000)

        Below shows the flop dealing and actions.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('4s5c2h')
        BoardDealing(commentary=None, cards=(4s, 5c, 2h))

        >>> state.complete_bet_or_raise_to(
        ...     91000,
        ... )  # Antonius  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.complete_bet_or_raise_to(
        ...     435000,
        ... )  # Blom  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
        >>> state.complete_bet_or_raise_to(
        ...     779000,
        ... )  # Antonius  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Blom
        CheckingOrCalling(commentary=None, player_index=1, amount=162473.5)

        Below shows the turn dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('5h')
        BoardDealing(commentary=None, cards=(5h,))

        Below shows the river dealing.

        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_board('9c')
        BoardDealing(commentary=None, cards=(9c,))

        Below show the final stacks.

        >>> state.stacks
        [1937923.75, 0.0]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit Omaha hold'em high/low-split eight or better
        low game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
        )(raw_starting_stacks, player_count)


class SevenCardStud(Poker, ABC):
    """The abstract base class for seven card stud games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The "raw" antes.
    :param bring_in: The bring-in.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit seven card stud game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit seven card stud high/low-split eight or
        better low game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a fixed-limit razz game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
    :param raw_antes: The "raw" antes.
    :param raw_blinds_or_straddles: The "raw" blinds or straddles.
    :param min_bet: The min bet.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
        )


class TripleDraw(Draw, ABC):
    """The abstract base class for triple draw games.

    :param automations: The automations.
    :param ante_trimming_status: The ante trimming status.
    :param raw_antes: The "raw" antes.
    :param raw_blinds_or_straddles: The "raw" blinds or straddles.
    :param small_bet: The small bet.
    :param big_bet: The big bet.
    :param mode: The mode.
    :param starting_board_count: The starting board count.
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
            divmod: Callable[[int, int], tuple[int, int]] = divmod,
            rake: Callable[[int], tuple[int, int]] = partial(rake, rake=0),
    ) -> State:
        """Create a no-limit deuce-to-seven lowball single draw game.

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param min_bet: The min bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
        HoleDealing(commentary=None, player_index=0, cards=(7h, 6c, 4c, 3d, ...
        >>> state.deal_hole('??????????')  # Hui  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(??, ??, ??, ??, ...
        >>> state.deal_hole('??????????')  # Esposito  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(??, ??, ??, ??, ...
        >>> state.deal_hole('AsQs6s5c3c')  # Arieh  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(As, Qs, 6s, 5c, ...

        >>> state.fold()  # Esposito
        Folding(commentary=None, player_index=2)
        >>> state.complete_bet_or_raise_to()  # Arieh  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount...
        >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.fold()  # Hui
        Folding(commentary=None, player_index=1)
        >>> state.check_or_call()  # Arieh
        CheckingOrCalling(commentary=None, player_index=3, amount=150000)

        Below shows the first draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
        >>> state.stand_pat_or_discard('AsQs')  # Arieh  # doctest: +ELLIPSIS
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=(As, ...
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('2hQh')  # Arieh  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(2h, Qh), statuse...

        >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Arieh
        CheckingOrCalling(commentary=None, player_index=3, amount=150000)

        Below shows the second draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
        >>> state.stand_pat_or_discard('Qh')  # Arieh
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=(Qh,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('4d')  # Arieh  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(4d,), statuses=(...

        >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Arieh
        CheckingOrCalling(commentary=None, player_index=3, amount=300000)

        Below shows the third draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
        >>> state.stand_pat_or_discard('6s')  # Arieh
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=(6s,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('7c')  # Arieh  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(7c,), statuses=(...

        >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
        CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
        >>> state.check_or_call()  # Arieh
        CheckingOrCalling(commentary=None, player_index=3, amount=280000)

        Below show the final stacks.

        >>> state.stacks
        [0, 4190000, 5910000, 12095000]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
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
            *,
            mode: Mode = Mode.TOURNAMENT,
            starting_board_count: int = 1,
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
        HoleDealing(commentary=None, player_index=0, cards=(??, ??, ??, ??),...
        >>> state.deal_hole('????????')  # Carol  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(??, ??, ??, ??),...
        >>> state.deal_hole('????????')  # Ted  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=2, cards=(??, ??, ??, ??),...
        >>> state.deal_hole('????????')  # Alice  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(??, ??, ??, ??),...

        >>> state.fold()  # Ted
        Folding(commentary=None, player_index=2)
        >>> state.check_or_call()  # Alice
        CheckingOrCalling(commentary=None, player_index=3, amount=2)
        >>> state.check_or_call()  # Bob
        CheckingOrCalling(commentary=None, player_index=0, amount=1)
        >>> state.check_or_call()  # Carol
        CheckingOrCalling(commentary=None, player_index=1, amount=0)

        Below shows the first draw and actions.

        >>> state.stand_pat_or_discard('????')  # Bob  # doctest: +ELLIPSIS
        StandingPatOrDiscarding(commentary=None, player_index=0, cards=(??, ...
        >>> state.stand_pat_or_discard('????')  # Carol  # doctest: +ELLIPSIS
        StandingPatOrDiscarding(commentary=None, player_index=1, cards=(??, ...
        >>> state.stand_pat_or_discard('??')  # Alice
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=(??,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('????')  # Bob  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(??, ??), statuse...
        >>> state.deal_hole('????')  # Carol  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(??, ??), statuse...
        >>> state.deal_hole('??')  # Alice  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(??,), statuses=(...

        >>> state.check_or_call()  # Bob
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.complete_bet_or_raise_to()  # Carol
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=2)
        >>> state.check_or_call()  # Alice
        CheckingOrCalling(commentary=None, player_index=3, amount=2)
        >>> state.check_or_call()  # Bob
        CheckingOrCalling(commentary=None, player_index=0, amount=2)

        Below shows the second draw and actions.

        >>> state.stand_pat_or_discard('??')  # Bob
        StandingPatOrDiscarding(commentary=None, player_index=0, cards=(??,))
        >>> state.stand_pat_or_discard()  # Carol
        StandingPatOrDiscarding(commentary=None, player_index=1, cards=())
        >>> state.stand_pat_or_discard('??')  # Alice
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=(??,))
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('??')  # Bob  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=0, cards=(??,), statuses=(...
        >>> state.deal_hole('??')  # Alice  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=3, cards=(??,), statuses=(...

        >>> state.check_or_call()  # Bob
        CheckingOrCalling(commentary=None, player_index=0, amount=0)
        >>> state.complete_bet_or_raise_to()  # Carol
        CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=4)
        >>> state.complete_bet_or_raise_to()  # Alice
        CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount=8)
        >>> state.fold()  # Bob
        Folding(commentary=None, player_index=0)
        >>> state.check_or_call()  # Carol
        CheckingOrCalling(commentary=None, player_index=1, amount=4)

        Below shows the third draw and actions.

        >>> state.stand_pat_or_discard('??')  # Carol
        StandingPatOrDiscarding(commentary=None, player_index=1, cards=(??,))
        >>> state.stand_pat_or_discard()  # Alice
        StandingPatOrDiscarding(commentary=None, player_index=3, cards=())
        >>> state.burn_card('??')
        CardBurning(commentary=None, card=??)
        >>> state.deal_hole('??')  # Carol  # doctest: +ELLIPSIS
        HoleDealing(commentary=None, player_index=1, cards=(??,), statuses=(...

        >>> state.check_or_call()  # Carol
        CheckingOrCalling(commentary=None, player_index=1, amount=0)
        >>> state.complete_bet_or_raise_to()  # Alice
        CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount=4)
        >>> state.check_or_call()  # Carol
        CheckingOrCalling(commentary=None, player_index=1, amount=4)

        Below show the showdown.

        >>> state.show_or_muck_hole_cards(
        ...     '2s4c6d9h',
        ... )  # Alice  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=3, hole_card...
        >>> state.show_or_muck_hole_cards(
        ...     '3s5d7c8h',
        ... )  # Carol  # doctest: +ELLIPSIS
        HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...

        Below show the final stacks.

        >>> state.stacks
        [196, 220, 200, 184]

        :param automations: The automations.
        :param ante_trimming_status: The ante trimming status.
        :param raw_antes: The "raw" antes.
        :param raw_blinds_or_straddles: The "raw" blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param raw_starting_stacks: The "raw" starting stacks.
        :param player_count: The number of players.
        :param starting_board_count: The starting board count.
        :param mode: The mode.
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
            mode=mode,
            starting_board_count=starting_board_count,
            divmod=divmod,
            rake=rake,
        )(raw_starting_stacks, player_count)
