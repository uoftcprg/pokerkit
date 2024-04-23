""":mod:`pokerkit.tests.test_wsop.test_2023_43` implements unit tests
for :mod:`pokerkit.state` with hands played on the Day 4 of the 2023
World Series of Poker Event #54: $10,000 H.O.R.S.E. Championship.

https://www.pokergo.com/videos/55817f62-ddfd-481b-bcf4-6513f9023672

Game order (in WSOP notations):
- Limit hold'em
- Omaha 8-or-better
- Razz
- Seven card stud
- Stud eight or better
"""

from collections import deque
from unittest import main, TestCase

from pokerkit.games import (
    FixedLimitSevenCardStudHighLowSplitEightOrBetter,
    FixedLimitTexasHoldem,
)
from pokerkit.notation import HandHistory
from pokerkit.state import HoleDealing, Operation
from pokerkit.utilities import Card


class StateTestCase(TestCase):
    @classmethod
    def filter_hole_dealing(
            cls,
            operations: list[Operation],
    ) -> list[Operation]:
        return [
            operation for operation in operations
            if not isinstance(operation, HoleDealing)
        ]

    def test_1_00_02_05(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (1930000, 3695000, 990000, 1445000, 515000, 2160000, 265000),
            7,
        )
        state.deck_cards = deque(
            Card.parse(
                '   8s Qs Qh 6d Tc Ah Ks',
                '   5h 7h 3s 5c 3h Kd 9h',
                '   7s 8c 9c As 7c 6s 8d',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 140000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 240000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1910000, 3675000, 970000, 1585000, 495000, 2120000, 245000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_2_00_03_32(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (1910000, 3675000, 970000, 1585000, 495000, 2120000, 245000),
            7,
        )
        state.deck_cards = deque(
            Card.parse(
                '   6s Js Kc Th 8c 9h 5h',
                '   6h 7h 2h 7s 2c 5d 2s',
                '   5s Jd 3c Ks Jc 3s 8h',
                '?? 6d 7c             4h',
                '?? 9s Qh             9d',
                '?? 6c 3d             9c',
                '?? 4c Ac             Tc',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 140000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 835000)

        # Fourth street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 995000)

        # Fifth Street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1635000)

        # Sixth Street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1955000)

        # Seventh Street

        state.burn_card()

        for _ in range(3):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 2275000)

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
            [3220000, 2710000, 930000, 1565000, 475000, 2100000, 0],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_3_00_10_24(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (3220000, 2710000, 930000, 1565000, 475000, 2100000),
            6,
        )
        state.deck_cards = deque(
            Card.parse(
                '   Kc Ah Qs ?? ?? ??',
                '   2d 5d Td ?? ?? ??',
                '   7d Th 3s ?? ?? ??',
                '??    2c 4h         ',
                '??    3d Kh         ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 120000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 160000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 320000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 480000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3200000, 2910000, 810000, 1545000, 455000, 2080000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_4_00_12_25(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (3200000, 2910000, 810000, 1545000, 455000, 2080000),
            6,
        )
        state.deck_cards = deque(
            Card.parse(
                '   9c 6d Ts ?? Ac 6c',
                '   7s 3s 4s ?? 2h 3d',
                '   9h Ah 5s ?? Th Js',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 120000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 380000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3100000, 3110000, 770000, 1525000, 435000, 2060000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_5_00_13_47(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (3100000, 3110000, 770000, 1525000, 435000, 2060000),
            6,
        )
        state.deck_cards = deque(
            Card.parse(
                '   8h Qd Tc Jc Ac 3d',
                '   7c 2d 7s 7h 8c 2c',
                '   6s 9d Kh 4s Kd Ts',
                '?? Kc 5c            ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 120000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 300000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 380000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3000000, 3310000, 750000, 1485000, 415000, 2040000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_6_00_15_43(self) -> None:
        game = FixedLimitSevenCardStudHighLowSplitEightOrBetter(
            (),
            True,
            20000,
            20000,
            80000,
            160000,
        )
        state = game(
            (3000000, 3310000, 750000, 1485000, 415000, 2040000),
            6,
        )
        state.deck_cards = deque(
            Card.parse(
                '   9h 8s Ah Kd As 6s',
                '   7d 2d 9c 8d 3c 6c',
                '   Kc Tc 4d Kh 6d Jc',
                '??          Qd 8h   ',
                '??          Ad 8c   ',
                '??          Qh 9d   ',
                '??          Ks Jh   ',
            ),
        )

        for _ in state.player_indices:
            state.post_ante()

        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 120000)

        # Third street

        for _ in range(state.player_count * 3):
            state.deal_hole()

        state.post_bring_in()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.fold()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 300000)

        # Fourth street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 300000)

        # Fifth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 620000)

        # Sixth Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 930000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        # Seventh Street

        state.burn_card()

        for _ in range(2):
            state.deal_hole()

        self.assertEqual(state.total_pot_amount, 930000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.kill_hand()
        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2980000, 3290000, 710000, 2000000, 0, 2020000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_7_00_20_03(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (80000,),
            80000,
            160000,
        )
        state = game((2020000, 2980000, 3290000, 710000, 2000000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Js ?? 8d ??',
                '   ?? 3h ?? 7d ??',
            ),
        )

        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 80000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 240000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1940000, 2980000, 3290000, 790000, 2000000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_8_00_20_31(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((1940000, 2980000, 3290000, 790000, 2000000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Qs 9h Qc Jd Tc',
                '   8h 8c 2s 7h 4c',
                '?? Ts8d4d',
                '?? 7c',
                '?? 6d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 320000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 480000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 800000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 960000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1540000, 3380000, 3290000, 790000, 2000000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_9_00_23_52(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((3380000, 3290000, 790000, 2000000, 1540000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   ?? Ah ?? ?? Js',
                '   ?? 4h ?? ?? Jc',
                '?? Qh7sTh',
                '?? As',
                '?? 5s',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 360000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 680000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1160000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3340000, 3810000, 790000, 2000000, 1060000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_10_00_26_43(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((3810000, 790000, 2000000, 1060000, 3340000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Td 9s Kc Qs Tc',
                '   7c 3h 4c Qd 9d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 280000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3770000, 710000, 2000000, 1180000, 3340000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_11_00_27_27(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((710000, 2000000, 1180000, 3340000, 3770000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   7s Jh Qc Kc Ac',
                '   5h 3c 8h 5s 9s',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 280000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [670000, 1920000, 1180000, 3340000, 3890000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_12_00_28_26(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((1920000, 1180000, 3340000, 3890000, 670000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Ah 9d ?? 2s 6h',
                '   Js 9c ?? 2h 4h',
                '?? 8d3d6d',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.fold()
        state.complete_bet_or_raise_to()
        state.fold()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 960000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1040000)

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [1600000, 1820000, 3340000, 3570000, 670000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_13_00_31_44(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((1820000, 3340000, 3570000, 670000, 1600000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   Jh ?? ?? ?? Qd',
                '   Jd ?? ?? ?? 9d',
                '?? 4s2s7h',
                '?? 9s',
                '?? 6c',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

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
        self.assertEqual(state.total_pot_amount, 560000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 720000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1040000)

        # River

        state.burn_card()
        state.deal_board()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1360000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [2540000, 3260000, 3570000, 670000, 960000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())

    def test_14_00_34_31(self) -> None:
        game = FixedLimitTexasHoldem(
            (),
            True,
            0,
            (40000, 80000),
            80000,
            160000,
        )
        state = game((3260000, 3570000, 670000, 960000, 2540000), 5)
        state.deck_cards = deque(
            Card.parse(
                '   5d Ah As Qh Qc',
                '   2c 8c 7s 2h 3s',
                '?? TdAd2s',
                '?? Js',
                '?? 6h',
            ),
        )

        state.post_blind_or_straddle()
        state.post_blind_or_straddle()
        self.assertEqual(state.total_pot_amount, 120000)

        # Pre-flop

        for _ in range(state.player_count * 2):
            state.deal_hole()

        state.complete_bet_or_raise_to()
        state.fold()
        state.fold()
        state.fold()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 360000)

        # Flop

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 360000)

        # Turn

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.collect_bets()
        self.assertEqual(state.total_pot_amount, 1000000)

        # River

        state.burn_card()
        state.deal_board()
        state.check_or_call()
        state.check_or_call()
        self.assertEqual(state.total_pot_amount, 1000000)

        # Showdown

        state.show_or_muck_hole_cards()
        state.show_or_muck_hole_cards()

        state.push_chips()
        state.pull_chips()
        self.assertEqual(state.total_pot_amount, 0)
        self.assertEqual(
            state.stacks,
            [3220000, 4090000, 190000, 960000, 2540000],
        )

        hh = HandHistory.from_game_state(game, state)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )

        new_hh = HandHistory.loads(hh.dumps())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            self.filter_hole_dealing(new_state.operations),
            self.filter_hole_dealing(state.operations),
        )
        self.assertEqual(hh.dumps(), new_hh.dumps())


if __name__ == '__main__':
    main()  # pragma: no cover
