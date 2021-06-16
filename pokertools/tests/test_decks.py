from unittest import TestCase, main

from pokertools import ShortDeck, StandardDeck, parse_card, parse_cards


class DeckTestCase(TestCase):
    def test_standard(self):
        deck = StandardDeck()

        self.assertEqual(len(deck), 52)
        self.assertIn(parse_card('4h'), deck)

        deck.draw(parse_cards('4h4c4s'))

        self.assertEqual(len(deck), 49)
        self.assertNotIn(parse_card('4h'), deck)

        deck.draw(1)

        self.assertEqual(len(deck), 48)

    def test_short_deck(self):
        self.assertEqual(len(ShortDeck()), 36)


if __name__ == '__main__':
    main()
