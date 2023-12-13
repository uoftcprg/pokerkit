""":mod:`pokerkit.tests.test_wsop.test_2023_43` implements unit tests
for :mod:`pokerkit.state` with hands played on 2023 World Series of
Poker Event #43: $50000 Poker Players Championship.

https://www.pokergo.com/videos/6e5e4f34-9857-458c-b61e-d478ad29dbd6

Game order (in WSOP notations):
- No-limit hold'em
- Seven card stud
- Omaha 8-or-better
- Razz
- Pot-limit Omaha
- Limit hold'em
- No-limit 2-7 single draw
- Stud 8-or-better
- Limit 2-7 triple draw
"""

from collections import deque
from unittest import main, TestCase

from pokerkit.games import (
    FixedLimitDeuceToSevenLowballTripleDraw,
    FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
    FixedLimitRazz,
    FixedLimitSevenCardStud,
    FixedLimitSevenCardStudHighLowSplitEightOrBetter,
    FixedLimitTexasHoldem,
    NoLimitDeuceToSevenLowballSingleDraw,
    NoLimitTexasHoldem,
    PotLimitOmahaHoldem,
)
from pokerkit.notation import HandHistory
from pokerkit.utilities import Card


class StateTestCase(TestCase):
    def test_1_00_02_07(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 120000},
            (40000, 80000),
            80000,
        )
        state = game((7380000, 2500000, 5110000, 10170000, 4545000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7s Js Td 6d Qh',
                '   4s 8h 8c 5h 7h',
                '?? JcTs2d',
                '?? As',
                '?? Qs',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 240000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(170000)
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(140000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 780000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(325000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1430000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(600000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2630000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7340000, 3775000, 5110000, 8935000, 4545000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_2_00_08_38(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 120000},
            (40000, 80000),
            80000,
        )
        state = game((3775000, 5110000, 8935000, 4545000, 7340000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Th Qs Ac Qc As',
                '   5d 4s 5h Js Qh',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 240000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.complete_bet_or_raise_to(170000)
        state.fold()
        state.check_or_call()
        state.fold()
        state.complete_bet_or_raise_to(875000)
        state.fold()
        state.complete_bet_or_raise_to(4990000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 6195000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3735000, 4115000, 8765000, 4545000, 8545000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_3_00_15_36(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 150000},
            (50000, 100000),
            100000,
        )
        state = game((4100000, 8775000, 4550000, 8525000, 3750000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd Ts 4c 7s Qc',
                '   8s 2d 3s 5h Tc',
                '?? Th8c5d',
                '?? 9d',
                '?? Jd',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(200000)
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 600000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(175000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 950000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 950000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to(225000)
        state.complete_bet_or_raise_to(700000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1875000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4050000, 8025000, 4550000, 8525000, 4550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_4_00_18_39(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 150000},
            (50000, 100000),
            100000,
        )
        state = game((8025000, 4550000, 8525000, 4550000, 4050000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd 5h Jc 9h Jd',
                '   8s 3s 7c 4d 6s',
                '?? 2s5s2d',
                '?? As',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 350000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(175000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 700000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(300000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7750000, 4825000, 8525000, 4550000, 4050000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_5_00_22_43(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((4050000, 7750000, 4825000, 8525000, 4550000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Td Kd As 8c Kc',
                '   3c 3h 8d 5s 8s',
                '   4d 4c 5c Qc 3s',
                '??          6d 9s',
                '??          Ah Ad',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 650000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 650000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1050000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4000000, 7700000, 4775000, 8275000, 4950000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_6_00_25_05(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((4000000, 7700000, 4775000, 8275000, 4950000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd Ts 7c Th 8h',
                '   Js 9s 3s 4d 2h',
                '   Ac 8c 6d Jh Qs',
                '?? Kc 4c         ',
                '?? 5s 7h         ',
                '?? 2d 6c         ',
                '?? Ad Qc         ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3100000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2150000, 9750000, 4675000, 8225000, 4900000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_7_00_29_03(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((2150000, 9750000, 4675000, 8225000, 4900000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   8d 9s Kd Ah Qs',
                '   2d 3c 2s Jd 5s',
                '   8h 7s 3s 6c Th',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2400000, 9700000, 4575000, 8175000, 4850000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_8_00_30_52(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((2400000, 9700000, 4575000, 8175000, 4850000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qh 8s 7d 6h Qc',
                '   6c 5d 4d 3d 6d',
                '   Jd 3c Ts Td Th',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2650000, 9600000, 4525000, 8125000, 4800000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_9_00_32_02(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((2650000, 9600000, 4525000, 8125000, 4800000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd 9d Kc Qh Kh',
                '   7d 5c 7c Td 6d',
                '   5h 8d 6h Jd 2h',
                '??    9h    Qs   ',
                '??    3h    6s   ',
                '??    7h    3c   ',
                '??    5s    7s   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3100000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2600000, 11250000, 4475000, 6675000, 4700000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_10_00_34_43(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((2600000, 11250000, 4475000, 6675000, 4700000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5d 7h Js Ts Qc',
                '   2s 3s 6d 8s 9c',
                '   Ad 4h 9d Qh 9s',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2550000, 11150000, 4425000, 6925000, 4650000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_11_00_35_59(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 50000, 200000, 400000)
        state = game((2550000, 11150000, 4425000, 6925000, 4650000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qh Js 9d Qs Qd',
                '   Tc Jc 8h Ts 3c',
                '   Th 2c 8c 4s 8d',
                '?? 6c 4h         ',
                '?? Kc 7h         ',
                '?? Ah 6h         ',
                '?? 6d 9c         ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1850000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2250000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3050000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3850000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 3850000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4750000, 9500000, 4175000, 6675000, 4600000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_12_00_41_13(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((4175000, 6675000, 4600000, 4750000, 9500000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   8d Jc As Kc Ad',
                '   7d 9s 8c Td Ts',
                '   5d 9d 7s 7c 3d',
                '   4d 6s 5h 5c 2s',
                '?? 3s7hKs',
                '?? 8s',
                '?? Ah',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2100000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4075000, 5275000, 6100000, 4750000, 9500000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_13_00_43_47(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((5275000, 6100000, 4750000, 9500000, 4075000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ad 9h Js Ac Kd',
                '   Qc 8h Ts 9c Qd',
                '   Jd 7c 8d 7h 8c',
                '   2c 4d 5c 3s 4s',
                '?? 2hKh9s',
                '?? Tc',
                '?? As',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1800000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2600000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3400000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7075000, 5900000, 4750000, 7900000, 4075000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_14_00_46_43(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((5900000, 4750000, 7900000, 4075000, 7075000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kc Kd Ad Th Jd',
                '   Jh Qh Js 9s 9h',
                '   6h 8d Td 8h 9c',
                '   3s 3h 6s 3d 6d',
                '?? Ah9d6c',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [5800000, 4350000, 8400000, 4075000, 7075000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_15_00_48_29(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((4350000, 8400000, 4075000, 7075000, 5800000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5s As Kc Ah 9d',
                '   5d Qd 7d Kh 6h',
                '   4s 4d 5h Qs 6d',
                '   3c 2s 3h 2c 5c',
                '?? 7h4c8c',
                '?? Jd',
                '?? 9h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2900000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3700000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4250000, 9375000, 4075000, 6200000, 5800000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_16_00_51_22(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((9375000, 4075000, 6200000, 5800000, 4250000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ac As Ah 7h ??',
                '   Kd Qs Jh 7d ??',
                '   5s Th 7s 4c ??',
                '   3d 9c 6d 3s ??',
                '?? 6sQc7c',
                '?? Jd',
                '?? Jc',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2200000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7975000, 3875000, 7800000, 5800000, 4250000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_17_00_55_24(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((3875000, 7800000, 5800000, 4250000, 7975000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Jc Ad 5h As Ac',
                '   7c 8d 3s Ks Qs',
                '   6d 6s 3h 4s 8c',
                '   2h 3d 2d 2s 2c',
                '?? KcAhJh',
                '?? Kd',
                '?? 8s',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3100000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3775000, 7600000, 5400000, 6550000, 6375000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_18_00_58_03(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((7600000, 5400000, 6550000, 6375000, 3775000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Js Ad ?? 6c As',
                '   9h Kc ?? 5c Th',
                '   7s Qc ?? 4d Td',
                '   6d 9c ?? 2d 4c',
                '?? Qs5h9d',
                '?? Ac',
                '?? 8s',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1700000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2500000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2500000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7500000, 5450000, 6550000, 6425000, 3775000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_20_01_00_21(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6550000, 6425000, 3775000, 7500000, 5450000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7c 8s 3s Qd 9d',
                '   3h 6s 2c 7h 8c',
                '   Kc 5s 8h 2d 5c',
                '??    Jh 6c      ',
                '??    Ks Js      ',
                '??    Kd 3c      ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 700000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1900000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6450000, 5575000, 4825000, 7450000, 5400000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_21_01_02_14(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6450000, 5575000, 4825000, 7450000, 5400000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5s Qs 8d Ks Qc',
                '   4h 6s 4s 3s Tc',
                '   Th 6d 8s Qd 7s',
                '?? Ts       6c   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.check_or_call()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 350000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 550000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6700000, 5525000, 4775000, 7350000, 5350000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_22_01_03_57(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6700000, 5525000, 4775000, 7350000, 5350000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd 8h Jh 9h 6c',
                '   2c 4h Jc 5c 2h',
                '   Ad Td Qh 7h 4d',
                '??          5s Ah',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 700000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6650000, 5475000, 4675000, 7100000, 5800000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_23_01_06_16(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6650000, 5475000, 4675000, 7100000, 5800000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ks 9d Td Ad 8d',
                '   9h 7d 6s 2h 2s',
                '   8h 9s Js Th 5d',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6600000, 5425000, 4575000, 7050000, 6050000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_24_01_07_20(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6600000, 5425000, 4575000, 7050000, 6050000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   6s As 4s Tc 5h',
                '   3h 6h 3d 9c 4h',
                '   Kh 3c 2d Kd Js',
                '??    Jc 8s      ',
                '??    Ah 3s      ',
                '??    7d 5s      ',
                '??    5d 6c      ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3100000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6500000, 3575000, 6625000, 7000000, 6000000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_25_01_10_31(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((6500000, 3575000, 6625000, 7000000, 6000000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7s Ks 5h Jd 9h',
                '   6d Jc 2h 3s 7c',
                '   5c Td 6s Qd 4d',
                '?? Ts    Ad    7h',
                '?? Qh    6h      ',
                '?? Kc    4c      ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Fourth street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1300000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2100000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [5650000, 3525000, 7875000, 6900000, 5750000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_26_01_13_57(self) -> None:
        game = FixedLimitRazz((), True, 50000, 50000, 200000, 400000)
        state = game((5650000, 3525000, 7875000, 6900000, 5750000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kd Th 6c Ks 7s',
                '   5c 8d 4c 6d 3c',
                '   Jh Ah 7h 2c 5d',
                '??    Js Qh    3d',
                '??    7c 5s    As',
                '??       3s    Jc',
                '??       2s    4s',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.check_or_call()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Fourth street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Fifth Street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3100000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [5550000, 3075000, 10125000, 6850000, 4100000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_27_01_18_22(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((4100000, 5550000, 3075000, 10125000, 6850000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qh As Qc Kh Ah',
                '   Qd Jc Jh Td Ac',
                '   Tc 6d 8s 8d 7h',
                '   2h 5s 2c 3s 2d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(350000)
        state.fold()
        state.complete_bet_or_raise_to(1100000)
        state.complete_bet_or_raise_to(3350000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4600000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4050000, 4350000, 3075000, 10125000, 8100000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_28_01_22_35(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((4350000, 3075000, 10125000, 8100000, 4050000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Tc Ah Kd Ts',
                '   ?? 5h Kc 9h 8s',
                '   ?? 5d Qs 5s 6d',
                '   ?? 2c Jh 2h 3h',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to(275000)
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 525000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4300000, 2875000, 10375000, 8100000, 4050000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_29_01_25_08(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((2875000, 10375000, 8100000, 4050000, 4300000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Td Kc Qh Ac Jh',
                '   4c Js Qd Qc 7s',
                '   2d 8c Th 8s 7d',
                '   2c 5d 6d 4h 3s',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to(350000)
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 600000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2825000, 10175000, 8350000, 4050000, 4300000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_30_01_26_14(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((10175000, 8350000, 4050000, 4300000, 2825000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Jd Ah Qs 8h Tc',
                '   7h Ks 6s 8d 9h',
                '   5c 4d 6d 3s 7d',
                '   2c 2s 5d 3d 2d',
                '?? 6cJc4h',
                '?? 9s',
                '?? 7c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(300000)
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 750000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 750000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to(250000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1250000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [10125000, 7700000, 4050000, 4300000, 3525000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_31_01_29_49(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((7700000, 4050000, 4300000, 3525000, 10125000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Js Ad Kh 9h 9c',
                '   Th Ts Jc 6s 7s',
                '   Td Tc 7h 4s 5h',
                '   6d 8h 7d 4h 2h',
                '?? 3c2dKc',
                '?? Qh',
                '?? 8c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 300000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 300000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 300000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7750000, 4000000, 4300000, 3525000, 10125000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_32_01_32_58(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((4000000, 4300000, 3525000, 10125000, 7750000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Tc Ac Jh Ad Qh',
                '   9h Jd 9c Qd 9d',
                '   4h 8c 8d 7h 8s',
                '   2c 4d 5s 2s 5d',
                '?? As5h7d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(350000)
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 850000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(800000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1650000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3950000, 3850000, 3525000, 10625000, 7750000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_33_01_37_39(self) -> None:
        game = PotLimitOmahaHoldem(
            (),
            False,
            {1: 100000},
            (50000, 100000),
            100000,
        )
        state = game((3850000, 3525000, 10625000, 7750000, 3950000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qs Ks Td Qh Ac',
                '   5d Jd 8h 6d Tc',
                '   3d 7c 8c 5s 9h',
                '   2h 3c 2s 4s 2d',
                '?? 4h6h9c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(250000)
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 650000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(375000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1025000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3800000, 3175000, 10625000, 7750000, 4350000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_34_01_39_18(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((3175000, 10625000, 7750000, 4350000, 3800000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Td Tc 6s 3h Jc',
                '   4c 9s 5h 3d 4d',
                '?? Ts9d5d',
                '?? Kc',
                '?? Qh',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1700000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2500000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2500000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3075000, 11925000, 7750000, 3150000, 3800000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_35_01_42_31(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((11925000, 7750000, 3150000, 3800000, 3075000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ks Td ?? 5c Qc',
                '   Kc 4d ?? 3h 9s',
                '?? 9h2cJc',
                '?? Jd',
                '?? Tc',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1800000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2600000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3400000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [13725000, 7550000, 3150000, 3800000, 1475000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_36_01_44_49(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((7550000, 3150000, 3800000, 1475000, 13725000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Td Qs Ks ?? Jd',
                '   5c 9c Jc ?? 3c',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 700000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7450000, 2950000, 4100000, 1475000, 13725000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_37_01_45_43(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((2950000, 4100000, 1475000, 13725000, 7450000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   8h 9d Kc Td Tc',
                '   4d 7c 8s 6h 7h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 300000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2850000, 4200000, 1475000, 13725000, 7450000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_38_01_46_42(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((4200000, 1475000, 13725000, 7450000, 2850000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5s Ah 8c 5d 9s',
                '   2c Qh 6c 4s 7h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 300000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4100000, 1575000, 13725000, 7450000, 2850000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_39_01_47_38(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((1575000, 13725000, 7450000, 2850000, 4100000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Js Ah 7s 6c Qs',
                '   9c 7d 4c 4h 8s',
                '?? 4s3c2c',
                '?? 6d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 900000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1700000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1475000, 14425000, 7450000, 2850000, 3500000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_40_01_51_27(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (100000, 200000),
            200000,
            400000,
        )
        state = game((14425000, 7450000, 2850000, 3500000, 1475000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Jd 8d Jh Ah Ts',
                '   3d 7s 5d 4h Td',
                '?? AcQdKh',
                '?? 6c',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2300000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2700000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [14325000, 7250000, 2850000, 4800000, 475000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_41_01_53_52(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 150000},
            (50000, 100000),
            100000,
        )
        state = game((7250000, 2850000, 4800000, 475000, 14325000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Js Ah Qc Qd Ks',
                '   Jc Ad 9h 8h Kc',
                '   9s Ac 4h 5s Ts',
                '   7h Jd 3s 4d 7s',
                '   6s 9d 3h 3d 5c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 300000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(200000)
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 500000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [7200000, 2600000, 4800000, 775000, 14325000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_42_01_56_25(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2600000, 4800000, 775000, 14325000, 7200000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Qh Ah Kh Ad',
                '   ?? Jh 9s Qd Ts',
                '   ?? Jc 8s Js 7d',
                '   ?? 5c 8c 7h 4c',
                '   ?? 3s 2c 4h 3d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.complete_bet_or_raise_to(775000)
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1225000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2525000, 4425000, 1225000, 14325000, 7200000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_43_01_59_02(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((4425000, 1225000, 14325000, 7200000, 2525000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kd 5s Ac Ts Ks',
                '   Jh 5c 8h Th Kh',
                '   Tc 4d 4s 9c 9s',
                '   6s 3s 4h 7h 6h',
                '   3c 3h 2h 7c 3d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(1000000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1375000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4800000, 850000, 14325000, 7200000, 2525000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_44_02_00_25(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((850000, 14325000, 7200000, 2525000, 4800000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qs Qh Td Kd Qd',
                '   Qc Jd 9s 9h Jc',
                '   Js 5h 9c 8d Tc',
                '   Ts 5c 4d 3c 6h',
                '   2s ?? 3d 2d 4c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(375000)
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 825000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [775000, 13950000, 7200000, 2975000, 4800000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_45_02_01_50(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((13950000, 7200000, 2975000, 4800000, 775000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kd Js Kh Ah Ts',
                '   Jh Jd Qc Ac 9s',
                '   6c 8d Th Ks 9h',
                '   5s 5h 8h 7c 4d',
                '   4h 3h 2h 3c 2c',
                '??    Qh         ',
                '      8c         ',
                '               4s',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(775000)
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1850000)

        # Draw

        state.stand_pat_or_discard('JsJd')
        state.stand_pat_or_discard('9h')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        self.assertEqual(state.total_pot_amount, 1850000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [13875000, 6200000, 2975000, 4800000, 1850000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_46_02_04_37(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((6200000, 2975000, 4800000, 1850000, 13875000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kh As Ad Qs 8s',
                '   Kd Jc Ks 8d 7h',
                '   Jd 6s Qd 8c 5h',
                '   Tc 4d Th 3c 3h',
                '   9d 2h 2c 2d 3d',
                '??    6c         ',
                '      5s         ',
                '               Ah',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(350000)
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        # Draw

        state.stand_pat_or_discard('JcAs')
        state.stand_pat_or_discard('3h')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6125000, 2400000, 4800000, 1850000, 14525000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_47_02_07_21(self) -> None:
        game = NoLimitDeuceToSevenLowballSingleDraw(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2400000, 4800000, 1850000, 14525000, 6125000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kc Js Jd Ks Ad',
                '   8c 3s 8h Kh Ac',
                '   6s 2s 5s Qc Ts',
                '   5c 2d 4h Jh 8d',
                '   3c 2c 4c Td 6h',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(2400000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2775000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2775000, 4425000, 1850000, 14525000, 6125000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_48_02_09_20(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4425000, 1850000, 14525000, 6125000, 2775000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ac Tc Td Kd 8h',
                '   8d 4h 7h Js 3h',
                '   As 5s 2h Jd Ah',
                '?? Th          3s',
                '?? 3c          Jc',
                '?? Ts          7d',
                '?? 7c          4s',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1325000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1825000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2825000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3825000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4825000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4537500, 1800000, 14400000, 6075000, 2887500],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_49_02_13_08(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4550000, 1800000, 14400000, 6075000, 2875000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Js Tc Jh ??',
                '   ?? 4s 3h 6s ??',
                '   ?? Th Jd 2h ??',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 575000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4500000, 1750000, 14675000, 5950000, 2825000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_50_02_14_32(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4500000, 1750000, 14675000, 5950000, 2825000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   6s 5c Ac ?? Td',
                '   5h 2s 7d ?? 2h',
                '   6d Js 3h ?? Ah',
                '?? As    6c      ',
                '?? 4h    2d      ',
                '?? 7s    2c      ',
                '?? Jc    Kh      ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1250000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2250000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3250000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4250000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4575000, 1700000, 14750000, 5900000, 2775000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_51_02_18_42(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4575000, 1700000, 14750000, 5900000, 2775000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? 7d Tc 7h 8d',
                '   ?? 2d 9h 3s 3h',
                '   ?? Ts Ah 6s 2h',
                '??          4d 5c',
                '??          9c Jd',
                '??          8s 6d',
                '??          8h 2c',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1250000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2250000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3250000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4250000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4525000, 1650000, 14700000, 5975000, 2850000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_52_02_22_35(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4525000, 1650000, 14700000, 5975000, 2850000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Ts 2s 7d Ks',
                '   ?? 9c 2d 2c Jc',
                '   ?? Jh Ah 2h Kh',
                '??          Kd 8d',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4475000, 1600000, 14650000, 5675000, 3300000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_53_02_25_11(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((4475000, 1600000, 14650000, 5675000, 3300000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kd Qh Jd 7h ??',
                '   Qd 4d 7d 4h ??',
                '   Qs 6s 9h 4c ??',
                '?? 6h       2c   ',
                '?? Ad       Td   ',
                '?? Kc       Jh   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1250000)

        # Fifth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2250000)

        # Sixth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2750000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [5675000, 1550000, 14600000, 4625000, 3250000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_54_02_28_14(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            50000,
            75000,
            250000,
            500000,
        )
        state = game((5675000, 1550000, 14600000, 4625000, 3250000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7d Ts Th Kd 9c',
                '   5d 6c 8c 2c 4c',
                '   Ah 7h Tc As 3c',
                '?? 3s       Js   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 250000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [6125000, 1500000, 14550000, 4575000, 2950000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_55_02_29_59(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((6125000, 1500000, 14550000, 4575000, 2950000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qd Ks Qh Ah Js',
                '   Jc Kd Qc Ad 9s',
                '   8s 4s Jd Qs 9c',
                '   7d 4c 8c 9h 5d',
                '   5h 2s 3h 4d 2d',
                '?? As            ',
                '   6s            ',
                '      7s         ',
                '      7c         ',
                '      5c         ',
                '?? 9d            ',
                '      6h         ',
                '?? 7h            ',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        # First draw

        state.stand_pat_or_discard('QdJc')
        state.stand_pat_or_discard('KsKd4s')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2000000)

        # Second draw

        state.stand_pat_or_discard('As')
        state.stand_pat_or_discard('7s')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3000000)

        # Third draw

        state.stand_pat_or_discard('8s')
        state.stand_pat_or_discard()
        state.burn_card()
        state.deal_hole()
        self.assertEqual(state.total_pot_amount, 3000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4625000, 3000000, 14550000, 4575000, 2950000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_56_02_34_51(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((3000000, 14550000, 4575000, 2950000, 4625000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ah Jd Kc 2d 8s',
                '   Kh 9h Qd 2h 8c',
                '   Qs 7h Th 2s 6c',
                '   4h 7d 5s 3c 5d',
                '   3h 6d 2c 3s 3d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 875000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2875000, 14300000, 4575000, 2950000, 5000000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_57_02_36_12(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((14300000, 4575000, 2950000, 5000000, 2875000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qs As Kd Ad Ac',
                '   9s Ks Kc Qh Td',
                '   9h 8s 8c Ts 7h',
                '   6d 5h 7d 4d 3d',
                '   3c 4c 7c 3h 2s',
                '??    Jh         ',
                '      4s         ',
                '               Qc',
                '               5c',
                '??    4h         ',
                '      2d         ',
                '               3s',
                '??    9d         ',
                '               6h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1125000)

        # First draw

        state.stand_pat_or_discard('AsKs')
        state.stand_pat_or_discard('AcTd')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1625000)

        # Second draw

        state.stand_pat_or_discard('Jh4s')
        state.stand_pat_or_discard('Qc')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2625000)

        # Third draw

        state.stand_pat_or_discard('4h')
        state.stand_pat_or_discard('3s')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4625000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [14175000, 2325000, 2950000, 5000000, 5250000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_58_02_40_27(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((2325000, 2950000, 5000000, 5250000, 14175000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Jc Ah ?? Kd Kh',
                '   8s Ks ?? Qs Qh',
                '   6s Jd ?? 9d Ts',
                '   4d Tc ?? 8d Th',
                '   3c 3h ?? 7c 5d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 750000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2575000, 2700000, 5000000, 5250000, 14175000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_59_02_41_31(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((2700000, 5000000, 5250000, 14175000, 2575000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ac Ah ?? 6h Ad',
                '   Td Kh ?? 4d Qs',
                '   9s Th ?? 4c Qd',
                '   5h 8d ?? 3d 5s',
                '   5d 4s ?? 2s 5c',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 875000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2575000, 4750000, 5250000, 14550000, 2575000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_60_02_42_44(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((4750000, 5250000, 14550000, 2575000, 2575000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Kh As Ac Qd',
                '   ?? 7c Ad Jc Jd',
                '   ?? 6d 6h Th 5h',
                '   ?? 2c 3h Tc 5d',
                '   ?? ?? 2h 3c 4c',
                '??    5s         ',
                '      3d         ',
                '         7d      ',
                '         2s      ',
                '??       4d      ',
                '??               ',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1125000)

        # First draw

        state.stand_pat_or_discard('Kh??')
        state.stand_pat_or_discard('AsAd')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2625000)

        # Second draw

        state.stand_pat_or_discard()
        state.stand_pat_or_discard('2h')
        state.burn_card()
        state.deal_hole()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4625000)

        # Third draw

        state.stand_pat_or_discard()
        state.stand_pat_or_discard()
        state.burn_card()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 5625000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4625000, 2500000, 17425000, 2575000, 2575000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_61_02_46_42(self) -> None:
        game = FixedLimitDeuceToSevenLowballTripleDraw(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((2500000, 17425000, 2575000, 2575000, 4625000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5c 9d Kd Ac Th',
                '   4h 7h Qs Kh 7c',
                '   4d 6d Qc Js 6s',
                '   4c 6c 4s 8d 3h',
                '   3s 2c 2s 3c 2d',
                '??    8s         ',
                '      5s         ',
                '               Qh',
                '??             7d',
                '??             Jc',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-draw

        for _ in range(state.player_count * 5):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1125000)

        # First draw

        state.stand_pat_or_discard('9d6c')
        state.stand_pat_or_discard('Th')
        state.burn_card()
        state.deal_hole()
        state.deal_hole()
        state.deal_hole()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2125000)

        # Second draw

        state.stand_pat_or_discard()
        state.stand_pat_or_discard('Qh')
        state.burn_card()
        state.deal_hole()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3125000)

        # Third draw

        state.stand_pat_or_discard()
        state.stand_pat_or_discard('7d')
        state.burn_card()
        state.deal_hole()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 3125000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2375000, 19050000, 2575000, 2575000, 3125000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_62_02_51_10(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((19050000, 2575000, 2575000, 3125000, 2375000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Kc 8s 9d Tc As',
                '   8h 4s 8c 2d 4c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(2350000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2725000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [19425000, 2200000, 2575000, 3125000, 2375000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_63_02_53_09(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2200000, 2575000, 3125000, 2375000, 19425000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   4h Qd Td Ad Js',
                '   3c 6d 2s 5s 6c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(2375000)
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2825000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2125000, 2200000, 3125000, 2825000, 19425000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_64_02_54_12(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2200000, 3125000, 2825000, 19425000, 2125000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   3s Kh Jd Ks 8d',
                '   3d 6c 5h 4c 2d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(300000)
        state.fold()
        state.complete_bet_or_raise_to(2200000)
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2875000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2875000, 2750000, 2825000, 19125000, 2125000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_65_02_56_12(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2750000, 2825000, 19125000, 2125000, 2875000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   8c Qd Kh Ks Kd',
                '   2c Js 5h 5s 6c',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.complete_bet_or_raise_to(300000)
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(2600000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3200000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2675000, 3200000, 18825000, 2125000, 2875000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_66_02_57_27(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((3200000, 18825000, 2125000, 2875000, 2675000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7s Jc 8c Ks Td',
                '   5s 3c 2s Jd 5d',
                '?? 8dAdQc',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to(400000)
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1100000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to(350000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1450000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3125000, 18200000, 2125000, 3575000, 2675000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_67_03_00_32(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((18200000, 2125000, 3575000, 2675000, 3125000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Th Ac Js Kh 5d',
                '   2c 5c 4s 3h 3s',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.complete_bet_or_raise_to(1900000)
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2275000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [18050000, 2275000, 3575000, 2675000, 3125000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_68_03_02_41(self) -> None:
        game = NoLimitTexasHoldem(
            (),
            False,
            {1: 225000},
            (75000, 150000),
            150000,
        )
        state = game((2275000, 3575000, 2675000, 3125000, 18050000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   8d 9d 6c Js Ac',
                '   3s 9c 5h 4h Kc',
                '?? 2c8cTh',
                '?? Ah',
                '?? 6d',
            ),
        )

        state.post_ante()
        state.collect_bets()
        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to(300000)
        state.fold()
        state.complete_bet_or_raise_to(3350000)
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 7000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        # Flop

        state.burn_card()
        state.deal_board()
        self.assertEqual(state.total_pot_amount, 7000000)

        # Turn

        state.burn_card()
        state.deal_board()
        self.assertEqual(state.total_pot_amount, 7000000)

        # River

        state.burn_card()
        state.deal_board()
        self.assertEqual(state.total_pot_amount, 7000000)

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2200000, 0, 2675000, 3125000, 21700000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_69_03_05_55(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2675000, 3125000, 21700000, 2200000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   Ks Js Kh 7s',
                '   2h 6h Tc 5s',
                '   3d Qd Jd 9s',
                '??    9h    8c',
                '??    Jh    5d',
                '??    Kd    Jc',
                '??    4d    7d',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1275000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1775000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1775000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2775000)

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2775000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2550000, 1825000, 21650000, 3675000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_71_03_11_08(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2425000, 2050000, 21600000, 3625000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   8h 3d 9h As',
                '   5s 3c 2h Qd',
                '   Tc Kc 2d Ts',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1025000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2375000, 2525000, 21475000, 3325000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_72_03_12_55(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2375000, 2525000, 21475000, 3325000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   5d Tc As Th',
                '   2s 9h 3d 5c',
                '   Ad Ac 8c 5s',
                '??    9c 4d   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1275000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2025000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2325000, 3500000, 20675000, 3200000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_73_03_14_40(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2325000, 3500000, 20675000, 3200000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   5s Kd Jc 9c',
                '   3c 8h Ts 6h',
                '   9s 7h 8c Ah',
                '??    Kc Th   ',
                '??    2c Ac   ',
                '??    Tc 3s   ',
                '??    Jd 7c   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 700000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1200000)

        # Fifth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2200000)

        # Sixth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3200000)

        # Seventh street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4200000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2275000, 5650000, 18625000, 3150000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_74_03_17_31(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2275000, 5650000, 18625000, 3150000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   Kh Qc Td Ah',
                '   7h 5d 3h 6s',
                '   7s 3c As 5c',
                '?? 3s    4s   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 775000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1025000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2750000, 5525000, 18325000, 3100000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_75_03_19_14(self) -> None:
        game = FixedLimitSevenCardStud((), True, 50000, 75000, 250000, 500000)
        state = game((2750000, 5525000, 18325000, 3100000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   9d Kc Ah Th',
                '   7d Jh 2d 7h',
                '   4s Ts Tc Qh',
                '??    9h    6c',
                '??    7s    7c',
                '??    Js    As',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1275000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1275000)

        # Fifth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1275000)

        # Sixth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1775000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2625000, 6250000, 18275000, 2550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_76_03_22_08(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (250000,),
            250000,
            500000,
        )
        state = game((2625000, 6250000, 18275000, 2550000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Ad As Qh',
                '   ?? Ac 8c 9s',
                '   ?? Ts 3s 5d',
                '   ?? 8s 2c 4c',
                '?? Jd7s4h',
                '?? 5h',
                '?? Js',
            ),
        )

        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 250000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2250000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2750000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3750000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 3750000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2375000, 6375000, 18400000, 2550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_77_03_25_05(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((2375000, 6375000, 18400000, 2550000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   Ad Td Qs Ah',
                '   7s 9s 6c Ac',
                '   5s 4s 3s 8s',
                '   3d 3h 2c 5c',
                '?? 8h6dQd',
                '?? Jd',
                '?? Qh',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2500000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 2500000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4000000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 6000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [125000, 6125000, 22150000, 1300000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_78_03_32_24(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((6125000, 22150000, 1300000, 125000), 4)
        state.deck_cards = deque(
            Card.parse(
                '   Ad Qc 9h 4d',
                '   5d Tc 9d 3s',
                '   4s 7c 5h 3c',
                '   2c 3h 3d 2d',
                '?? JdKs2h',
                '?? Td',
                '?? Qh',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.fold()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1125000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1625000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1625000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1625000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [5375000, 23025000, 1300000, 0],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_79_03_36_22(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (125000, 250000),
            250000,
            500000,
        )
        state = game((23025000, 1300000, 5375000), 3)
        state.deck_cards = deque(
            Card.parse(
                '   Ah Kc Ac',
                '   7s Qc Ks',
                '   6d 3s Qd',
                '   2d 2h 2s',
                '?? 4s3hQh',
                '?? 5s',
                '?? 5d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 375000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1500000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3900000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4900000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 5900000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [25150000, 0, 4550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_80_03_42_38(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (150000, 300000),
            300000,
            600000,
        )
        state = game((4550000, 25150000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   Ks 9s',
                '   Js 4s',
                '   5s 3c',
                '   4d 2d',
                '?? 8s2c7d',
                '?? Jd',
                '?? 8d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1200000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1800000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3000000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 3000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [4550000, 25150000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_81_03_44_38(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (150000, 300000),
            300000,
            600000,
        )
        state = game((25150000, 4550000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   Ac Th',
                '   9h 7h',
                '   8h 7d',
                '   2c 5d',
                '?? 7c6cQh',
                '?? 5c',
                '?? 6h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1800000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2400000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3600000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 7200000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [25150000, 4550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_82_03_46_32(self) -> None:
        game = FixedLimitOmahaHoldemHighLowSplitEightOrBetter(
            (),
            True,
            0,
            (150000, 300000),
            300000,
            600000,
        )
        state = game((4550000, 25150000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   Ah 4s',
                '   Qc 2s',
                '   9h 2h',
                '   5d 2c',
                '?? 2dQsAd',
                '?? 7d',
                '?? 9s',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 450000)

        # Pre-flop

        for _ in range(state.player_count * 4):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1800000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2400000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3600000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 4800000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2150000, 27550000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_83_03_48_33(self) -> None:
        game = FixedLimitRazz((), True, 100000, 100000, 300000, 600000)
        state = game((2150000, 27550000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   Qh As',
                '   Qd 2c',
                '   8s 6h',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 600000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1950000, 27750000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_84_03_49_18(self) -> None:
        game = FixedLimitRazz((), True, 100000, 100000, 300000, 600000)
        state = game((1950000, 27750000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   Kd Ah',
                '   7s 6s',
                '   4h Kc',
                '?? As 9s',
                '?? 8c Qd',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 800000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2000000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2650000, 27050000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_85_03_50_24(self) -> None:
        game = FixedLimitRazz((), True, 100000, 100000, 300000, 600000)
        state = game((2650000, 27050000), 2)
        state.deck_cards = deque(
            Card.parse(
                '   8c 4h',
                '   2h 3d',
                '   4c 8d',
                '?? Ad 2s',
                '?? Qd Td',
                '?? Jd 8s',
                '?? Kh 7h',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 200000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1400000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2600000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 3800000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 5300000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        self.assertEqual(state.total_pot_amount, 5300000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [0, 29700000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(hh.dumps(), new_hh.dumps())


if __name__ == '__main__':
    main()  # pragma: no cover
