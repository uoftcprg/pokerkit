""":mod:`pokerkit.tests.test_games` implements unit tests for
:mod:`pokerkit.games`.
"""

from unittest import main, TestCase

from pokerkit.games import (
    KuhnPoker,
    NoLimitRoyalHoldem,
    PotLimitOmahaHoldem,
    RhodeIslandHoldem,
)
from pokerkit.hands import KuhnPokerHand
from pokerkit.state import (
    Automation,
    BettingStructure,
    Mode,
    Opening,
    State,
    Street,
)
from pokerkit.utilities import Card, Deck


class PotLimitOmahaHoldemTestCase(TestCase):
    def test_double_board(self) -> None:
        state = PotLimitOmahaHoldem.create_state(
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
            [1, 2],
            2,
            200,
            4,
            starting_board_count=2,
            mode=Mode.CASH_GAME,
        )

        state.deal_hole('AcKc3c2c')
        state.deal_hole('AdKd3d2d')
        state.deal_hole('AhKh3h2h')
        state.deal_hole('AsKs3s2s')
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.burn_card('??')
        state.deal_board('QcJcTc')
        state.deal_board('QdJdTd')
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.burn_card('??')
        state.deal_board('9c')
        state.deal_board('9d')
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.burn_card('??')
        state.deal_board('8c')
        state.deal_board('8d')
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [202, 202, 198, 198])
        self.assertEqual(state.board_count, 2)
        self.assertEqual(
            list(state.get_board_cards(0)),
            list(Card.parse('QcJcTc9c8c')),
        )
        self.assertEqual(
            list(state.get_board_cards(1)),
            list(Card.parse('QdJdTd9d8d')),
        )

        state = PotLimitOmahaHoldem.create_state(
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
            [1, 2],
            2,
            200,
            4,
            starting_board_count=2,
            mode=Mode.CASH_GAME,
        )

        state.deal_hole('AcKc3c2c')
        state.deal_hole('AdKd3d2d')
        state.deal_hole('AhKh3h2h')
        state.deal_hole('AsKs3s2s')
        state.complete_bet_or_raise_to(7)
        state.complete_bet_or_raise_to(24)
        state.complete_bet_or_raise_to(81)
        state.complete_bet_or_raise_to(200)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.select_runout_count(1)
        state.select_runout_count(1)
        state.select_runout_count(1)
        state.select_runout_count(1)

        state.burn_card('??')
        state.deal_board('QcJcTc')
        state.deal_board('QdJdTd')

        state.burn_card('??')
        state.deal_board('9c')
        state.deal_board('9d')

        state.burn_card('??')
        state.deal_board('8c')
        state.deal_board('8d')

        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [400, 400, 0, 0])
        self.assertEqual(state.board_count, 2)
        self.assertEqual(
            list(state.get_board_cards(0)),
            list(Card.parse('QcJcTc9c8c')),
        )
        self.assertEqual(
            list(state.get_board_cards(1)),
            list(Card.parse('QdJdTd9d8d')),
        )

        state = PotLimitOmahaHoldem.create_state(
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
            [1, 2],
            2,
            200,
            4,
            starting_board_count=2,
            mode=Mode.CASH_GAME,
        )

        state.deal_hole('AcKc3c2c')
        state.deal_hole('AdKd3d2d')
        state.deal_hole('AhKh3h2h')
        state.deal_hole('AsKs3s2s')
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.burn_card('??')
        state.deal_board('QcJcTc')
        state.deal_board('QdJhTs')
        state.complete_bet_or_raise_to(8)
        state.complete_bet_or_raise_to(32)
        state.complete_bet_or_raise_to(112)
        state.complete_bet_or_raise_to(198)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        state.select_runout_count(None)
        state.select_runout_count(None)
        state.select_runout_count(None)
        state.select_runout_count(2)

        state.burn_card('??')
        state.deal_board('7c')
        state.deal_board('7d')

        state.burn_card('??')
        state.deal_board('6c')
        state.deal_board('6d')

        state.burn_card('??')
        state.deal_board('5c')
        state.deal_board('7s')

        state.burn_card('??')
        state.deal_board('4c')
        state.deal_board('6s')

        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [450, 50, 50, 250])
        self.assertEqual(state.board_count, 4)
        self.assertEqual(
            list(state.get_board_cards(0)),
            list(Card.parse('QcJcTc7c6c')),
        )
        self.assertEqual(
            list(state.get_board_cards(1)),
            list(Card.parse('QcJcTc7d6d')),
        )
        self.assertEqual(
            list(state.get_board_cards(2)),
            list(Card.parse('QdJhTs5c4c')),
        )
        self.assertEqual(
            list(state.get_board_cards(3)),
            list(Card.parse('QdJhTs7s6s')),
        )


class NoLimitRoyalHoldemTestCase(TestCase):
    def test_create_state(self) -> None:
        state = NoLimitRoyalHoldem.create_state(
            tuple(Automation),
            True,
            0,
            [1, 2],
            2,
            200,
            3,
        )

        self.assertEqual(len(state.deck), 20)
        self.assertEqual(len(state.deck_cards), 14)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        self.assertEqual(len(state.deck_cards), 10)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        self.assertEqual(len(state.deck_cards), 8)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        self.assertEqual(len(state.deck_cards), 6)
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()

        self.assertFalse(state.status)


class KuhnPokerTestCase(TestCase):
    def test_create_state(self) -> None:
        state_0 = State(
            (),
            Deck.KUHN_POKER,
            (KuhnPokerHand,),
            (
                Street(
                    False,
                    (False,),
                    0,
                    False,
                    Opening.POSITION,
                    1,
                    1,
                ),
            ),
            BettingStructure.FIXED_LIMIT,
            True,
            (1,) * 2,
            (0,) * 2,
            0,
            (2,) * 2,
            2,
        )
        state_1 = KuhnPoker.create_state(())

        state_0.deck_cards.clear()
        state_1.deck_cards.clear()
        self.assertEqual(state_0, state_1)


class RhodeIslandHoldemTestCase(TestCase):
    def test_create_state(self) -> None:
        state = RhodeIslandHoldem.create_state(())

        self.assertEqual(state.starting_stacks, (155,) * 2)

        state.post_ante()
        state.post_ante()
        state.collect_bets()

        state.deal_hole('As')
        state.deal_hole('Kc')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()

        state.burn_card('??')
        state.deal_board('Ac')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()

        state.burn_card('??')
        state.deal_board('Qc')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()
        state.kill_hand()
        state.push_chips()
        state.pull_chips()

        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [100, 210])

        state = RhodeIslandHoldem.create_state(())

        self.assertEqual(state.starting_stacks, (155,) * 2)

        state.post_ante()
        state.post_ante()
        state.collect_bets()

        state.deal_hole('As')
        state.deal_hole('Kc')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        self.assertFalse(state.can_complete_bet_or_raise_to())
        state.check_or_call()
        state.collect_bets()

        state.burn_card('??')
        state.deal_board('Ac')
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        self.assertFalse(state.can_complete_bet_or_raise_to())
        state.check_or_call()
        state.collect_bets()

        state.burn_card('??')
        state.deal_board('Qc')
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        self.assertFalse(state.can_complete_bet_or_raise_to())
        state.check_or_call()
        state.collect_bets()

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()
        state.kill_hand()
        state.push_chips()
        state.pull_chips()

        self.assertFalse(state.status)
        self.assertEqual(state.stacks, [000, 310])


if __name__ == '__main__':
    main()  # pragma: no cover
