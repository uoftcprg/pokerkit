from os.path import exists
from unittest import TestCase, main, skipUnless

from pokertools import BadugiHand, LowballA5Hand, ShortDeckHand, StandardHand, parse_cards


class LookupTestCase(TestCase):
    @skipUnless(exists('lookups/standard-lookup.txt'), 'The standard hand file does not exist')
    def test_standard_lookup(self):
        # Generated with Python treys package: https://pypi.org/project/treys/
        with open('lookups/standard-lookup.txt') as file:
            lines = map(str.strip, file.readlines())

        indices = tuple(map(StandardHand._lookup.get_index, map(parse_cards, lines)))

        for i, j in zip(indices, indices[1:]):
            self.assertLessEqual(i, j)

        self.assertEqual(StandardHand._lookup.index_count, 7462)
        self.assertEqual(min(indices), 0)
        self.assertEqual(max(indices), StandardHand._lookup.index_count - 1)

    @skipUnless(exists('lookups/short-hand-lookup.txt'), 'The short hand file does not exist')
    def test_short_deck_lookup(self):
        # Generated with short-deck package: https://github.com/amason13/shortdeck
        with open('lookups/short-hand-lookup.txt') as file:
            lines = map(str.strip, file.readlines())

        indices = tuple(map(ShortDeckHand._lookup.get_index, map(parse_cards, lines)))

        for i, j in zip(indices, indices[1:]):
            self.assertLessEqual(i, j)

        self.assertEqual(ShortDeckHand._lookup.index_count, 1404)
        self.assertEqual(min(indices), 0)
        self.assertEqual(max(indices), ShortDeckHand._lookup.index_count - 1)

    @skipUnless(exists('lookups/lowballA5-lookup.txt'), 'The lowballA5 hand file does not exist')
    def test_lowballA5_lookup(self):
        # Generated with custom Python code
        with open('lookups/lowballA5-lookup.txt') as file:
            lines = map(str.strip, file.readlines())

        indices = tuple(map(LowballA5Hand._lookup.get_index, map(parse_cards, lines)))

        for i, j in zip(indices, indices[1:]):
            self.assertGreaterEqual(i, j)

        self.assertEqual(LowballA5Hand._lookup.index_count, 6175)
        self.assertEqual(min(indices), 0)
        self.assertEqual(max(indices), LowballA5Hand._lookup.index_count - 1)

    @skipUnless(exists('lookups/badugi-lookup.txt'), 'The badugi hand file does not exist')
    def test_badugi_lookup(self):
        # Generated with custom Python code
        with open('lookups/badugi-lookup.txt') as file:
            lines = map(str.strip, file.readlines())

        indices = tuple(map(BadugiHand._lookup.get_index, map(parse_cards, lines)))

        for i, j in zip(indices, indices[1:]):
            self.assertGreaterEqual(i, j)

        self.assertEqual(BadugiHand._lookup.index_count, 1092)
        self.assertEqual(min(indices), 0)
        self.assertEqual(max(indices), BadugiHand._lookup.index_count - 1)


if __name__ == '__main__':
    main()
