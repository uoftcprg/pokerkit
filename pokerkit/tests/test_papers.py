""":mod:`pokerkit.tests.test_papers` implements unit tests for
papers and documentations on PokerKit.
"""

from textwrap import dedent
from unittest import TestCase, main
from warnings import resetwarnings, simplefilter

from pokerkit.notation import HandHistory


class Kim2023TestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        simplefilter('ignore')

    @classmethod
    def tearDownClass(cls) -> None:
        resetwarnings()

    def test_figure_1(self) -> None:
        from pokerkit import (
            Automation as A,
            BettingStructure,
            Deck,
            KuhnPokerHand,
            Opening,
            State,
            Street,
        )

        state = State(  # noqa: F841
            # Automations,
            (
                A.ANTE_POSTING,
                A.BET_COLLECTION,
                A.BLIND_OR_STRADDLE_POSTING,
                A.CARD_BURNING,
                A.HOLE_DEALING,
                A.BOARD_DEALING,
                A.HOLE_CARDS_SHOWING_OR_MUCKING,
                A.HAND_KILLING,
                A.CHIPS_PUSHING,
                A.CHIPS_PULLING,
            ),
            Deck.KUHN_POKER,  # Deck
            (KuhnPokerHand,),  # Hand types
            # Streets
            (
                Street(
                    False,  # Card burning
                    (False,),  # Hole dealings
                    0,  #  Board dealings  # noqa: E262
                    False,  # Draw cards?
                    Opening.POSITION,  # Opener
                    1,  # Min bet
                    # Max number of completions,
                    # bets, or raises
                    None,
                ),
            ),
            # Betting structure
            BettingStructure.FIXED_LIMIT,
            True,  # Uniform antes?
            (1,) * 2,  # Antes
            (0,) * 2,  # Blinds or straddles
            0,  # Bring-in
            (2,) * 2,  # Starting stacks
            2,  # Number of players
        )

    def test_figure_2(self) -> None:
        from pokerkit import (
            Automation as A,
            NoLimitTexasHoldem,
        )

        state = NoLimitTexasHoldem.create_state(
            # Automations
            (
                A.ANTE_POSTING,
                A.BET_COLLECTION,
                A.BLIND_OR_STRADDLE_POSTING,
                A.CARD_BURNING,
                A.HOLE_CARDS_SHOWING_OR_MUCKING,
                A.HAND_KILLING,
                A.CHIPS_PUSHING,
                A.CHIPS_PULLING,
            ),
            True,  # Uniform antes?
            500,  # Antes
            (1000, 2000),  # Blinds or straddles
            2000,  # Min-bet
            # Starting stacks
            (1125600, 2000000, 553500),
            3,  # Number of players
        )
        # Pre-flop
        state.deal_hole("Ac2d")  # Ivey
        # Antonius (hole cards unknown)
        state.deal_hole("5h7s")
        state.deal_hole("7h6h")  # Dwan
        # Dwan
        state.complete_bet_or_raise_to(7000)
        # Ivey
        state.complete_bet_or_raise_to(23000)
        state.fold()  # Antonius
        state.check_or_call()  # Dwan
        # Flop
        state.deal_board("Jc3d5c")
        # Ivey
        state.complete_bet_or_raise_to(35000)
        state.check_or_call()  # Dwan
        # Turn
        state.deal_board("4h")
        # Ivey
        state.complete_bet_or_raise_to(90000)
        # Dwan
        state.complete_bet_or_raise_to(232600)
        # Ivey
        state.complete_bet_or_raise_to(1067100)
        state.check_or_call()  # Dwan
        # River
        state.deal_board("Jh")
        # Final stacks: 572100, 1997500, 1109500
        # print(state.stacks)

        self.assertEqual(state.stacks, [572100, 1997500, 1109500])

    def test_figure_3(self) -> None:
        from pokerkit import (  # noqa: F401
            Card,
            OmahaHoldemHand,
        )

        h0 = OmahaHoldemHand.from_game(
            "6c7c8c9c",  # Hole cards
            "8s9sTc",  # Board cards
        )
        h1 = OmahaHoldemHand("6c7c8s9sTc")

        # print(h0 == h1)  # True

        self.assertEqual(h0, h1)  # True


class Kim2024TestCase(TestCase):
    def test_dwan_ivey_2009(self) -> None:
        s = dedent(
            '''\
            # The first televised million dollar pot between Tom Dwan and Phil
            # Ivey.
            # Link: https://youtu.be/GnxFohpljqM

            variant = "NT"
            ante_trimming_status = true
            antes = [500, 500, 500]
            blinds_or_straddles = [1000, 2000, 0]
            min_bet = 2000
            starting_stacks = [1125600, 2000000, 553500]
            actions = [
              # Pre-flop

              "d dh p1 Ac2d",  # Ivey
              "d dh p2 ????",  # Antonius
              "d dh p3 7h6h",  # Dwan

              "p3 cbr 7000",  # Dwan
              "p1 cbr 23000",  # Ivey
              "p2 f",  # Antonius
              "p3 cc",  # Dwan

              # Flop

              "d db Jc3d5c",

              "p1 cbr 35000",  # Ivey
              "p3 cc",  # Dwan

              # Turn

              "d db 4h",

              "p1 cbr 90000",  # Ivey
              "p3 cbr 232600",  # Dwan
              "p1 cbr 1067100",  # Ivey
              "p3 cc",  # Dwan

              # Showdown

              "p1 sm Ac2d",  # Ivey
              "p3 sm 7h6h",  # Dwan

              # River

              "d db Jh",
            ]
            author = "Juho Kim"
            event = "Full Tilt Million Dollar Cash Game S4E12"
            year = 2009
            players = ["Phil Ivey", "Patrik Antonius", "Tom Dwan"]
            currency = "USD"
            '''
        )
        hh = HandHistory.loads(s)
        it = iter(hh)
        state = next(it)

        while state.status:
            state = next(it)

        self.assertRaises(StopIteration, next, it)
        self.assertEqual(state.stacks, [572100, 1997500, 1109500])

        s = hh.dumps()
        hh = HandHistory.loads(s)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [572100, 1997500, 1109500])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

        hh = HandHistory.loads(s, automations=())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [572100, 1997500, 1109500])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

    def test_phua_xuan_2019(self) -> None:
        s = dedent(
            '''\
            # An all-in hand between Xuan and Phua.
            # Link: https://youtu.be/QlgCcphLjaQ

            variant = "NS"
            ante_trimming_status = true
            antes = [3000, 3000, 3000, 3000, 3000, 3000]
            blinds_or_straddles = [0, 0, 0, 0, 0, 3000]
            min_bet = 3000
            starting_stacks = [495000, 232000, 362000, 403000, 301000, 204000]
            actions = [
              # Pre-flop

              "d dh p1 Th8h",  # Badziakouski
              "d dh p2 QsJd",  # Zhong
              "d dh p3 QhQd",  # Xuan
              "d dh p4 8d7c",  # Jun
              "d dh p5 KhKs",  # Phua
              "d dh p6 8c7h",  # Koon

              "p1 cc",  # Badziakouski
              "p2 cc",  # Zhong
              "p3 cbr 35000",  # Xuan
              "p4 f",  # Jun
              "p5 cbr 298000",  # Phua
              "p6 f",  # Koon
              "p1 f",  # Badziakouski
              "p2 f",  # Zhong
              "p3 cc",  # Xuan

              # Showdown

              "p5 sm KhKs",  # Phua
              "p3 sm QhQd",  # Xuan

              # Flop

              "d db 9h6cKc",

              # Turn

              "d db Jh",

              # River

              "d db Ts",
            ]
            author = "Juho Kim"
            event = "Triton London 2019"
            address = "5 Hamilton Pl"
            city = "London"
            region = "Greater London"
            postal_code = "W1J 7ED"
            country = "United Kingdom"
            year = 2019
            players = [
              "Mikita Badziakouski",
              "Liu Ming Zhong",
              "Tan Xuan",
              "Wang Jun",
              "Paul Phua",
              "Jason Koon",
            ]
            currency = "GBP"
            '''
        )
        hh = HandHistory.loads(s)
        it = iter(hh)
        state = next(it)

        while state.status:
            state = next(it)

        self.assertRaises(StopIteration, next, it)
        self.assertEqual(
            state.stacks,
            [489000, 226000, 684000, 400000, 0, 198000],
        )

        s = hh.dumps()
        hh = HandHistory.loads(s)
        new_state = tuple(hh)[-1]

        self.assertEqual(
            new_state.stacks,
            [489000, 226000, 684000, 400000, 0, 198000],
        )
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

        hh = HandHistory.loads(s, automations=())
        new_state = tuple(hh)[-1]

        self.assertEqual(
            new_state.stacks,
            [489000, 226000, 684000, 400000, 0, 198000],
        )
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

    def test_antonius_blom_2009(self) -> None:
        s = dedent(
            '''\
            # The largest online poker pot every played between Patrik Antonius
            # and Viktor Blom.
            # Link: https://youtu.be/UMBm66Id2AA

            variant = "PO"
            ante_trimming_status = true
            antes = [0, 0]
            blinds_or_straddles = [500, 1000]
            min_bet = 1000
            starting_stacks = [1259450.25, 678473.5]
            actions = [
              # Pre-flop

              "d dh p1 Ah3sKsKh",  # Antonius
              "d dh p2 6d9s7d8h",  # Blom

              "p2 cbr 3000",  # Blom
              "p1 cbr 9000",  # Antonius
              "p2 cbr 27000",  # Blom
              "p1 cbr 81000",  # Antonius
              "p2 cc",  # Blom

              # Flop

              "d db 4s5c2h",

              "p1 cbr 91000",  # Antonius
              "p2 cbr 435000",  # Blom
              "p1 cbr 779000",  # Antonius
              "p2 cc",  # Blom

              # Showdown

              "p1 sm Ah3sKsKh",  # Antonius
              "p2 sm 6d9s7d8h",  # Blom

              # Turn

              "d db 5h",

              # River

              "d db 9c",
            ]
            author = "Juho Kim"
            month = 11
            year = 2009
            players = ["Patrik Antonius", "Victor Blom"]
            currency = "USD"
            '''
        )
        hh = HandHistory.loads(s)
        it = iter(hh)
        state = next(it)

        while state.status:
            state = next(it)

        self.assertRaises(StopIteration, next, it)
        self.assertEqual(state.stacks, [1937923.75, 0.0])

        s = hh.dumps()
        hh = HandHistory.loads(s)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [1937923.75, 0.0])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

        hh = HandHistory.loads(s, automations=())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [1937923.75, 0.0])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

    def test_arieh_yockey_2019(self) -> None:
        s = dedent(
            '''\
            # A bad beat between Yockey and Arieh.
            # Link: https://youtu.be/pChCqb2FNxY

            variant = "F2L3D"
            ante_trimming_status = true
            antes = [0, 0, 0, 0]
            blinds_or_straddles = [75000, 150000, 0, 0]
            small_bet = 150000
            big_bet = 300000
            starting_stacks = [1180000, 4340000, 5910000, 10765000]
            actions = [
              # Pre-draw

              "d dh p1 7h6c4c3d2c",  # Yockey
              "d dh p2 ??????????",  # Hui
              "d dh p3 ??????????",  # Esposito
              "d dh p4 AsQs6s5c3c",  # Arieh

              "p3 f",  # Esposito
              "p4 cbr 300000",  # Arieh
              "p1 cbr 450000",  # Yockey
              "p2 f",  # Hui
              "p4 cc",  # Arieh

              # First draw

              "p1 sd",  # Yockey
              "p4 sd AsQs",  # Arieh
              "d dh p4 2hQh",  # Arieh

              "p1 cbr 150000",  # Yockey
              "p4 cc",  # Arieh

              # Second draw

              "p1 sd",  # Yockey
              "p4 sd Qh",  # Arieh
              "d dh p4 4d",  # Arieh

              "p1 cbr 300000",  # Yockey
              "p4 cc",  # Arieh

              # Third draw

              "p1 sd",  # Yockey
              "p4 sd 6s",  # Arieh
              "d dh p4 7c",  # Arieh

              "p1 cbr 280000",  # Yockey
              "p4 cc",  # Arieh

              # Showdown

              "p1 sm 7h6c4c3d2c",  # Yockey
              "p4 sm 2h4d7c5c3c",  # Arieh
            ]
            author = "Juho Kim"
            event = """2019 World Series of Poker Event #58: $50,000 Poker \\
            Players Championship | Day 5"""
            city = "Las Vegas"
            region = "Nevada"
            country = "United States of America"
            day = 28
            month = 6
            year = 2019
            players = [
              "Bryce Yockey",
              "Phil Hui",
              "John Esposito",
              "Josh Arieh",
            ]
            '''
        )
        hh = HandHistory.loads(s)
        it = iter(hh)
        state = next(it)

        while state.status:
            state = next(it)

        self.assertRaises(StopIteration, next, it)
        self.assertEqual(state.stacks, [0, 4190000, 5910000, 12095000])

        s = hh.dumps()
        hh = HandHistory.loads(s)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [0, 4190000, 5910000, 12095000])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

        hh = HandHistory.loads(s, automations=())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [0, 4190000, 5910000, 12095000])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

    def test_alice_carol_wikipedia(self) -> None:
        s = dedent(
            '''\
            # An example badugi hand from Wikipedia.
            # Link: https://en.wikipedia.org/wiki/Badugi

            variant = "FB"
            ante_trimming_status = true
            antes = [0, 0, 0, 0]
            blinds_or_straddles = [1, 2, 0, 0]
            small_bet = 2
            big_bet = 4
            starting_stacks = [200, 200, 200, 200]
            actions = [
              # Pre-draw

              "d dh p1 ????????",  # Bob
              "d dh p2 ????????",  # Carol
              "d dh p3 ????????",  # Ted
              "d dh p4 ????????",  # Alice

              "p3 f",  # Ted
              "p4 cc",  # Alice
              "p1 cc",  # Bob
              "p2 cc",  # Carol

              # First draw

              "p1 sd ????",  # Bob
              "p2 sd ????",  # Carol
              "p4 sd ??",  # Alice
              "d dh p1 ????",  # Bob
              "d dh p2 ????",  # Carol
              "d dh p4 ??",  # Alice

              "p1 cc",  # Bob
              "p2 cbr 2",  # Carol
              "p4 cc",  # Alice
              "p1 cc",  # Bob

              # Second draw

              "p1 sd ??",  # Bob
              "p2 sd",  # Carol
              "p4 sd ??",  # Alice
              "d dh p1 ??",  # Bob
              "d dh p4 ??",  # Alice

              "p1 cc",  # Bob
              "p2 cbr 4",  # Carol
              "p4 cbr 8",  # Alice
              "p1 f",  # Bob
              "p2 cc",  # Bob

              # Third draw

              "p2 sd ??",  # Carol
              "p4 sd",  # Alice
              "d dh p2 ??",  # Carol

              "p2 cc",  # Carol
              "p4 cbr 4",  # Alice
              "p2 cc",  # Carol

              # Showdown

              "p4 sm 2s4c6d9h",  # Alice
              "p2 sm 3s5d7c8h",  # Carol
            ]
            author = "Juho Kim"
            players = ["Bob", "Carol", "Ted", "Alice"]
            '''
        )
        hh = HandHistory.loads(s)
        it = iter(hh)
        state = next(it)

        while state.status:
            state = next(it)

        self.assertRaises(StopIteration, next, it)
        self.assertEqual(state.stacks, [196, 220, 200, 184])

        s = hh.dumps()
        hh = HandHistory.loads(s)
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [196, 220, 200, 184])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())

        hh = HandHistory.loads(s, automations=())
        new_state = tuple(hh)[-1]

        self.assertEqual(new_state.stacks, [196, 220, 200, 184])
        self.assertEqual(new_state.operations, state.operations)
        self.assertEqual(s, hh.dumps())


class READMETestCase(TestCase):
    def test_dwan_ivey(self) -> None:
        # The first televised million dollar pot between Tom Dwan and Phil
        # Ivey.
        # Link: https://youtu.be/GnxFohpljqM

        from pokerkit import Automation, NoLimitTexasHoldem

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
            500,
            (1000, 2000),
            2000,
            (1125600, 2000000, 553500),
            3,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('Ac2d')  # Ivey
        state.deal_hole('????')  # Antonius
        state.deal_hole('7h6h')  # Dwan

        state.complete_bet_or_raise_to(7000)  # Dwan
        state.complete_bet_or_raise_to(23000)  # Ivey
        state.fold()  # Antonius
        state.check_or_call()  # Dwan

        # Below shows the flop dealing and actions.

        state.burn_card('??')
        state.deal_board('Jc3d5c')

        state.complete_bet_or_raise_to(35000)  # Ivey
        state.check_or_call()  # Dwan

        # Below shows the turn dealing and actions.

        state.burn_card('??')
        state.deal_board('4h')

        state.complete_bet_or_raise_to(90000)  # Ivey
        state.complete_bet_or_raise_to(232600)  # Dwan
        state.complete_bet_or_raise_to(1067100)  # Ivey
        state.check_or_call()  # Dwan

        # Below shows the river dealing.

        state.burn_card('??')
        state.deal_board('Jh')

        # Below show the final stacks.

        # print(state.stacks)  # [572100, 1997500, 1109500]

        self.assertEqual(state.stacks, [572100, 1997500, 1109500])

    def test_phua_xuan(self) -> None:
        # An all-in hand between Xuan and Phua.
        # Link: https://youtu.be/QlgCcphLjaQ

        from pokerkit import Automation, NoLimitShortDeckHoldem

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
            3000,
            {-1: 3000},
            3000,
            (495000, 232000, 362000, 403000, 301000, 204000),
            6,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('Th8h')  # Badziakouski
        state.deal_hole('QsJd')  # Zhong
        state.deal_hole('QhQd')  # Xuan
        state.deal_hole('8d7c')  # Jun
        state.deal_hole('KhKs')  # Phua
        state.deal_hole('8c7h')  # Koon

        state.check_or_call()  # Badziakouski
        state.check_or_call()  # Zhong
        state.complete_bet_or_raise_to(35000)  # Xuan
        state.fold()  # Jun
        state.complete_bet_or_raise_to(298000)  # Phua
        state.fold()  # Koon
        state.fold()  # Badziakouski
        state.fold()  # Zhong
        state.check_or_call()  # Xuan

        # Below shows the flop dealing.

        state.burn_card('??')
        state.deal_board('9h6cKc')

        # Below shows the turn dealing.

        state.burn_card('??')
        state.deal_board('Jh')

        # Below shows the river dealing.

        state.burn_card('??')
        state.deal_board('Ts')

        # Below show the final stacks.

        # print(state.stacks)  # [489000, 226000, 684000, 400000, 0, 198000]

        self.assertEqual(
            state.stacks,
            [489000, 226000, 684000, 400000, 0, 198000],
        )

    def test_antonius_blom(self) -> None:
        # The largest online poker pot every played between Patrik Antonius and
        # Viktor Blom.
        # Link: https://youtu.be/UMBm66Id2AA

        from pokerkit import Automation, PotLimitOmahaHoldem

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
            (500, 1000),
            2000,
            (1259450.25, 678473.5),  # type: ignore[arg-type]
            2,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('Ah3sKsKh')  # Antonius
        state.deal_hole('6d9s7d8h')  # Blom

        state.complete_bet_or_raise_to(3000)  # Blom
        state.complete_bet_or_raise_to(9000)  # Antonius
        state.complete_bet_or_raise_to(27000)  # Blom
        state.complete_bet_or_raise_to(81000)  # Antonius
        state.check_or_call()  # Blom

        # Below shows the flop dealing and actions.

        state.burn_card('??')
        state.deal_board('4s5c2h')

        state.complete_bet_or_raise_to(91000)  # Antonius
        state.complete_bet_or_raise_to(435000)  # Blom
        state.complete_bet_or_raise_to(779000)  # Antonius
        state.check_or_call()  # Blom

        # Below shows the turn dealing.

        state.burn_card('??')
        state.deal_board('5h')

        # Below shows the river dealing.

        state.burn_card('??')
        state.deal_board('9c')

        # Below show the final stacks.

        # print(state.stacks)  # [1937923.75, 0.0]

        self.assertEqual(state.stacks, [1937923.75, 0.0])

    def test_yockey_arieh(self) -> None:
        # A bad beat between Yockey and Arieh.
        # Link: https://youtu.be/pChCqb2FNxY

        from pokerkit import (
            Automation,
            FixedLimitDeuceToSevenLowballTripleDraw,
        )

        state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
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
            (75000, 150000),
            150000,
            300000,
            (1180000, 4340000, 5910000, 10765000),
            4,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('7h6c4c3d2c')  # Yockey
        state.deal_hole('??????????')  # Hui
        state.deal_hole('??????????')  # Esposito
        state.deal_hole('AsQs6s5c3c')  # Arieh

        state.fold()  # Esposito
        state.complete_bet_or_raise_to()  # Arieh
        state.complete_bet_or_raise_to()  # Yockey
        state.fold()  # Hui
        state.check_or_call()  # Arieh

        # Below shows the first draw and actions.

        state.stand_pat_or_discard()  # Yockey
        state.stand_pat_or_discard('AsQs')  # Arieh
        state.burn_card('??')
        state.deal_hole('2hQh')  # Arieh

        state.complete_bet_or_raise_to()  # Yockey
        state.check_or_call()  # Arieh

        # Below shows the second draw and actions.

        state.stand_pat_or_discard()  # Yockey
        state.stand_pat_or_discard('Qh')  # Arieh
        state.burn_card('??')
        state.deal_hole('4d')  # Arieh

        state.complete_bet_or_raise_to()  # Yockey
        state.check_or_call()  # Arieh

        # Below shows the third draw and actions.

        state.stand_pat_or_discard()  # Yockey
        state.stand_pat_or_discard('6s')  # Arieh
        state.burn_card('??')
        state.deal_hole('7c')  # Arieh

        state.complete_bet_or_raise_to()  # Yockey
        state.check_or_call()  # Arieh

        # Below show the final stacks.

        # print(state.stacks)  # [0, 4190000, 5910000, 12095000]

        self.assertEqual(state.stacks, [0, 4190000, 5910000, 12095000])

    def test_alice_carol(self) -> None:
        # An example badugi hand from Wikipedia.
        # Link: https://en.wikipedia.org/wiki/Badugi

        from pokerkit import Automation, FixedLimitBadugi

        state = FixedLimitBadugi.create_state(
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
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
            4,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('????????')  # Bob
        state.deal_hole('????????')  # Carol
        state.deal_hole('????????')  # Ted
        state.deal_hole('????????')  # Alice

        state.fold()  # Ted
        state.check_or_call()  # Alice
        state.check_or_call()  # Bob
        state.check_or_call()  # Carol

        # Below shows the first draw and actions.

        state.stand_pat_or_discard('????')  # Bob
        state.stand_pat_or_discard('????')  # Carol
        state.stand_pat_or_discard('??')  # Alice
        state.burn_card('??')
        state.deal_hole('????')  # Bob
        state.deal_hole('????')  # Carol
        state.deal_hole('??')  # Alice

        state.check_or_call()  # Bob
        state.complete_bet_or_raise_to()  # Carol
        state.check_or_call()  # Alice
        state.check_or_call()  # Bob

        # Below shows the second draw and actions.

        state.stand_pat_or_discard('??')  # Bob
        state.stand_pat_or_discard()  # Carol
        state.stand_pat_or_discard('??')  # Alice
        state.burn_card('??')
        state.deal_hole('??')  # Bob
        state.deal_hole('??')  # Alice

        state.check_or_call()  # Bob
        state.complete_bet_or_raise_to()  # Carol
        state.complete_bet_or_raise_to()  # Alice
        state.fold()  # Bob
        state.check_or_call()  # Carol

        # Below shows the third draw and actions.

        state.stand_pat_or_discard('??')  # Carol
        state.stand_pat_or_discard()  # Alice
        state.burn_card('??')
        state.deal_hole('??')  # Carol

        state.check_or_call()  # Carol
        state.complete_bet_or_raise_to()  # Alice
        state.check_or_call()  # Carol

        # Below show the showdown.

        state.show_or_muck_hole_cards('2s4c6d9h')  # Alice
        state.show_or_muck_hole_cards('3s5d7c8h')  # Carol

        # Below show the final stacks.

        # print(state.stacks)  # [196, 220, 200, 184]

        self.assertEqual(state.stacks, [196, 220, 200, 184])


if __name__ == '__main__':
    main()  # pragma: no cover
