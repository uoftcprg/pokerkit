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
            ante_trimming_status: bool,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            small_bet: int,
            big_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
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
        ...         Automation.CHIP_PUSHING,
        ...         Automation.CHIP_PULLING,
        ...     ),
        ...     True,
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     2,
        ... )

        Below shows the pre-flop dealings and actions.

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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
        ...     True,
        ...     500,
        ...     (1000, 2000),
        ...     2000,
        ...     (1125600, 2000000, 553500),
        ...     3,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing and actions.

        >>> state.deal_board('Jc3d5c')
        State.BoardDealing(cards=(Jc, 3d, 5c))

        >>> state.complete_bet_or_raise_to(35000)  # Ivey
        State.CompletionBettingOrRaisingTo(player_index=0, amount=35000)
        >>> state.check_or_call()  # Dwan
        State.CheckingOrCalling(player_index=2, amount=35000)

        Below shows the turn dealing and actions.

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

        Below shows the river dealing.

        >>> state.deal_board('Jh')
        State.BoardDealing(cards=(Jh,))

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
            ante_trimming_status,
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
            ante_trimming_status: bool,
            antes: int | Iterable[int] | Mapping[int, int] | None,
            blinds_or_straddles: Iterable[int] | Mapping[int, int],
            min_bet: int,
            starting_stacks: int | Iterable[int],
            player_count: int,
    ) -> State:
        """Create a no-limit short-deck hold'em game.

        Below shows an all-in hand between Xuan and Phua.

        Link: https://youtu.be/QlgCcphLjaQ

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
        ...     True,
        ...     3000,
        ...     {-1: 3000},
        ...     3000,
        ...     (495000, 232000, 362000, 403000, 301000, 204000),
        ...     6,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing.

        >>> state.deal_board('9h6cKc')
        State.BoardDealing(cards=(9h, 6c, Kc))

        Below shows the turn dealing.

        >>> state.deal_board('Jh')
        State.BoardDealing(cards=(Jh,))

        Below shows the river dealing.

        >>> state.deal_board('Ts')
        State.BoardDealing(cards=(Ts,))

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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
        ...     True,
        ...     None,
        ...     (50000, 100000),
        ...     2000,
        ...     (125945025, 67847350),
        ...     2,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the flop dealing and actions.

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

        Below shows the turn dealing.

        >>> state.deal_board('5h')
        State.BoardDealing(cards=(5h,))

        Below shows the river dealing.

        >>> state.deal_board('9c')
        State.BoardDealing(cards=(9c,))

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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
            ante_trimming_status,
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
    """The class for no-limit deuce-to-seven lowball single draw games.
    """

    @classmethod
    def create_state(
            cls,
            automations: tuple[Automation, ...],
            ante_trimming_status: bool,
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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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

        >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
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
        ...     True,
        ...     None,
        ...     (75000, 150000),
        ...     150000,
        ...     300000,
        ...     (1180000, 4340000, 5910000, 10765000),
        ...     4,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the first draw and actions.

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

        Below shows the second draw and actions.

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

        Below shows the third draw and actions.

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
            ante_trimming_status,
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
            ante_trimming_status: bool,
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
        ...     True,
        ...     None,
        ...     (1, 2),
        ...     2,
        ...     4,
        ...     200,
        ...     4,
        ... )

        Below shows the pre-flop dealings and actions.

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

        Below shows the first draw and actions.

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

        Below shows the second draw and actions.

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

        Below shows the third draw and actions.

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
            ante_trimming_status,
            cls._clean_values(antes, player_count),
            cls._clean_values(blinds_or_straddles, player_count),
            0,
            cls._clean_values(starting_stacks, player_count),
        )
