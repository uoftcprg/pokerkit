from unittest import TestCase, main

from pokerface import Deck, ShortDeck, StandardDeck, parse_card, parse_cards


class DeckTestCase(TestCase):
    def test_deck(self):
        self.assertEqual(len(Deck()), 0)

    def test_standard_deck(self):
        self.assertCountEqual(StandardDeck(), parse_cards(
            '2c3c4c5c6c7c8c9cTcJcQcKcAc'
            '2d3d4d5d6d7d8d9dTdJdQdKdAd'
            '2h3h4h5h6h7h8h9hThJhQhKhAh'
            '2s3s4s5s6s7s8s9sTsJsQsKsAs'
        ))

    def test_short_deck(self):
        self.assertCountEqual(ShortDeck(), parse_cards(
            '6c7c8c9cTcJcQcKcAc'
            '6d7d8d9dTdJdQdKdAd'
            '6h7h8h9hThJhQhKhAh'
            '6s7s8s9sTsJsQsKsAs'
        ))

    def test_draw(self):
        deck = StandardDeck()

        self.assertEqual(len(deck), 52)
        self.assertIn(parse_card('4h'), deck)
        self.assertEqual(deck.draw(parse_cards('4h4c4s')), tuple(parse_cards(
            '4h4c4s'
        )))
        self.assertEqual(len(deck), 49)
        self.assertNotIn(parse_card('4h'), deck)
        self.assertEqual(len(deck.draw(1)), 1)
        self.assertEqual(len(deck), 48)
        self.assertRaises(ValueError, deck.draw, 49)


if __name__ == '__main__':
    main()
