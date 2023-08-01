""":mod:`pokerkit.games` implements various poker game definitions."""

from __future__ import annotations

from abc import ABC
from collections.abc import Iterable, Mapping

from pokerkit.hands import (
    BadugiHand,
    EightOrBetterLowHand,
    OmahaEightOrBetterLowHand,
    OmahaHoldemHand,
    RegularLowHand,
    ShortDeckHoldemHand,
    StandardHighHand,
    StandardLowHand,
)
from pokerkit.state import BettingStructure, Opening, State, Street
from pokerkit.utilities import Deck, RankOrder


class Poker(ABC):
    """The abstract base class for poker games."""

    max_down_card_count: int
    """The maximum number of down cards."""
    max_up_card_count: int
    """The maximum number of up cards."""
    max_board_card_count: int
    """The maximum number of board cards."""
    rank_orders: tuple[RankOrder, ...]
    """The rank orders."""
    button_status: bool
    """The button status."""

    @classmethod
    def _clean_values(
            cls,
            values: int | Iterable[int] | Mapping[int, int] | None,
            count: int,
    ) -> tuple[int, ...]:
        if values is None:
            return (0,) * count
        elif isinstance(values, Mapping):
            parsed_values = [0] * count

            for key, value in values.items():
                parsed_values[key] = value

            return tuple(parsed_values)
        elif isinstance(values, Iterable):
            parsed_values = list(values)

            for i in range(len(parsed_values), count):
                parsed_values.append(0)

            return tuple(parsed_values)
        elif isinstance(values, int):
            return (values,) * count
        else:
            raise AssertionError


class TexasHoldem(Poker, ABC):
    """The abstract base class for Texas hold'em games."""

    max_down_card_count = 2
    max_up_card_count = 0
    max_board_card_count = 5
    rank_orders = (RankOrder.STANDARD,)
    button_status = True


class FixedLimitTexasHoldem(TexasHoldem):
    """The class for fixed-limit Texas hold'em games."""

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit Texas hold'em game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardHighHand,),
            (
                Street(
                    False,
                    (False,) * 2,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    4,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class NoLimitTexasHoldem(TexasHoldem):
    """The class for no-limit Texas hold'em games."""

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit Texas hold'em game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardHighHand,),
            (
                Street(
                    False,
                    (False,) * 2,
                    0,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
            ),
            BettingStructure.NO_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class NoLimitShortDeckHoldem(TexasHoldem):
    """The class for no-limit short-deck hold'em games."""

    max_down_card_count = 2
    max_up_card_count = 0
    max_board_card_count = 5
    rank_orders = (RankOrder.SHORT_DECK_HOLDEM,)
    button_status = True

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit short-deck hold'em game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.SHORT_DECK_HOLDEM,
            (ShortDeckHoldemHand,),
            (
                Street(
                    False,
                    (False,) * 2,
                    0,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
            ),
            BettingStructure.NO_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class OmahaHoldem(Poker, ABC):
    """The abstract base class for Omaha hold'em games."""

    max_down_card_count = 4
    max_up_card_count = 0
    max_board_card_count = 5
    button_status = True


class PotLimitOmahaHoldem(OmahaHoldem):
    """The class for pot-limit Omaha hold'em games."""

    rank_orders = (RankOrder.STANDARD,)

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a pot-limit Omaha hold'em game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (OmahaHoldemHand,),
            (
                Street(
                    False,
                    (False,) * 4,
                    0,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
            ),
            BettingStructure.POT_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class FixedLimitOmahaHoldemSplitHighEightOrBetterLow(OmahaHoldem):
    """The class for fixed-limit Omaha hold'em split-high/eight or
    better low games.
    """

    rank_orders = RankOrder.STANDARD, RankOrder.EIGHT_OR_BETTER_LOW

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit Omaha hold'em split-high/eight or better
        low game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (OmahaHoldemHand, OmahaEightOrBetterLowHand),
            (
                Street(
                    False,
                    (False,) * 4,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    3,
                    False,
                    Opening.POSITION,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (),
                    1,
                    False,
                    Opening.POSITION,
                    big_bet,
                    4,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class SevenCardStud(Poker, ABC):
    """The abstract base class for seven card stud games."""

    max_down_card_count = 3
    max_up_card_count = 4
    max_board_card_count = 0
    button_status = False


class FixedLimitSevenCardStud(SevenCardStud):
    """The class for fixed-limit seven card stud games."""

    rank_orders = (RankOrder.STANDARD,)

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit seven card stud game.

        :param antes: The antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardHighHand,),
            (
                Street(
                    False,
                    (False, False, True),
                    0,
                    False,
                    Opening.LOW_CARD,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (False,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(0, player_count),
            bring_in,
            cls._clean_values(starting_stacks, player_count),
        )


class FixedLimitSevenCardStudSplitHighEightOrBetterLow(SevenCardStud):
    """The class for fixed-limit seven card stud split-high/eight or
    better low games.
    """

    rank_orders = RankOrder.STANDARD, RankOrder.EIGHT_OR_BETTER_LOW

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit seven card stud split-high/eight or
        better low game.

        :param antes: The antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardHighHand, EightOrBetterLowHand),
            (
                Street(
                    False,
                    (False, False, True),
                    0,
                    False,
                    Opening.LOW_CARD,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (False,),
                    0,
                    False,
                    Opening.HIGH_HAND,
                    big_bet,
                    4,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(0, player_count),
            bring_in,
            cls._clean_values(starting_stacks, player_count),
        )


class FixedLimitRazz(SevenCardStud):
    """The class for fixed-limit razz games."""

    rank_orders = (RankOrder.REGULAR,)

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            bring_in: int,
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit razz game.

        :param antes: The antes.
        :param bring_in: The bring-in.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.REGULAR,
            (RegularLowHand,),
            (
                Street(
                    False,
                    (False, False, True),
                    0,
                    False,
                    Opening.HIGH_CARD,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND,
                    small_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (True,),
                    0,
                    False,
                    Opening.LOW_HAND,
                    big_bet,
                    4,
                ),
                Street(
                    True,
                    (False,),
                    0,
                    False,
                    Opening.LOW_HAND,
                    big_bet,
                    4,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(0, player_count),
            bring_in,
            cls._clean_values(starting_stacks, player_count),
        )


class DeuceToSevenLowball(Poker, ABC):
    """The abstract base class for deuce-to-seven lowball games."""

    max_down_card_count = 5
    max_up_card_count = 0
    max_board_card_count = 0
    rank_orders = (RankOrder.STANDARD,)
    button_status = True


class NoLimitDeuceToSevenLowballSingleDraw(DeuceToSevenLowball):
    """The class for no-limit deuce-to-seven lowball single draw games."""

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit deuce-to-seven lowball single draw game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param min_bet: The min bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardLowHand,),
            (
                Street(
                    False,
                    (False,) * 5,
                    0,
                    False,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    min_bet,
                    None,
                ),
            ),
            BettingStructure.NO_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class FixedLimitDeuceToSevenLowballTripleDraw(DeuceToSevenLowball):
    """The class for fixed-limit deuce-to-seven lowball triple draw
    games.
    """

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit deuce-to-seven lowball triple draw game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.STANDARD,
            (StandardLowHand,),
            (
                Street(
                    False,
                    (False,) * 5,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    small_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    None,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )


class FixedLimitBadugi(Poker):
    """The class for fixed-limit badugi games."""

    max_down_card_count = 4
    max_up_card_count = 0
    max_board_card_count = 0
    rank_orders = (RankOrder.REGULAR,)
    button_status = True

    @classmethod
    def create_state(
            cls,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit badugi game.

        :param antes: The antes.
        :param blinds_or_straddles: The blinds or straddles.
        :param small_bet: The small bet.
        :param big_bet: The big bet.
        :param starting_stacks: The starting stacks.
        :param player_count: The number of players.
        :return: The created state.
        """
        return State(
            Deck.REGULAR,
            (BadugiHand,),
            (
                Street(
                    False,
                    (False,) * 4,
                    0,
                    False,
                    Opening.POSITION,
                    small_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    small_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    None,
                ),
                Street(
                    True,
                    (),
                    0,
                    True,
                    Opening.POSITION,
                    big_bet,
                    None,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )
