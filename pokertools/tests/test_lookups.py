from unittest import TestCase, main

from pokertools import BadugiHand, Lowball27Hand, LowballA5Hand, ShortHand, StandardHand


class LookupTestCase(TestCase):
    def test_standard(self):
        self.assertEqual(StandardHand._lookup.index_count, 7462)

    def test_short_deck(self):
        self.assertEqual(ShortHand._lookup.index_count, 1404)

    def test_badugi(self):
        self.assertEqual(BadugiHand._lookup.index_count, 1093)

    def test_lowballA5(self):
        self.assertEqual(LowballA5Hand._lookup.index_count, 6175)

    def test_lowball27(self):
        self.assertEqual(Lowball27Hand._lookup.index_count, 7462)


if __name__ == '__main__':
    main()
