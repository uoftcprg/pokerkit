""":mod:`pokerkit.tests.test_notation` implements unit tests for
notation related tools on PokerKit.
"""

from tomllib import loads
from unittest import TestCase, main
from warnings import resetwarnings, simplefilter

from pokerkit.games import (
    FixedLimitTexasHoldem,
    NoLimitTexasHoldem,
)
from pokerkit.notation import HandHistory
from pokerkit.state import Automation


class HandHistoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        simplefilter('ignore')

    @classmethod
    def tearDownClass(cls) -> None:
        resetwarnings()

    def test_user_fields(self) -> None:
        game = FixedLimitTexasHoldem(
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
        )
        state = game(200, 5)

        state.deal_hole('????')
        state.deal_hole('????')
        state.deal_hole('????')
        state.deal_hole('????')
        state.deal_hole('????')
        state.fold()
        state.fold()
        state.fold()
        state.fold()

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)
        hh.user_defined_fields['key'] = 'value'
        hh.user_defined_fields['_key'] = '_value'

        self.assertEqual(loads(hh.dumps()).get('key'), 'value')
        self.assertEqual(loads(hh.dumps()).get('_key'), '_value')

        hh = HandHistory.loads(hh.dumps())

        self.assertEqual(hh.user_defined_fields.get('key'), 'value')
        self.assertEqual(hh.user_defined_fields.get('_key'), '_value')
        self.assertEqual(loads(hh.dumps()).get('key'), 'value')
        self.assertEqual(loads(hh.dumps()).get('_key'), '_value')

    def test_to_acpc_protocol_full(self) -> None:
        game: FixedLimitTexasHoldem | NoLimitTexasHoldem = (
            FixedLimitTexasHoldem(
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
                (50, 100),
                100,
                200,
            )
        )
        state = game(20000, 2)

        state.deal_hole('TdAs')
        state.deal_hole('????')
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('2c8c3h')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('9c')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Kh')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.show_or_muck_hole_cards('8hTc')
        state.show_or_muck_hole_cards('TdAs')

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            [
                ('S->', 'MATCHSTATE:0:0::TdAs|\r\n'),
                ('S->', 'MATCHSTATE:0:0:r:TdAs|\r\n'),
                ('<-C', 'MATCHSTATE:0:0:r:TdAs|:r\r\n'),
                ('S->', 'MATCHSTATE:0:0:rr:TdAs|\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/:TdAs|/2c8c3h\r\n'),
                ('<-C', 'MATCHSTATE:0:0:rrc/:TdAs|/2c8c3h:r\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/r:TdAs|/2c8c3h\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/:TdAs|/2c8c3h/9c\r\n'),
                ('<-C', 'MATCHSTATE:0:0:rrc/rc/:TdAs|/2c8c3h/9c:c\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/c:TdAs|/2c8c3h/9c\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/cr:TdAs|/2c8c3h/9c\r\n'),
                ('<-C', 'MATCHSTATE:0:0:rrc/rc/cr:TdAs|/2c8c3h/9c:c\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/:TdAs|/2c8c3h/9c/Kh\r\n'),
                ('<-C', 'MATCHSTATE:0:0:rrc/rc/crc/:TdAs|/2c8c3h/9c/Kh:c\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/c:TdAs|/2c8c3h/9c/Kh\r\n'),
                ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/cr:TdAs|/2c8c3h/9c/Kh\r\n'),
                (
                    '<-C',
                    'MATCHSTATE:0:0:rrc/rc/crc/cr:TdAs|/2c8c3h/9c/Kh:c\r\n',
                ),
                (
                    'S->',
                    'MATCHSTATE:0:0:rrc/rc/crc/crc:TdAs|8hTc/2c8c3h/9c/Kh\r\n',
                ),
            ],
        )

        game = FixedLimitTexasHoldem(
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
            (50, 100),
            100,
            200,
        )
        state = game(20000, 2)

        state.deal_hole('????')
        state.deal_hole('Qd7c')
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('2h8h5c')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Th')
        state.complete_bet_or_raise_to()
        state.fold()

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(1, 1)),
            [
                ('S->', 'MATCHSTATE:1:1::|Qd7c\r\n'),
                ('<-C', 'MATCHSTATE:1:1::|Qd7c:r\r\n'),
                ('S->', 'MATCHSTATE:1:1:r:|Qd7c\r\n'),
                ('S->', 'MATCHSTATE:1:1:rr:|Qd7c\r\n'),
                ('<-C', 'MATCHSTATE:1:1:rr:|Qd7c:c\r\n'),
                ('S->', 'MATCHSTATE:1:1:rrc/:|Qd7c/2h8h5c\r\n'),
                ('S->', 'MATCHSTATE:1:1:rrc/r:|Qd7c/2h8h5c\r\n'),
                ('<-C', 'MATCHSTATE:1:1:rrc/r:|Qd7c/2h8h5c:c\r\n'),
                ('S->', 'MATCHSTATE:1:1:rrc/rc/:|Qd7c/2h8h5c/Th\r\n'),
                ('S->', 'MATCHSTATE:1:1:rrc/rc/r:|Qd7c/2h8h5c/Th\r\n'),
                ('<-C', 'MATCHSTATE:1:1:rrc/rc/r:|Qd7c/2h8h5c/Th:f\r\n'),
                ('S->', 'MATCHSTATE:1:1:rrc/rc/rf:|Qd7c/2h8h5c/Th\r\n'),
            ],
        )

        game = FixedLimitTexasHoldem(
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
            (50, 100),
            100,
            200,
        )
        state = game(20000, 2)

        state.deal_hole('9d7s')
        state.deal_hole('????')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('5d2cJc')
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('3d')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 2)),
            [
                ('S->', 'MATCHSTATE:0:2::9d7s|\r\n'),
                ('S->', 'MATCHSTATE:0:2:r:9d7s|\r\n'),
                ('<-C', 'MATCHSTATE:0:2:r:9d7s|:c\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/:9d7s|/5d2cJc\r\n'),
                ('<-C', 'MATCHSTATE:0:2:rc/:9d7s|/5d2cJc:c\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/c:9d7s|/5d2cJc\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/cc/:9d7s|/5d2cJc/3d\r\n'),
                ('<-C', 'MATCHSTATE:0:2:rc/cc/:9d7s|/5d2cJc/3d:c\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/cc/c:9d7s|/5d2cJc/3d\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/cc/cr:9d7s|/5d2cJc/3d\r\n'),
                ('<-C', 'MATCHSTATE:0:2:rc/cc/cr:9d7s|/5d2cJc/3d:f\r\n'),
                ('S->', 'MATCHSTATE:0:2:rc/cc/crf:9d7s|/5d2cJc/3d\r\n'),
            ],
        )

        game = NoLimitTexasHoldem(
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
            (50, 100),
            100,
        )
        state = game(20000, 2)

        state.deal_hole('9s8h')
        state.deal_hole('????')
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('8c8d5c')
        state.complete_bet_or_raise_to(150)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('6s')
        state.complete_bet_or_raise_to(250)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('2d')
        state.complete_bet_or_raise_to(750)
        state.check_or_call()
        state.show_or_muck_hole_cards('9s8h')
        state.show_or_muck_hole_cards('9c6h')

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 30)),
            [
                ('S->', 'MATCHSTATE:0:30::9s8h|\r\n'),
                ('S->', 'MATCHSTATE:0:30:c:9s8h|\r\n'),
                ('<-C', 'MATCHSTATE:0:30:c:9s8h|:c\r\n'),
                ('S->', 'MATCHSTATE:0:30:cc/:9s8h|/8c8d5c\r\n'),
                ('<-C', 'MATCHSTATE:0:30:cc/:9s8h|/8c8d5c:r250\r\n'),
                ('S->', 'MATCHSTATE:0:30:cc/r250:9s8h|/8c8d5c\r\n'),
                ('S->', 'MATCHSTATE:0:30:cc/r250c/:9s8h|/8c8d5c/6s\r\n'),
                ('<-C', 'MATCHSTATE:0:30:cc/r250c/:9s8h|/8c8d5c/6s:r500\r\n'),
                ('S->', 'MATCHSTATE:0:30:cc/r250c/r500:9s8h|/8c8d5c/6s\r\n'),
                (
                    'S->',
                    'MATCHSTATE:0:30:cc/r250c/r500c/:9s8h|/8c8d5c/6s/2d\r\n',
                ),
                (
                    '<-C',
                    (
                        'MATCHSTATE'
                        ':0'
                        ':30'
                        ':cc/r250c/r500c/'
                        ':9s8h|/8c8d5c/6s/2d:r1250'
                        '\r\n'
                    ),
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':0'
                        ':30'
                        ':cc/r250c/r500c/r1250'
                        ':9s8h|/8c8d5c/6s/2d'
                        '\r\n'
                    ),
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':0'
                        ':30'
                        ':cc/r250c/r500c/r1250c'
                        ':9s8h|9c6h/8c8d5c/6s/2d'
                        '\r\n'
                    ),
                ),
            ],
        )

        game = NoLimitTexasHoldem(
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
            (50, 100),
            100,
        )
        state = game(20000, 2)

        state.deal_hole('????')
        state.deal_hole('JdTc')
        state.complete_bet_or_raise_to(300)
        state.complete_bet_or_raise_to(900)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('6dJc9c')
        state.complete_bet_or_raise_to(900)
        state.complete_bet_or_raise_to(2700)
        state.complete_bet_or_raise_to(8100)
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Kh')
        state.complete_bet_or_raise_to(11000)
        state.check_or_call()
        state.show_or_muck_hole_cards('KsJs')
        state.show_or_muck_hole_cards('JdTc')
        state.burn_card('??')
        state.deal_board('Qc')

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(1, 31)),
            [
                ('S->', 'MATCHSTATE:1:31::|JdTc\r\n'),
                ('<-C', 'MATCHSTATE:1:31::|JdTc:r300\r\n'),
                ('S->', 'MATCHSTATE:1:31:r300:|JdTc\r\n'),
                ('S->', 'MATCHSTATE:1:31:r300r900:|JdTc\r\n'),
                ('<-C', 'MATCHSTATE:1:31:r300r900:|JdTc:c\r\n'),
                ('S->', 'MATCHSTATE:1:31:r300r900c/:|JdTc/6dJc9c\r\n'),
                ('S->', 'MATCHSTATE:1:31:r300r900c/r1800:|JdTc/6dJc9c\r\n'),
                (
                    '<-C',
                    'MATCHSTATE:1:31:r300r900c/r1800:|JdTc/6dJc9c:r3600\r\n',
                ),
                (
                    'S->',
                    'MATCHSTATE:1:31:r300r900c/r1800r3600:|JdTc/6dJc9c\r\n',
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000'
                        ':|JdTc/6dJc9c'
                        '\r\n'
                    ),
                ),
                (
                    '<-C',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000'
                        ':|JdTc/6dJc9c:c'
                        '\r\n'
                    ),
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000c/'
                        ':|JdTc/6dJc9c/Kh'
                        '\r\n'
                    ),
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000c/r20000'
                        ':|JdTc/6dJc9c/Kh'
                        '\r\n'
                    ),
                ),
                (
                    '<-C',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000c/r20000'
                        ':|JdTc/6dJc9c/Kh:c'
                        '\r\n'
                    ),
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':1'
                        ':31'
                        ':r300r900c/r1800r3600r9000c/r20000c/'
                        ':KsJs|JdTc/6dJc9c/Kh/Qc'
                        '\r\n'
                    ),
                ),
            ],
        )

        game = FixedLimitTexasHoldem(
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
            (50, 100),
            100,
            200,
        )
        state = game(20000, 3)

        state.deal_hole('????')
        state.deal_hole('????')
        state.deal_hole('AsTs')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('4cJh8h')
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Kd')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('8c')
        state.complete_bet_or_raise_to()
        state.fold()

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(2, 55)),
            [
                ('S->', 'MATCHSTATE:2:55::||AsTs\r\n'),
                ('<-C', 'MATCHSTATE:2:55::||AsTs:r\r\n'),
                ('S->', 'MATCHSTATE:2:55:r:||AsTs\r\n'),
                ('S->', 'MATCHSTATE:2:55:rc:||AsTs\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/:||AsTs/4cJh8h\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/r:||AsTs/4cJh8h\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/rf:||AsTs/4cJh8h\r\n'),
                ('<-C', 'MATCHSTATE:2:55:rcc/rf:||AsTs/4cJh8h:c\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/rfc/:||AsTs/4cJh8h/Kd\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/rfc/r:||AsTs/4cJh8h/Kd\r\n'),
                ('<-C', 'MATCHSTATE:2:55:rcc/rfc/r:||AsTs/4cJh8h/Kd:c\r\n'),
                ('S->', 'MATCHSTATE:2:55:rcc/rfc/rc/:||AsTs/4cJh8h/Kd/8c\r\n'),
                (
                    'S->',
                    'MATCHSTATE:2:55:rcc/rfc/rc/r:||AsTs/4cJh8h/Kd/8c\r\n',
                ),
                (
                    '<-C',
                    'MATCHSTATE:2:55:rcc/rfc/rc/r:||AsTs/4cJh8h/Kd/8c:f\r\n',
                ),
                (
                    'S->',
                    'MATCHSTATE:2:55:rcc/rfc/rc/rf:||AsTs/4cJh8h/Kd/8c\r\n',
                ),
            ],
        )

        game = FixedLimitTexasHoldem(
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
            (50, 100),
            100,
            200,
        )
        state = game(20000, 3)

        state.deal_hole('Ad6h')
        state.deal_hole('????')
        state.deal_hole('????')
        state.check_or_call()
        state.complete_bet_or_raise_to()
        state.fold()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('TsKd7h')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Kh')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('6d')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.show_or_muck_hole_cards('Ad6h')
        state.show_or_muck_hole_cards('Td2h')

        self.assertFalse(state.status)

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 90)),
            [
                ('S->', 'MATCHSTATE:0:90::Ad6h||\r\n'),
                ('S->', 'MATCHSTATE:0:90:c:Ad6h||\r\n'),
                ('<-C', 'MATCHSTATE:0:90:c:Ad6h||:r\r\n'),
                ('S->', 'MATCHSTATE:0:90:cr:Ad6h||\r\n'),
                ('S->', 'MATCHSTATE:0:90:crf:Ad6h||\r\n'),
                ('S->', 'MATCHSTATE:0:90:crfc/:Ad6h||/TsKd7h\r\n'),
                ('<-C', 'MATCHSTATE:0:90:crfc/:Ad6h||/TsKd7h:r\r\n'),
                ('S->', 'MATCHSTATE:0:90:crfc/r:Ad6h||/TsKd7h\r\n'),
                ('S->', 'MATCHSTATE:0:90:crfc/rc/:Ad6h||/TsKd7h/Kh\r\n'),
                ('<-C', 'MATCHSTATE:0:90:crfc/rc/:Ad6h||/TsKd7h/Kh:r\r\n'),
                ('S->', 'MATCHSTATE:0:90:crfc/rc/r:Ad6h||/TsKd7h/Kh\r\n'),
                ('S->', 'MATCHSTATE:0:90:crfc/rc/rc/:Ad6h||/TsKd7h/Kh/6d\r\n'),
                (
                    '<-C',
                    'MATCHSTATE:0:90:crfc/rc/rc/:Ad6h||/TsKd7h/Kh/6d:r\r\n',
                ),
                (
                    'S->',
                    'MATCHSTATE:0:90:crfc/rc/rc/r:Ad6h||/TsKd7h/Kh/6d\r\n',
                ),
                (
                    'S->',
                    (
                        'MATCHSTATE'
                        ':0'
                        ':90'
                        ':crfc/rc/rc/rc'
                        ':Ad6h||Td2h/TsKd7h/Kh/6d'
                        '\r\n'
                    ),
                ),
            ],
        )

    def test_to_acpc_protocol_partial(self) -> None:
        interactions = [
            ('S->', 'MATCHSTATE:0:0::TdAs|\r\n'),
            ('S->', 'MATCHSTATE:0:0:r:TdAs|\r\n'),
            ('<-C', 'MATCHSTATE:0:0:r:TdAs|:r\r\n'),
            ('S->', 'MATCHSTATE:0:0:rr:TdAs|\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/:TdAs|/2c8c3h\r\n'),
            ('<-C', 'MATCHSTATE:0:0:rrc/:TdAs|/2c8c3h:r\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/r:TdAs|/2c8c3h\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/:TdAs|/2c8c3h/9c\r\n'),
            ('<-C', 'MATCHSTATE:0:0:rrc/rc/:TdAs|/2c8c3h/9c:c\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/c:TdAs|/2c8c3h/9c\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/cr:TdAs|/2c8c3h/9c\r\n'),
            ('<-C', 'MATCHSTATE:0:0:rrc/rc/cr:TdAs|/2c8c3h/9c:c\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/:TdAs|/2c8c3h/9c/Kh\r\n'),
            ('<-C', 'MATCHSTATE:0:0:rrc/rc/crc/:TdAs|/2c8c3h/9c/Kh:c\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/c:TdAs|/2c8c3h/9c/Kh\r\n'),
            ('S->', 'MATCHSTATE:0:0:rrc/rc/crc/cr:TdAs|/2c8c3h/9c/Kh\r\n'),
            ('<-C', 'MATCHSTATE:0:0:rrc/rc/crc/cr:TdAs|/2c8c3h/9c/Kh:c\r\n'),
            (
                'S->',
                'MATCHSTATE:0:0:rrc/rc/crc/crc:TdAs|8hTc/2c8c3h/9c/Kh\r\n',
            ),
        ]
        game = FixedLimitTexasHoldem(
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
            (50, 100),
            100,
            200,
        )
        state = game(20000, 2)

        state.deal_hole('TdAs')
        state.deal_hole('????')
        state.complete_bet_or_raise_to()
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('2c8c3h')
        state.complete_bet_or_raise_to()
        state.check_or_call()
        state.burn_card('??')
        state.deal_board('9c')
        state.check_or_call()
        state.complete_bet_or_raise_to()

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            interactions[:-7],
        )

        state.check_or_call()
        state.burn_card('??')
        state.deal_board('Kh')

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            interactions[:-5],
        )

        state.check_or_call()

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            interactions[:-3],
        )

        state.complete_bet_or_raise_to()

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            interactions[:-2],
        )

        state.check_or_call()
        state.show_or_muck_hole_cards('8hTc')
        state.show_or_muck_hole_cards('TdAs')

        hh = HandHistory.from_game_state(game, state)

        self.assertEqual(
            list(hh.to_acpc_protocol(0, 0)),
            interactions,
        )


if __name__ == '__main__':
    main()  # pragma: no cover
