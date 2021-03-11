from unittest import TestCase, main

from pokertools import StdHand, BadugiHand, ShortHand


class LookupTestCase(TestCase):
    def test_std(self) -> None:
        self.assertEqual(StdHand._lookup.index_count, 7462)

    def test_short(self) -> None:
        self.assertEqual(ShortHand._lookup.index_count, 1404)

    def test_badugi(self) -> None:
        self.assertEqual(BadugiHand._lookup.index_count, 1093)


if __name__ == '__main__':
    main()
