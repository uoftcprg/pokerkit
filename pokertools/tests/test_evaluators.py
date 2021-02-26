from unittest import TestCase, main

from pokertools import GreekEvaluator, OmahaEvaluator, ShortEvaluator, StandardEvaluator, parse_cards
from pokertools.evaluators import RankEvaluator


class EvaluatorTestCase(TestCase):
    def test_standard(self) -> None:
        hand = StandardEvaluator.hand

        self.assertRaises(ValueError, hand, (), ())
        self.assertLess(hand(parse_cards('AcAd'), parse_cards('AhAsKcKdKh')),
                        hand(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))
        self.assertGreater(hand(parse_cards('AcAd'), parse_cards('AhAsKcKd')),
                           hand(parse_cards('AcKs'), parse_cards('AhAsQsJs')))
        self.assertGreater(hand(parse_cards('AcAd'), parse_cards('AhAsKc')),
                           hand(parse_cards('AcKs'), parse_cards('AhAsQs')))
        self.assertEqual(hand(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                         hand(parse_cards('AsKs'), parse_cards('QdJdTh2s2s')))

    def test_greek(self) -> None:
        hand = GreekEvaluator.hand

        self.assertLess(hand(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                        hand(parse_cards('AsKs'), parse_cards('QdJdTh2s2d')))

    def test_omaha(self) -> None:
        hand = OmahaEvaluator.hand

        self.assertLess(hand(parse_cards('6c7c8c9c'), parse_cards('8s9sTc')),
                        hand(parse_cards('6c7c8s9s'), parse_cards('8c9cTc')))
        self.assertLess(hand(parse_cards('6c7c8c9c'), parse_cards('8s9sTc2sKs')),
                        hand(parse_cards('6c7c8s9s'), parse_cards('8c9cTc2sKs')))

    def test_short(self) -> None:
        hand = ShortEvaluator.hand

        self.assertRaises(ValueError, hand, parse_cards('As2s'), parse_cards('AhAsKcKdKh'))
        self.assertLess(hand(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                        hand(parse_cards('Ac6c'), parse_cards('AhAsKcJcTc')))
        self.assertLess(hand(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                        hand(parse_cards('Ac9d'), parse_cards('6s7s8c')))

    def test_rank(self) -> None:
        hand = RankEvaluator.hand

        self.assertGreater(hand(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                           hand(parse_cards('9c6c'), parse_cards('9h9sKcJcTc')))
        self.assertEqual(hand(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                         hand(parse_cards('Ac9d'), parse_cards('6s7s8c')))


if __name__ == '__main__':
    main()
