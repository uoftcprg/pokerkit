from unittest import TestCase, main

from gameframe.exceptions import GameFrameError

from pokertools import NoLimitTexasHoldEm, Stakes


class GameFrameTestCase(TestCase):
    def test_betting_action_when_not_betting_stage(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).parse, 'cc')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 2', 'br 4', 'cc'
        ).parse, 'br 100')

        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).parse, 'cc')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'br 2', 'br 4', 'br 6', 'cc', 'cc', 'cc',
        ).parse, 'br 8')

    def test_fold_when_redundant(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'br 6', 'f', 'f', 'cc',
            'db AcAsKc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc',
        ).parse, 'f')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc',
        ).parse, 'f')

    def test_bet_raise_when_covered(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'br 199',
        ).parse, 'br 100')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 50', 'br 193',
        ).parse, 'br 93')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'br 195',
        ).parse, 'br 95')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 93',
        ).parse, 'br 93')

        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 299', 'cc', 'cc',
        ).parse, 'br 99')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'f', 'f', 'cc', 'cc',
            'db AcAsKc', 'br 197',
        ).parse, 'br 50')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'cc', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'br 197', 'cc', 'cc',
        ).parse, 'br 197')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd', 'br 6', 'cc', 'cc', 'cc',
            'db AcAsKc', 'cc', 'cc', 'cc', 'cc',
            'db Qs', 'cc', 'cc', 'cc', 'cc',
            'db Qc', 'cc', 'cc', 'br 293',
        ).parse, 'br 193')

    def test_bet_raise_when_irrelevant(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 99',
        ).parse, 'br 197')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'br 93',
        ).parse, 'br 193')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'br 95',
        ).parse, 'br 195')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 93',
        ).parse, 'br 193')

        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'br 99', 'cc',
            'br 199',
            'cc',
        ).parse, 'br 299')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'br 6', 'f', 'cc',
            'db AcAsKc',
            'br 93',
        ).parse, 'br 193')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc',
            'db Qs',
            'br 197', 'cc',
        ).parse, 'br 297')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'f', 'f', 'cc',
            'db AcAsKc',
            'br 10', 'cc',
            'db Qs',
            'br 10', 'br 20', 'cc',
            'db Qc',
            'br 67',
        ).parse, 'br 267')

    def test_bet_raise_with_invalid_amount(self):
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6',
        ).parse, 'br 9')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6',
        ).parse, 'br 1000')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'br 12', 'br 24',
        ).parse, 'br 30')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'br 4', 'cc',
            'db AcAsKc',
            'br 4', 'cc',
            'db Qs',
            'br 4', 'br 8',
        ).parse, 'br 10')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
        ).parse, 'br 1')

        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'cc', 'br 98', 'br 99',
        ).parse, 'br 100')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'br 2', 'br 4', 'br 6', 'br 8', 'cc',
        ).parse, 'br 9')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'br 96', 'br 97',
        ).parse, 'br 98')
        self.assertRaises(GameFrameError, NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'f', 'f', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'br 50',
        ).parse, 'br 55')

    def test_showdown_opener(self):
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'br 6', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'br 4', 'cc',
            'db Qc',
            'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100)).parse(
            'dh 0 QdQh', 'dh 1 AhAd',
            'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc',
            'db Qs',
            'cc', 'cc',
            'db Qc',
            'cc', 'br 6', 'br 12', 'cc',
        ).actor.index, 0)

        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'br 2', 'cc', 'cc', 'cc',
            'db Qc',
            'cc', 'cc', 'cc', 'cc',
        ).actor.index, 0)
        self.assertEqual(NoLimitTexasHoldEm(Stakes(1, (1, 2)), (200, 100, 300, 200)).parse(
            'dh 0 QdQh', 'dh 1 AhAd', 'dh 2 KsKh', 'dh 3 JsJd',
            'cc', 'cc', 'cc', 'cc',
            'db AcAsKc',
            'cc', 'cc', 'cc', 'cc',
            'db Qs',
            'cc', 'cc', 'cc', 'cc',
            'db Qc',
            'br 6', 'br 12', 'br 150', 'cc', 'cc', 'cc',
        ).actor.index, 2)


if __name__ == '__main__':
    main()
