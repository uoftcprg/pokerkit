from unittest import TestCase, main

from gameframe.exceptions import GameFrameError

from pokertools import NoLimitTexasHoldEm, Stakes


class GameFrameTestCase(TestCase):
    def test_betting_action_when_not_betting_stage(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 2', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'cc',
        ).parse, 'cc')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 2', 'br 4', 'cc'
        ).parse, 'br 100')

    def test_fold_when_redundant(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'cc',
            'db AcAsKc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc',
        ).parse, 'f')

    def test_bet_raise_when_covered(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'br 199',
        ).parse, 'br 100')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'br 50', 'br 193',
        ).parse, 'br 93')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'br 195',
        ).parse, 'br 95')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'br 93',
        ).parse, 'br 93')

    def test_bet_raise_when_irrelevant(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 99',
        ).parse, 'br 197')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'br 93',
        ).parse, 'br 193')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'br 95',
        ).parse, 'br 195')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc', 'cc', 'br 93',
        ).parse, 'br 193')

    def test_bet_raise_with_invalid_amount(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6',
        ).parse, 'br 9')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6',
        ).parse, 'br 1000')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'br 12', 'br 24',
        ).parse, 'br 30')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'cc', 'br 4', 'cc',
            'db AcAsKc', 'br 4', 'cc',
            'db Qs', 'br 4', 'br 8',
        ).parse, 'br 10')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'br 6', 'cc',
            'db AcAsKc', 'cc', 'cc',
            'db Qs', 'cc', 'cc',
            'db Qc',
        ).parse, 'br 1')


if __name__ == '__main__':
    main()
