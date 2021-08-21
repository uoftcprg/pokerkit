from unittest import TestCase, main

from pokerface import Stakes


class StakesTestCase(TestCase):
    def test_bets(self):
        self.assertEqual(Stakes(0, (1, 2)).small_bet, 2)
        self.assertEqual(Stakes(0, (1, 2)).big_bet, 4)
        self.assertEqual(Stakes(1, ()).small_bet, 1)
        self.assertEqual(Stakes(1, ()).big_bet, 2)
        self.assertEqual(Stakes(0, (1, 2, 0, 2, 2)).small_bet, 2)
        self.assertEqual(Stakes(0, (1, 2, 0, 2, 2)).big_bet, 4)
        self.assertEqual(Stakes(5, (1, 2, 0, 2, 2)).small_bet, 5)
        self.assertEqual(Stakes(5, (1, 2, 0, 2, 2)).big_bet, 10)
        self.assertEqual(
            Stakes(5, (1, 2, 0, 2, 2), small_bet=10).small_bet, 10,
        )
        self.assertEqual(Stakes(5, (1, 2, 0, 2, 2), small_bet=10).big_bet, 20)
        self.assertEqual(
            Stakes(5, (1, 2, 0, 2, 2), small_bet=10, big_bet=25).big_bet, 25,
        )

    def test_verify(self):
        self.assertRaises(ValueError, Stakes, 0, ())
        self.assertRaises(ValueError, Stakes, -1, (1, 2))
        self.assertRaises(ValueError, Stakes, 1, (-1, 2))
        self.assertRaises(ValueError, Stakes, -1, (-1, 2))
        self.assertRaises(ValueError, Stakes, 0, (1, 2, 0, 1))
        self.assertRaises(ValueError, Stakes, 0, (1, 1, 0, 2, 1))
        self.assertRaises(ValueError, Stakes, 0, (1, 2, 2, 2, 1))


if __name__ == '__main__':
    main()
