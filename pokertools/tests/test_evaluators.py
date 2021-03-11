from unittest import TestCase, main

from pokertools import (BadugiEvaluator, GreekEvaluator, OmahaEvaluator, RankEvaluator, ShortEvaluator, StdEvaluator,
                        parse_cards)


class EvaluatorTestCase(TestCase):
    def test_std(self) -> None:
        self.assertRaises(ValueError, ShortEvaluator.hand, (), ())
        self.assertLess(StdEvaluator.hand(parse_cards('AcAd'), parse_cards('AhAsKcKdKh')),
                        StdEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))
        self.assertGreater(StdEvaluator.hand(parse_cards('AcAd'), parse_cards('AhAsKcKd')),
                           StdEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsQsJs')))
        self.assertGreater(StdEvaluator.hand(parse_cards('AcAd'), parse_cards('AhAsKc')),
                           StdEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsQs')))
        self.assertEqual(StdEvaluator.hand(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                         StdEvaluator.hand(parse_cards('AsKs'), parse_cards('QdJdTh2s2s')))

    def test_greek(self) -> None:
        self.assertLess(GreekEvaluator.hand(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                        GreekEvaluator.hand(parse_cards('AsKs'), parse_cards('QdJdTh2s2d')))

    def test_omaha(self) -> None:
        self.assertLess(OmahaEvaluator.hand(parse_cards('6c7c8c9c'), parse_cards('8s9sTc')),
                        OmahaEvaluator.hand(parse_cards('6c7c8s9s'), parse_cards('8c9cTc')))
        self.assertLess(OmahaEvaluator.hand(parse_cards('6c7c8c9c'), parse_cards('8s9sTc2sKs')),
                        OmahaEvaluator.hand(parse_cards('6c7c8s9s'), parse_cards('8c9cTc2sKs')))

    def test_short(self) -> None:
        self.assertRaises(ValueError, ShortEvaluator.hand, parse_cards('AcKs'), parse_cards('4hAsKcJsTs'))
        self.assertLess(ShortEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                        ShortEvaluator.hand(parse_cards('Ac6c'), parse_cards('AhAsKcJcTc')))
        self.assertLess(ShortEvaluator.hand(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                        ShortEvaluator.hand(parse_cards('Ac9d'), parse_cards('6s7s8c')))

    def test_badugi(self) -> None:
        self.assertGreater(BadugiEvaluator.hand(parse_cards('2s4c5d6h')), BadugiEvaluator.hand(parse_cards('As2c3d7h')))
        self.assertGreater(BadugiEvaluator.hand(parse_cards('4s5c6dKh')), BadugiEvaluator.hand(parse_cards('2s3s4d7h')))
        self.assertGreater(BadugiEvaluator.hand(parse_cards('As5d9d9h')), BadugiEvaluator.hand(parse_cards('Ac2s2cJd')))
        self.assertGreater(BadugiEvaluator.hand(parse_cards('2s3s4d7h')), BadugiEvaluator.hand(parse_cards('4s5s6dKh')))
        self.assertEqual(BadugiEvaluator.hand(parse_cards('As2c3d3s')), BadugiEvaluator.hand(parse_cards('Ad2hKc3c')))
        self.assertGreater(BadugiEvaluator.hand(parse_cards('5d7cKcKh')), BadugiEvaluator.hand(parse_cards('2s3dKsKd')))

    def test_rank(self) -> None:
        self.assertGreater(RankEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                           RankEvaluator.hand(parse_cards('9c6c'), parse_cards('9h9sKcJcTc')))
        self.assertEqual(RankEvaluator.hand(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                         RankEvaluator.hand(parse_cards('Ac9d'), parse_cards('6s7s8c')))


if __name__ == '__main__':
    main()
