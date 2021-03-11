from unittest import TestCase, main

from pokertools import (BadugiEvaluator, GreekEvaluator, OmahaEvaluator, RankEvaluator, ShortEvaluator, StdEvaluator,
                        parse_cards)


class EvaluatorTestCase(TestCase):
    def test_std(self) -> None:
        std = StdEvaluator.hand

        self.assertLess(std(parse_cards('AcAd'), parse_cards('AhAsKcKdKh')),
                        std(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))
        self.assertGreater(std(parse_cards('AcAd'), parse_cards('AhAsKcKd')),
                           std(parse_cards('AcKs'), parse_cards('AhAsQsJs')))
        self.assertGreater(std(parse_cards('AcAd'), parse_cards('AhAsKc')),
                           std(parse_cards('AcKs'), parse_cards('AhAsQs')))
        self.assertEqual(std(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                         std(parse_cards('AsKs'), parse_cards('QdJdTh2s2s')))

    def test_greek(self) -> None:
        greek = GreekEvaluator.hand

        self.assertLess(greek(parse_cards('Ac2d'), parse_cards('QdJdTh2sKs')),
                        greek(parse_cards('AsKs'), parse_cards('QdJdTh2s2d')))

    def test_omaha(self) -> None:
        omaha = OmahaEvaluator.hand

        self.assertLess(omaha(parse_cards('6c7c8c9c'), parse_cards('8s9sTc')),
                        omaha(parse_cards('6c7c8s9s'), parse_cards('8c9cTc')))
        self.assertLess(omaha(parse_cards('6c7c8c9c'), parse_cards('8s9sTc2sKs')),
                        omaha(parse_cards('6c7c8s9s'), parse_cards('8c9cTc2sKs')))

    def test_short(self) -> None:
        short = ShortEvaluator.hand

        self.assertLess(short(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                        short(parse_cards('Ac6c'), parse_cards('AhAsKcJcTc')))
        self.assertLess(short(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                        short(parse_cards('Ac9d'), parse_cards('6s7s8c')))

    def test_badugi(self) -> None:
        badugi = BadugiEvaluator.hand

        self.assertGreater(badugi(parse_cards('2s4c5d6h')), badugi(parse_cards('As2c3d7h')))
        self.assertGreater(badugi(parse_cards('4s5c6dKh')), badugi(parse_cards('2s3s4d7h')))
        self.assertGreater(badugi(parse_cards('As5d9d9h')), badugi(parse_cards('Ac2s2cJd')))
        self.assertGreater(badugi(parse_cards('2s3s4d7h')), badugi(parse_cards('4s5s6dKh')))
        self.assertEqual(badugi(parse_cards('As2c3d3s')), badugi(parse_cards('Ad2hKc3c')))
        self.assertGreater(badugi(parse_cards('5d7cKcKh')), badugi(parse_cards('2s3dKsKd')))

    def test_rank(self) -> None:
        rank = RankEvaluator.hand

        self.assertGreater(rank(parse_cards('AcKs'), parse_cards('AhAsKcJsTs')),
                           rank(parse_cards('9c6c'), parse_cards('9h9sKcJcTc')))
        self.assertEqual(rank(parse_cards('AcAd'), parse_cards('6s6cKcKd')),
                         rank(parse_cards('Ac9d'), parse_cards('6s7s8c')))


if __name__ == '__main__':
    main()
