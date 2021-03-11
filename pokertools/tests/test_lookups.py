from unittest import TestCase, main

from pokertools import BadugiHand, LB27Hand, LBA5Hand, ShortHand, StdHand


class LookupTestCase(TestCase):
    def test_std(self) -> None:
        self.assertEqual(StdHand._lookup.index_count, 7462)

    def test_short(self) -> None:
        self.assertEqual(ShortHand._lookup.index_count, 1404)

    def test_badugi(self) -> None:
        self.assertEqual(BadugiHand._lookup.index_count, 1093)

    def test_lbA5(self) -> None:
        self.assertEqual(LBA5Hand._lookup.index_count, 6175)

    def test_lb27(self) -> None:
        self.assertEqual(LB27Hand._lookup.index_count, 7462)


if __name__ == '__main__':
    main()
