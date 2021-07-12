from unittest import TestCase, main

from pokertools import Card, parse_cards
from pokertools._utilities import distinct, prod, rotate


class UtilitiesTestCase(TestCase):
    def test_distinct(self):
        self.assertTrue(distinct(()))
        self.assertTrue(distinct(parse_cards('AhAsJsQh')))
        self.assertFalse(distinct(parse_cards('AhAsJsQhAh')))
        self.assertTrue(distinct(map(Card.rank.fget, parse_cards('AhJsQh'))))
        self.assertFalse(distinct(map(Card.rank.fget, parse_cards('AhAsJsQh'))))
        self.assertTrue(distinct(map(Card.suit.fget, parse_cards('AcAdJhQs'))))
        self.assertFalse(distinct(map(Card.suit.fget, parse_cards('AcAdJhQh'))))

    def test_rotate(self):
        self.assertEqual(rotate(list(range(10)), 5), list(range(5, 10)) + list(range(5)))
        self.assertEqual(rotate([1, 3, 5, 7], 0), [1, 3, 5, 7])
        self.assertEqual(rotate((1, 3, 5, 7), 1), (3, 5, 7, 1))
        self.assertEqual(rotate((1, 3, 5, 7), -2), (5, 7, 1, 3))

    def test_prod(self):
        self.assertEqual(prod(()), 1)
        self.assertEqual(prod((3,)), 3)
        self.assertEqual(prod((3, 5, 7)), 105)
        self.assertEqual(prod(range(1, 5)), 24)


if __name__ == '__main__':
    main()
