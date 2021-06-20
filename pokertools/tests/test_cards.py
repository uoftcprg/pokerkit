from unittest import TestCase, main

from pokertools import Card, HoleCard, Rank, Suit


class CardTestCase(TestCase):
    def test_cards(self):
        self.assertEqual(repr(Card(Rank.TWO, Suit.CLUB)), '2c')
        self.assertEqual(str(Card(Rank.TWO, Suit.CLUB)), '2c')

        self.assertEqual(repr(Card(Rank.ACE, Suit.SPADE)), 'As')
        self.assertEqual(str(Card(Rank.ACE, Suit.SPADE)), 'As')

        self.assertEqual(repr(Card(None, None)), '??')
        self.assertEqual(str(Card(None, None)), '??')

    def test_hole_cards(self):
        self.assertEqual(repr(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(str(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(repr(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(str(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '??')

        self.assertEqual(repr(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(str(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(repr(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(str(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), '??')

        self.assertEqual(repr(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(repr(HoleCard(False, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(False, Card(None, None))), '??')


if __name__ == '__main__':
    main()
