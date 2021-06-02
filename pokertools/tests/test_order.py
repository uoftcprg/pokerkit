from unittest import TestCase, main

from pokertools import OmahaEvaluator, Rank, Suit, parse_card, parse_cards


class OrderTestCase(TestCase):
    def test_ranks(self) -> None:
        self.assertLess(Rank.SEVEN, Rank.JACK)
        self.assertLessEqual(Rank.SEVEN, Rank.JACK)
        self.assertGreater(Rank.TEN, Rank.TWO)

    def test_suits(self) -> None:
        self.assertLess(Suit.CLUB, Suit.SPADE)
        self.assertLessEqual(Suit.CLUB, Suit.SPADE)
        self.assertGreater(Suit.HEART, Suit.DIAMOND)

    def test_cards(self) -> None:
        self.assertLess(parse_card('Ah'), parse_card('As'))
        self.assertLessEqual(parse_card('Ah'), parse_card('As'))
        self.assertGreater(parse_card('As'), parse_card('Ah'))
        self.assertGreaterEqual(parse_card('As'), parse_card('Ah'))
        self.assertLess(parse_card('4h'), parse_card('5c'))

    def test_hands(self) -> None:
        self.assertLessEqual(
            OmahaEvaluator.hand(parse_cards('6c7c8c9c'), parse_cards('8s9sTc')),
            OmahaEvaluator.hand(parse_cards('6c7c8s9s'), parse_cards('8c9cTc')),
        )


if __name__ == '__main__':
    main()
