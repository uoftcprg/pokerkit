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
from pokerkit.state import BettingStructure, Opening, Automation, State, Street
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit Texas hold'em game.

        Below is an example hand in fixed-limit Texas hold'em.

        >>> from pokerkit import *
        >>> state = FixedLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     2,
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('AcAs'))
        (0, (Ac, As))
        >>> state.deal_hole(Card.parse('7h6h'))
        (1, (7h, 6h))

        >>> state.complete_bet_or_raise_to()
        (1, 4)
        >>> state.complete_bet_or_raise_to()
        (0, 6)
        >>> state.fold()
        1

        Below show the final stacks.

        >>> state.stacks
        [204, 196]

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
            automations,
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit Texas hold'em game.

        Below shows the first televised million dollar pot between
        Tom Dwan and Phil Ivey.

        Link: https://youtu.be/GnxFohpljqM

        >>> from pokerkit import *
        >>> state = NoLimitTexasHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     500,
        ...     (1000, 2000),
        ...     2000,
        ...     (1125600, 2000000, 553500),
        ...     3,
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('Ac2d'))  # Ivey
        (0, (Ac, 2d))
        >>> state.deal_hole(Card.parse('5h7s'))  # Antonius*
        (1, (5h, 7s))
        >>> state.deal_hole(Card.parse('7h6h'))  # Dwan
        (2, (7h, 6h))

        >>> state.complete_bet_or_raise_to(7000)  # Dwan
        (2, 7000)
        >>> state.complete_bet_or_raise_to(23000)  # Ivey
        (0, 23000)
        >>> state.fold()  # Antonius
        1
        >>> state.check_or_call()  # Dwan
        (2, 16000)

        Below shows the flop dealing and actions.

        >>> state.deal_board(Card.parse('Jc3d5c'))
        (Jc, 3d, 5c)

        >>> state.complete_bet_or_raise_to(35000)  # Ivey
        (0, 35000)
        >>> state.check_or_call()  # Dwan
        (2, 35000)

        Below shows the turn dealing and actions.

        >>> state.deal_board(Card.parse('4h'))
        (4h,)

        >>> state.complete_bet_or_raise_to(90000)  # Ivey
        (0, 90000)
        >>> state.complete_bet_or_raise_to(232600)  # Dwan
        (2, 232600)
        >>> state.complete_bet_or_raise_to(1067100)  # Ivey
        (0, 1067100)
        >>> state.check_or_call()  # Dwan
        (2, 262400)

        Below shows the river dealing.

        >>> state.deal_board(Card.parse('Jh'))
        (Jh,)

        Below show the final stacks.

        >>> state.stacks
        [572100, 1997500, 1109500]

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
            automations,
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit short-deck hold'em game.

        Below shows an all-in hand between Xuan and Phua.

        Link: https://youtu.be/QlgCcphLjaQ

        >>> from pokerkit import *
        >>> state = NoLimitShortDeckHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     3000,
        ...     {-1: 3000},
        ...     3000,
        ...     (495000, 232000, 362000, 403000, 301000, 204000),
        ...     6,
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('Th8h'))  # Badziakouski
        (0, (Th, 8h))
        >>> state.deal_hole(Card.parse('QsJd'))  # Zhong
        (1, (Qs, Jd))
        >>> state.deal_hole(Card.parse('QhQd'))  # Xuan
        (2, (Qh, Qd))
        >>> state.deal_hole(Card.parse('8d7c'))  # Jun
        (3, (8d, 7c))
        >>> state.deal_hole(Card.parse('KhKs'))  # Phua
        (4, (Kh, Ks))
        >>> state.deal_hole(Card.parse('8c7h'))  # Koon
        (5, (8c, 7h))

        >>> state.check_or_call()  # Badziakouski
        (0, 3000)
        >>> state.check_or_call()  # Zhong
        (1, 3000)
        >>> state.complete_bet_or_raise_to(35000)  # Xuan
        (2, 35000)
        >>> state.fold()  # Jun
        3
        >>> state.complete_bet_or_raise_to(298000)  # Phua
        (4, 298000)
        >>> state.fold()  # Koon
        5
        >>> state.fold()  # Badziakouski
        0
        >>> state.fold()  # Zhong
        1
        >>> state.check_or_call()  # Xuan
        (2, 263000)

        Below shows the flop dealing.

        >>> state.deal_board(Card.parse('9h6cKc'))
        (9h, 6c, Kc)

        Below shows the turn dealing.

        >>> state.deal_board(Card.parse('Jh'))
        (Jh,)

        Below shows the river dealing.

        >>> state.deal_board(Card.parse('Ts'))
        (Ts,)

        Below show the final stacks.

        >>> state.stacks
        [489000, 226000, 684000, 400000, 0, 198000]

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
            automations,
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a pot-limit Omaha hold'em game.

        Below shows the largest online poker pot every played between
        Patrik Antonius and Viktor Blom.

        Link: https://youtu.be/UMBm66Id2AA

        >>> from pokerkit import *
        >>> state = PotLimitOmahaHoldem.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     None,
        ...     (50000, 100000),
        ...     2000,
        ...     (125945025, 67847350),
        ...     2,
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('Ah3sKsKh'))  # Antonius
        (0, (Ah, 3s, Ks, Kh))
        >>> state.deal_hole(Card.parse('6d9s7d8h'))  # Blom
        (1, (6d, 9s, 7d, 8h))

        >>> state.complete_bet_or_raise_to(300000)  # Blom
        (1, 300000)
        >>> state.complete_bet_or_raise_to(900000)  # Antonius
        (0, 900000)
        >>> state.complete_bet_or_raise_to(2700000)  # Blom
        (1, 2700000)
        >>> state.complete_bet_or_raise_to(8100000)  # Antonius
        (0, 8100000)
        >>> state.check_or_call()  # Blom
        (1, 5400000)

        Below shows the flop dealing and actions.

        >>> state.deal_board(Card.parse('4s5c2h'))
        (4s, 5c, 2h)

        >>> state.complete_bet_or_raise_to(9100000)  # Antonius
        (0, 9100000)
        >>> state.complete_bet_or_raise_to(43500000)  # Blom
        (1, 43500000)
        >>> state.complete_bet_or_raise_to(77900000)  # Antonius
        (0, 77900000)
        >>> state.check_or_call()  # Blom
        (1, 16247350)

        Below shows the turn dealing.

        >>> state.deal_board(Card.parse('5h'))
        (5h,)

        Below shows the river dealing.

        >>> state.deal_board(Card.parse('9c'))
        (9c,)

        Below show the final stacks.

        >>> state.stacks
        [193792375, 0]

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
            automations,
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
            automations: tuple[Automation, ...],
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
            automations,
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
            automations: tuple[Automation, ...],
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
                    True, (True,),
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
            automations,
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
            automations: tuple[Automation, ...],
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
            automations,
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
            automations: tuple[Automation, ...],
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
            automations,
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
            automations: tuple[Automation, ...],
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
            automations,
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit deuce-to-seven lowball triple draw game.

        Below shows a bad beat between Yockey and Arieh.

        Link: https://youtu.be/pChCqb2FNxY

        >>> from pokerkit import *
        >>> state = (
        ...     FixedLimitDeuceToSevenLowballTripleDraw.create_state(
        ...         (
        ...             Automation.ANTE_POSTING,
        ...             Automation.BET_COLLECTION,
        ...             Automation.BLIND_OR_STRADDLE_POSTING,
        ...             Automation.CARD_BURNING,
        ...             Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...             Automation.HAND_KILLING,
        ...             Automation.CHIP_PUSHING,
        ...             Automation.CHIP_PULLING,
        ...         ),
        ...         None,
        ...         (75000, 150000),
        ...         150000,
        ...         300000,
        ...         (1180000, 4340000, 5910000, 10765000),
        ...         4,
        ...     )
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('7h6c4c3d2c'))  # Yockey
        (0, (7h, 6c, 4c, 3d, 2c))
        >>> state.deal_hole(Card.parse('JsJcJdJhTs'))  # Hui*
        (1, (Js, Jc, Jd, Jh, Ts))
        >>> state.deal_hole(Card.parse('KsKcKdKhTh'))  # Esposito*
        (2, (Ks, Kc, Kd, Kh, Th))
        >>> state.deal_hole(Card.parse('AsQs6s5c3c'))  # Arieh
        (3, (As, Qs, 6s, 5c, 3c))

        >>> state.fold()  # Esposito
        2
        >>> state.complete_bet_or_raise_to()  # Arieh
        (3, 300000)
        >>> state.complete_bet_or_raise_to()  # Yockey
        (0, 450000)
        >>> state.fold()  # Hui
        1
        >>> state.check_or_call()  # Arieh
        (3, 150000)

        Below shows the first draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        (0, ())
        >>> state.stand_pat_or_discard(Card.parse('AsQs'))  # Arieh
        (3, (As, Qs))
        >>> state.deal_hole(Card.parse('2hQh'))  # Arieh
        (3, (2h, Qh))

        >>> state.complete_bet_or_raise_to()  # Yockey
        (0, 150000)
        >>> state.check_or_call()  # Arieh
        (3, 150000)

        Below shows the second draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        (0, ())
        >>> state.stand_pat_or_discard(Card.parse('Qh'))  # Arieh
        (3, (Qh,))
        >>> state.deal_hole(Card.parse('4d'))  # Arieh
        (3, (4d,))

        >>> state.complete_bet_or_raise_to()  # Yockey
        (0, 300000)
        >>> state.check_or_call()  # Arieh
        (3, 300000)

        Below shows the third draw and actions.

        >>> state.stand_pat_or_discard()  # Yockey
        (0, ())
        >>> state.stand_pat_or_discard(Card.parse('6s'))  # Arieh
        (3, (6s,))
        >>> state.deal_hole(Card.parse('7c'))  # Arieh
        (3, (7c,))

        >>> state.complete_bet_or_raise_to()  # Yockey
        (0, 280000)
        >>> state.check_or_call()  # Arieh
        (3, 280000)

        Below show the final stacks.

        >>> state.stacks
        [0, 4190000, 5910000, 12095000]

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
            automations,
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
            automations: tuple[Automation, ...],
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a fixed-limit badugi game.

        Below shows an example badugi hand from Wikipedia.

        Link: https://en.wikipedia.org/wiki/Badugi

        >>> from pokerkit import *
        >>> state = FixedLimitBadugi.create_state(
        ...     (
        ...         Automation.ANTE_POSTING,
        ...         Automation.BET_COLLECTION,
        ...         Automation.BLIND_OR_STRADDLE_POSTING,
        ...         Automation.CARD_BURNING,
        ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        ...         Automation.HAND_KILLING,
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     (200,) * 4,
        ...     4,
        ... )

        Below shows the pre-flop dealings and actions.

        >>> state.deal_hole(Card.parse('As4hJcKh'))  # Bob*
        (0, (As, 4h, Jc, Kh))
        >>> state.deal_hole(Card.parse('3s5d7s8s'))  # Carol*
        (1, (3s, 5d, 7s, 8s))
        >>> state.deal_hole(Card.parse('KsKdQsQd'))  # Ted*
        (2, (Ks, Kd, Qs, Qd))
        >>> state.deal_hole(Card.parse('2s4c6dKc'))  # Alice*
        (3, (2s, 4c, 6d, Kc))

        >>> state.fold()  # Ted
        2
        >>> state.check_or_call()  # Alice
        (3, 2)
        >>> state.check_or_call()  # Bob
        (0, 1)
        >>> state.check_or_call()  # Carol
        (1, 0)

        Below shows the first draw and actions.

        >>> state.stand_pat_or_discard(Card.parse('JcKh'))  # Bob*
        (0, (Jc, Kh))
        >>> state.stand_pat_or_discard(Card.parse('7s8s'))  # Carol*
        (1, (7s, 8s))
        >>> state.stand_pat_or_discard(Card.parse('Kc'))  # Alice*
        (3, (Kc,))
        >>> state.deal_hole(Card.parse('TcJs'))  # Bob*
        (0, (Tc, Js))
        >>> state.deal_hole(Card.parse('7cTh'))  # Carol*
        (1, (7c, Th))
        >>> state.deal_hole(Card.parse('Qc'))  # Alice*
        (3, (Qc,))

        >>> state.check_or_call()  # Bob
        (0, 0)
        >>> state.complete_bet_or_raise_to()  # Carol
        (1, 2)
        >>> state.check_or_call()  # Alice
        (3, 2)
        >>> state.check_or_call()  # Bob
        (0, 2)

        Below shows the second draw and actions.

        >>> state.stand_pat_or_discard(Card.parse('Js'))  # Bob*
        (0, (Js,))
        >>> state.stand_pat_or_discard()  # Carol*
        (1, ())
        >>> state.stand_pat_or_discard(Card.parse('Qc'))  # Alice*
        (3, (Qc,))
        >>> state.deal_hole(Card.parse('Ts'))  # Bob*
        (0, (Ts,))
        >>> state.deal_hole(Card.parse('9h'))  # Alice*
        (3, (9h,))

        >>> state.check_or_call()  # Bob
        (0, 0)
        >>> state.complete_bet_or_raise_to()  # Carol
        (1, 4)
        >>> state.complete_bet_or_raise_to()  # Alice
        (3, 8)
        >>> state.fold()  # Bob
        0
        >>> state.check_or_call()  # Carol
        (1, 4)

        Below shows the third draw and actions.

        >>> state.stand_pat_or_discard(Card.parse('Th'))  # Carol*
        (1, (Th,))
        >>> state.stand_pat_or_discard()  # Alice*
        (3, ())
        >>> state.deal_hole(Card.parse('8h'))  # Carol*
        (1, (8h,))

        >>> state.check_or_call()  # Carol
        (1, 0)
        >>> state.complete_bet_or_raise_to()  # Alice
        (3, 4)
        >>> state.check_or_call()  # Carol
        (1, 4)

        Below show the final stacks.

        >>> state.stacks
        [196, 220, 200, 184]

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
            automations,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )
