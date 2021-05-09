from unittest import TestCase, main

from pokertools import (BadugiEvaluator, GreekEvaluator, OmahaEvaluator, RankEvaluator, ShortEvaluator,
                        StandardEvaluator, parse_cards)


class EvaluatorTestCase(TestCase):
    def test_standard(self) -> None:
        self.assertRaises(ValueError, ShortEvaluator.evaluate, (), ())
        self.assertLess(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKdKh')),
                        StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))
        self.assertGreater(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKd')),
                           StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJs')))
        self.assertGreater(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKc')),
                           StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQs')))
        self.assertEqual(StandardEvaluator.evaluate(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                         StandardEvaluator.evaluate(parse_cards('AsKs'), parse_cards('QdJdTh2s2s')))

    def test_greek(self) -> None:
        self.assertLess(GreekEvaluator.evaluate(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                        GreekEvaluator.evaluate(parse_cards('AsKs'), parse_cards('QdJdTh2s2d')))

    def test_omaha(self) -> None:
        self.assertLess(OmahaEvaluator.evaluate(parse_cards('6c7c8c9c'), parse_cards('8s9sTc')),
                        OmahaEvaluator.evaluate(parse_cards('6c7c8s9s'), parse_cards('8c9cTc')))
        self.assertLess(OmahaEvaluator.evaluate(parse_cards('6c7c8c9c'), parse_cards('8s9sTc2sKs')),
                        OmahaEvaluator.evaluate(parse_cards('6c7c8s9s'), parse_cards('8c9cTc2sKs')))

    def test_short(self) -> None:
        self.assertRaises(ValueError, ShortEvaluator.evaluate, parse_cards('AcKs'), parse_cards('4hAsKcJsTs'))
        self.assertLess(ShortEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                        ShortEvaluator.evaluate(parse_cards('Ac6c'), parse_cards('AhAsKcJcTc')))
        self.assertLess(ShortEvaluator.evaluate(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                        ShortEvaluator.evaluate(parse_cards('Ac9d'), parse_cards('6s7s8c')))

    def test_badugi(self) -> None:
        self.assertGreater(BadugiEvaluator.evaluate(parse_cards('2s4c5d6h')),
                           BadugiEvaluator.evaluate(parse_cards('As2c3d7h')))
        self.assertGreater(BadugiEvaluator.evaluate(parse_cards('4s5c6dKh')),
                           BadugiEvaluator.evaluate(parse_cards('2s3s4d7h')))
        self.assertGreater(BadugiEvaluator.evaluate(parse_cards('As5d9d9h')),
                           BadugiEvaluator.evaluate(parse_cards('Ac2s2cJd')))
        self.assertGreater(BadugiEvaluator.evaluate(parse_cards('2s3s4d7h')),
                           BadugiEvaluator.evaluate(parse_cards('4s5s6dKh')))
        self.assertEqual(BadugiEvaluator.evaluate(parse_cards('As2c3d3s')),
                         BadugiEvaluator.evaluate(parse_cards('Ad2hKc3c')))
        self.assertGreater(BadugiEvaluator.evaluate(parse_cards('5d7cKcKh')),
                           BadugiEvaluator.evaluate(parse_cards('2s3dKsKd')))

    def test_rank(self) -> None:
        self.assertGreater(RankEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                           RankEvaluator.evaluate(parse_cards('9c6c'), parse_cards('9h9sKcJcTc')))
        self.assertEqual(RankEvaluator.evaluate(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                         RankEvaluator.evaluate(parse_cards('Ac9d'), parse_cards('6s7s8c')))


if __name__ == '__main__':
    main()
