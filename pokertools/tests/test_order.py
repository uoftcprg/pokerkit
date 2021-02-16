from unittest import TestCase, main

from pokertools import OmahaEvaluator, Rank, Suit, parse_card


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
        evaluator = OmahaEvaluator()

        self.assertLessEqual(evaluator.hand(map(parse_card, ['6c', '7c', '8c', '9c']),
                                            map(parse_card, ['8s', '9s', 'Tc'])),
                             evaluator.hand(map(parse_card, ['6c', '7c', '8s', '9s']),
                                            map(parse_card, ['8c', '9c', 'Tc'])))


if __name__ == '__main__':
    main()
