from unittest import TestCase, main

from pokertools import ShortDeck, StdDeck


class DeckTestCase(TestCase):
    def test_deck(self) -> None:
        self.assertEqual(len(StdDeck()), 52)

    def test_short_deck(self) -> None:
        self.assertEqual(len(ShortDeck()), 36)


if __name__ == '__main__':
    main()
