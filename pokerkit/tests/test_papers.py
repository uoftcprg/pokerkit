""":mod:`pokerkit.tests.test_papers` implements unit tests for
papers and documentations on PokerKit.
"""

from unittest import TestCase, main
from warnings import resetwarnings, simplefilter


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

    def test_xuan_phua(self) -> None:
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
            (50000, 100000),
            2000,
            (125945025, 67847350),
            2,
        )

        # Below shows the pre-flop dealings and actions.

        state.deal_hole('Ah3sKsKh')  # Antonius
        state.deal_hole('6d9s7d8h')  # Blom

        state.complete_bet_or_raise_to(300000)  # Blom
        state.complete_bet_or_raise_to(900000)  # Antonius
        state.complete_bet_or_raise_to(2700000)  # Blom
        state.complete_bet_or_raise_to(8100000)  # Antonius
        state.check_or_call()  # Blom

        # Below shows the flop dealing and actions.

        state.burn_card('??')
        state.deal_board('4s5c2h')

        state.complete_bet_or_raise_to(9100000)  # Antonius
        state.complete_bet_or_raise_to(43500000)  # Blom
        state.complete_bet_or_raise_to(77900000)  # Antonius
        state.check_or_call()  # Blom

        # Below shows the turn dealing.

        state.burn_card('??')
        state.deal_board('5h')

        # Below shows the river dealing.

        state.burn_card('??')
        state.deal_board('9c')

        # Below show the final stacks.

        # print(state.stacks)  # [193792375, 0]

        self.assertEqual(state.stacks, [193792375, 0])

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
