""":mod:`pokerkit.tests.test_papers` implements unit tests for
the various rules of poker.
"""

from copy import deepcopy
from unittest import TestCase, main

from pokerkit.games import NoLimitTexasHoldem, PotLimitOmahaHoldem
from pokerkit.state import Automation


class WSOPTournamentRulesTestCase(TestCase):
    def test_2024_96(self) -> None:
        state = NoLimitTexasHoldem.create_state(
            tuple(Automation),
            True,
            0,
            (100, 200),
            200,
            (650, 20000, 20000),
            3,
        )

        state.complete_bet_or_raise_to(600)
        state.complete_bet_or_raise_to(650)
        state.check_or_call()

        self.assertFalse(state.can_complete_bet_or_raise_to())

        state = PotLimitOmahaHoldem.create_state(
            tuple(Automation),
            True,
            0,
            [5, 10],
            10,
            (400, 400, 1000, 400, 100),
            5,
        )

        state.complete_bet_or_raise_to(30)
        state.complete_bet_or_raise_to(90)
        state.complete_bet_or_raise_to(100)
        state.fold()
        state.fold()

        self.assertTrue(state.can_complete_bet_or_raise_to(200))

    def test_2024_96_a(self) -> None:
        state = NoLimitTexasHoldem.create_state(
            tuple(Automation),
            True,
            1,
            0,
            1,
            (20001, 20001, 20001, 1301, 1701),
            5,
        )

        state.complete_bet_or_raise_to(500)
        state.complete_bet_or_raise_to(1000)
        state.check_or_call()
        state.complete_bet_or_raise_to(1300)
        state.complete_bet_or_raise_to(1700)

        hypothetical_state = deepcopy(state)

        hypothetical_state.check_or_call()

        self.assertTrue(hypothetical_state.can_complete_bet_or_raise_to())
        self.assertEqual(
            hypothetical_state.min_completion_betting_or_raising_to_amount,
            2200,
        )
        self.assertEqual(
            hypothetical_state.max_completion_betting_or_raising_to_amount,
            20000,
        )

        hypothetical_state.check_or_call()

        self.assertTrue(hypothetical_state.can_complete_bet_or_raise_to())
        self.assertEqual(
            hypothetical_state.min_completion_betting_or_raising_to_amount,
            2200,
        )
        self.assertEqual(
            hypothetical_state.max_completion_betting_or_raising_to_amount,
            20000,
        )

        hypothetical_state = deepcopy(state)

        hypothetical_state.fold()

        self.assertTrue(hypothetical_state.can_complete_bet_or_raise_to())
        self.assertEqual(
            hypothetical_state.min_completion_betting_or_raising_to_amount,
            2200,
        )
        self.assertEqual(
            hypothetical_state.max_completion_betting_or_raising_to_amount,
            20000,
        )

        hypothetical_state.check_or_call()

        self.assertTrue(hypothetical_state.can_complete_bet_or_raise_to())
        self.assertEqual(
            hypothetical_state.min_completion_betting_or_raising_to_amount,
            2200,
        )
        self.assertEqual(
            hypothetical_state.max_completion_betting_or_raising_to_amount,
            20000,
        )


if __name__ == '__main__':
    main()  # pragma: no cover
