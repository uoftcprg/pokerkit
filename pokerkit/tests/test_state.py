""":mod:`pokerkit.tests.test_state` implements unit tests for
:mod:`pokerkit.state`.
"""

from hashlib import md5
from itertools import combinations
from unittest import main, TestCase

from pokerkit.games import (
    FixedLimitDeuceToSevenLowballTripleDraw,
    FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
    FixedLimitRazz,
    FixedLimitSevenCardStud,
    NoLimitShortDeckHoldem,
    NoLimitTexasHoldem,
)
from pokerkit.state import (
    Automation,
    _HighHandOpeningLookup,
    _LowHandOpeningLookup,
)
from pokerkit.tests.test_lookups import LookupTestCaseMixin
from pokerkit.utilities import Deck, ValuesLike


class LowHandOpeningLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        combinations_ = []

        for i in range(1, 5):
            for combination in combinations(Deck.STANDARD, i):
                combinations_.append(combination)

        lookup = _LowHandOpeningLookup()
        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            '9b19d8c42e4b03661329b424d7b6c8e9',
        )


class HighHandOpeningLookupTestCase(LookupTestCaseMixin, TestCase):
    def test_get_entry(self) -> None:
        combinations_ = []

        for i in range(1, 5):
            for combination in combinations(Deck.STANDARD, i):
                combinations_.append(combination)

        lookup = _HighHandOpeningLookup()
        combinations_.sort(key=lookup.get_entry)
        string = self.serialize_combinations(combinations_)
        algorithm = md5()
        algorithm.update(string.encode())

        self.assertEqual(
            algorithm.hexdigest(),
            'b11a0c444a528e78c5be57c7bb6db06c',
        )


class StateTestCase(TestCase):
    def test_all_ins(self) -> None:
        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            False,
            {1: 2},
            (1, 2),
            2,
            (6, 4, 1),
            3,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        self.assertRaises(ValueError, state.complete_bet_or_raise_to)
        state.check_or_call()
        self.assertRaises(ValueError, state.complete_bet_or_raise_to)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [6, 0, 5])

        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            (1, 2),
            2,
            (6, 4, 1),
            3,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        self.assertRaises(ValueError, state.complete_bet_or_raise_to)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [8, 0, 3])

        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            (1, 2),
            2,
            (3, 4, 1),
            3,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [4, 1, 3])

        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            (1, 2),
            2,
            (3, 4, 6, 1, 2, 2),
            6,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.deal_hole('JcJd')
        state.deal_hole('TcTd')
        state.deal_hole('9c9d')
        self.assertRaises(ValueError, state.complete_bet_or_raise_to)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 18, 0, 0, 0])

        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            (1, 2),
            2,
            (200, 2, 200),
            3,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.complete_bet_or_raise_to(100)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.complete_bet_or_raise_to(100)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 402])

        state = NoLimitTexasHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            (1, 2),
            2,
            (2, 200, 200),
            3,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.complete_bet_or_raise_to(100)
        self.assertRaises(ValueError, state.complete_bet_or_raise_to)
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs2c')
        state.complete_bet_or_raise_to(100)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('3c')
        state.burn_card('??')
        state.deal_board('4c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 402])

        state = NoLimitShortDeckHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            {-1: 2},
            2,
            (2, 2, 2, 2, 2, 6),
            6,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.deal_hole('JcJd')
        state.deal_hole('TcTd')
        state.deal_hole('9c9d')
        state.burn_card('??')
        state.deal_board('QhQs6c')
        state.burn_card('??')
        state.deal_board('7c')
        state.burn_card('??')
        state.deal_board('8c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 12, 0, 0, 4])

        state = NoLimitShortDeckHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            {-1: 2},
            2,
            (2, 2, 3, 3, 2, 6),
            6,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.deal_hole('JcJd')
        state.deal_hole('TcTd')
        state.deal_hole('9c9d')
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs6c')
        state.burn_card('??')
        state.deal_board('7c')
        state.burn_card('??')
        state.deal_board('8c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 15, 0, 0, 3])

        state = NoLimitShortDeckHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            {-1: 2},
            2,
            (2, 2, 3, 3, 2, 6),
            6,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.deal_hole('JcJd')
        state.deal_hole('TcTd')
        state.deal_hole('9c9d')
        state.check_or_call()
        state.fold()
        state.burn_card('??')
        state.deal_board('QhQs6c')
        state.burn_card('??')
        state.deal_board('7c')
        state.burn_card('??')
        state.deal_board('8c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 14, 1, 0, 3])

        state = NoLimitShortDeckHoldem.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            2,
            {-1: 2},
            2,
            (2, 2, 5, 3, 2, 6),
            6,
        )

        state.deal_hole('AcAd')
        state.deal_hole('KcKd')
        state.deal_hole('QcQd')
        state.deal_hole('JcJd')
        state.deal_hole('TcTd')
        state.deal_hole('9c9d')
        state.check_or_call()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('QhQs6c')
        state.burn_card('??')
        state.deal_board('7c')
        state.burn_card('??')
        state.deal_board('8c')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [0, 0, 18, 1, 0, 1])

        state = FixedLimitOmahaHoldemHighLowSplitEightOrBetter.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            100,
            (100, 200),
            200,
            400,
            150,
            2,
        )

        state.deal_hole('AcAdAhAs')
        state.deal_hole('KcKdKhKs')
        state.burn_card('??')
        state.deal_board('JcJdJh')
        state.burn_card('??')
        state.deal_board('Js')
        state.burn_card('??')
        state.deal_board('Tc')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [300, 0])

        state = FixedLimitSevenCardStud.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            50,
            200,
            400,
            (200, 150, 175),
            3,
        )

        state.deal_hole('AcAdAh')
        state.deal_hole('KcKdKh')
        state.deal_hole('QcQdQh')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_hole('As')
        state.deal_hole('Ks')
        state.deal_hole('Qs')
        state.burn_card('??')
        state.deal_hole('2c')
        state.deal_hole('2d')
        state.deal_hole('2h')
        state.burn_card('??')
        state.deal_hole('3c')
        state.deal_hole('3d')
        state.deal_hole('3h')
        state.burn_card('??')
        state.deal_hole('4c')
        state.deal_hole('4d')
        state.deal_hole('4h')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [525, 0, 0])

        state = FixedLimitSevenCardStud.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            50,
            200,
            400,
            (200, 150, 175),
            3,
        )

        state.deal_hole('AcAdAh')
        state.deal_hole('KcKdKh')
        state.deal_hole('QcQdQh')
        state.post_bring_in()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_hole('As')
        state.deal_hole('Ks')
        state.deal_hole('Qs')
        state.burn_card('??')
        state.deal_hole('2c')
        state.deal_hole('2d')
        state.deal_hole('2h')
        state.burn_card('??')
        state.deal_hole('3c')
        state.deal_hole('3d')
        state.deal_hole('3h')
        state.burn_card('??')
        state.deal_hole('4c')
        state.deal_hole('4d')
        state.deal_hole('4h')
        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [525, 0, 0])

    def test_automated_dealing(self) -> None:
        state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.HOLE_DEALING,
                Automation.BOARD_DEALING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            (1, 2),
            2,
            4,
            200,
            6,
        )

        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.stand_pat_or_discard(state.hole_cards[0])
        state.stand_pat_or_discard(state.hole_cards[1])
        state.stand_pat_or_discard(state.hole_cards[2])
        state.stand_pat_or_discard(state.hole_cards[3])
        state.stand_pat_or_discard(state.hole_cards[4])
        state.stand_pat_or_discard(state.hole_cards[5])
        state.burn_card('??')
        state.check_or_call()

    def test_reshuffling(self) -> None:
        state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.HOLE_DEALING,
                Automation.BOARD_DEALING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            (1, 2),
            2,
            4,
            200,
            6,
        )

        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.stand_pat_or_discard(state.hole_cards[0])
        state.stand_pat_or_discard(state.hole_cards[1])
        state.stand_pat_or_discard(state.hole_cards[2])
        state.stand_pat_or_discard(state.hole_cards[3])
        state.stand_pat_or_discard(state.hole_cards[4])
        state.stand_pat_or_discard(state.hole_cards[5])
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.stand_pat_or_discard(state.hole_cards[0])
        state.stand_pat_or_discard(state.hole_cards[1])
        state.stand_pat_or_discard(state.hole_cards[2])
        state.stand_pat_or_discard(state.hole_cards[3])
        state.stand_pat_or_discard(state.hole_cards[4])
        state.stand_pat_or_discard(state.hole_cards[5])
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.stand_pat_or_discard(state.hole_cards[0])
        state.stand_pat_or_discard(state.hole_cards[1])
        state.stand_pat_or_discard(state.hole_cards[2])
        state.stand_pat_or_discard(state.hole_cards[3])
        state.stand_pat_or_discard(state.hole_cards[4])
        state.stand_pat_or_discard(state.hole_cards[5])
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

    def test_hole_to_board_dealing(self) -> None:
        state = FixedLimitRazz.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            True,
            0,
            1,
            2,
            4,
            200,
            9,
        )

        for _ in range(3 * state.player_count):
            state.deal_hole()

        state.complete_bet_or_raise_to()

        for _ in range(state.player_count - 1):
            state.check_or_call()

        for _ in range(state.player_count):
            state.deal_hole()

        for _ in range(state.player_count):
            state.check_or_call()

        for _ in range(state.player_count):
            state.deal_hole()

        for _ in range(state.player_count):
            state.check_or_call()

        self.assertFalse(state.can_deal_hole())
        self.assertRaises(ValueError, state.deal_hole)
        self.assertTrue(state.can_deal_board())
        state.deal_board()

        for _ in range(state.player_count):
            state.check_or_call()

        self.assertFalse(state.can_deal_hole())
        self.assertRaises(ValueError, state.deal_hole)
        self.assertTrue(state.can_deal_board())
        state.deal_board()

        for _ in range(state.player_count):
            state.check_or_call()

    def test_preflop_opener(self) -> None:

        def create_state(
                forced_bets: ValuesLike,
                player_count: int,
        ):
            return NoLimitTexasHoldem.create_state(
                tuple(Automation),
                False,
                0,
                forced_bets,
                2,
                200,
                player_count,
            )

        self.assertEqual(create_state((1, 2), 2).actor_index, 1)
        self.assertEqual(create_state((1, 2), 3).actor_index, 2)
        self.assertEqual(create_state((1, 2), 6).actor_index, 2)
        self.assertEqual(create_state((1, 2, 4), 6).actor_index, 3)
        self.assertEqual(create_state((1, 2, 4, 8), 6).actor_index, 4)
        self.assertEqual(create_state((1, 2, 0, 0, 0, 4), 6).actor_index, 0)
        self.assertEqual(create_state((1, 2, 4, 0, 0, 8), 6).actor_index, 0)


if __name__ == '__main__':
    main()  # pragma: no cover
