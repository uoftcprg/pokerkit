""":mod:`pokerkit.tests.test_notation` implements unit tests for
notation related tools on PokerKit.
"""

from tomllib import loads
from unittest import TestCase, main
from warnings import resetwarnings, simplefilter

from pokerkit.games import FixedLimitBadugi
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
        game = FixedLimitBadugi(
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

        state.deal_hole('????????')
        state.deal_hole('????????')
        state.deal_hole('????????')
        state.deal_hole('????????')
        state.deal_hole('????????')
        state.fold()
        state.fold()
        state.fold()
        state.fold()

        assert not state.status

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


if __name__ == '__main__':
    main()  # pragma: no cover
