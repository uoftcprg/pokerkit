from functools import partial
from itertools import product, starmap
from unittest import TestCase, main

from auxiliary import reverse_args

from pokerface import (
    Card, HoleCard, Rank, Ranks, ShortDeck, StandardDeck, Suit, parse_card,
    parse_cards, rainbow, suited,
)


class CardTestCase(TestCase):
    def test_lt(self):
        self.assertSequenceEqual(
            tuple(map(str, sorted(StandardDeck()))), tuple(map(str, starmap(
                reverse_args(Card), product(Suit, Ranks.STANDARD.value),
            ))),
        )
        self.assertSequenceEqual(
            tuple(map(str, sorted(ShortDeck()))), tuple(map(str, starmap(
                reverse_args(Card), product(Suit, Ranks.SHORT_DECK.value),
            ))),
        )

    def test_card(self):
        self.assertEqual(repr(Card(Rank.TWO, Suit.CLUB)), '2c')
        self.assertEqual(str(Card(Rank.TWO, Suit.CLUB)), '2c')

        self.assertEqual(repr(Card(Rank.ACE, Suit.SPADE)), 'As')
        self.assertEqual(str(Card(Rank.ACE, Suit.SPADE)), 'As')

        self.assertEqual(repr(Card(Rank.ACE, None)), 'A?')
        self.assertEqual(str(Card(Rank.ACE, None)), 'A?')
        self.assertEqual(repr(Card(None, Suit.SPADE)), '?s')
        self.assertEqual(str(Card(None, Suit.SPADE)), '?s')
        self.assertEqual(repr(Card(None, None)), '??')
        self.assertEqual(str(Card(None, None)), '??')

    def test_hole_card(self):
        self.assertEqual(repr(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(str(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(
            repr(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '2c',
        )
        self.assertEqual(
            str(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '??',
        )

        self.assertEqual(
            repr(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As',
        )
        self.assertEqual(str(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(
            repr(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), 'As',
        )
        self.assertEqual(
            str(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), '??',
        )

        self.assertEqual(repr(HoleCard(True, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(repr(HoleCard(True, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(repr(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(repr(HoleCard(False, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(repr(HoleCard(False, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(repr(HoleCard(False, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(True, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(str(HoleCard(True, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(str(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(False, Card(None, Suit.SPADE))), '??')
        self.assertEqual(str(HoleCard(False, Card(Rank.ACE, None))), '??')
        self.assertEqual(str(HoleCard(False, Card(None, None))), '??')

    def test_show(self):
        hole_card = HoleCard(False, parse_card('2c'))

        self.assertEqual(hole_card, hole_card.show())
        self.assertNotEqual(hole_card.status, hole_card.show().status)

    def test_parse_cards(self):
        self.assertCountEqual(
            parse_cards('AcAdAhAs'), map(partial(Card, Rank.ACE), Suit),
        )
        self.assertCountEqual(parse_cards('Kh???sJhA?????2c'), (
            Card(Rank.KING, Suit.HEART), Card(None, None),
            Card(None, Suit.SPADE), Card(Rank.JACK, Suit.HEART),
            Card(Rank.ACE, None), Card(None, None), Card(None, None),
            Card(Rank.TWO, Suit.CLUB),
        ))

    def test_parse_card(self):
        self.assertEqual(parse_card('Ah'), Card(Rank.ACE, Suit.HEART))
        self.assertEqual(parse_card('Kd'), Card(Rank.KING, Suit.DIAMOND))
        self.assertEqual(parse_card('?h'), Card(None, Suit.HEART))
        self.assertEqual(parse_card('A?'), Card(Rank.ACE, None))
        self.assertEqual(parse_card('??'), Card(None, None))

    def test_rainbow(self):
        self.assertTrue(rainbow(()))
        self.assertTrue(rainbow(parse_cards('Ac')))
        self.assertTrue(rainbow(parse_cards('AhJsQc')))
        self.assertTrue(rainbow(parse_cards('AhAsJdQc')))
        self.assertFalse(rainbow(parse_cards('AhAsJsQhAh')))
        self.assertFalse(rainbow(parse_cards('AhAsJsQh')))

    def test_suited(self):
        self.assertTrue(suited(()))
        self.assertTrue(suited((parse_card('Ah'),)))
        self.assertTrue(suited(parse_cards('AhKhQhJhTh')))
        self.assertFalse(suited(parse_cards('AhKhQhJhTs')))
        self.assertFalse(suited(parse_cards('AsKc')))
        self.assertFalse(suited(parse_cards('AsKcQdJhTs')))


if __name__ == '__main__':
    main()
