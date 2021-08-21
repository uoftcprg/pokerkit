from unittest import TestCase, main

from pokerface import (
    BadugiEvaluator, BadugiHand, GreekEvaluator, LowIndexedHand,
    Lowball27Evaluator, Lowball27Hand, LowballA5Evaluator, LowballA5Hand,
    OmahaEvaluator, Rank, RankEvaluator, ShortDeckEvaluator, ShortDeckHand,
    StandardEvaluator, StandardHand, parse_cards,
)


class EvaluatorTestCase(TestCase):
    def test_standard_evaluator_evaluate_hand(self):
        self.assertRaises(ValueError, StandardEvaluator.evaluate_hand, (), ())
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQdQh'),
        ), StandardHand(parse_cards('AcAdAhAsKc')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJsTs'),
        ), StandardHand(parse_cards('AsKsQsJsTs')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQd'),
        ), StandardHand(parse_cards('AcAdAhAsKc')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJs'),
        ), StandardHand(parse_cards('AcAhAsKsQs')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQs'),
        ), StandardHand(parse_cards('AcAhAsKsQs')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('Ac2d'), parse_cards('QdJdTh2sKs'),
        ), StandardHand(parse_cards('AcKsQdJdTh')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('AsKs'), parse_cards('QsJdTs2c2s'),
        ), StandardHand(parse_cards('AsKsQsTs2s')))
        self.assertEqual(StandardEvaluator.evaluate_hand(
            parse_cards('Ac9c'), parse_cards('AhKhQhJhTh'),
        ), StandardHand(parse_cards('AhKhQhJhTh')))

    def test_greek_evaluator_evaluate_hand(self):
        self.assertEqual(GreekEvaluator.evaluate_hand(
            parse_cards('Ac2d'), parse_cards('QdJdTh2sKs'),
        ), StandardHand(parse_cards('2s2dAcKsQd')))
        self.assertEqual(GreekEvaluator.evaluate_hand(
            parse_cards('AsKs'), parse_cards('QdJdTh2s2d'),
        ), StandardHand(parse_cards('AsKsQdJdTh')))
        self.assertEqual(GreekEvaluator.evaluate_hand(
            parse_cards('Ac9c'), parse_cards('AhKhQhJhTh'),
        ), StandardHand(parse_cards('AcAhKhQh9c')))

    def test_omaha_evaluator_evaluate_hand(self):
        self.assertEqual(OmahaEvaluator.evaluate_hand(
            parse_cards('6c7c8c9c'), parse_cards('8s9sTc'),
        ), StandardHand(parse_cards('6c7c8s9sTc')))
        self.assertEqual(OmahaEvaluator.evaluate_hand(
            parse_cards('6c7c8s9s'), parse_cards('8c9cTc'),
        ), StandardHand(parse_cards('6c7c8c9cTc')))
        self.assertEqual(OmahaEvaluator.evaluate_hand(
            parse_cards('6c7c8c9c'), parse_cards('8s9sTc9hKs'),
        ), StandardHand(parse_cards('8c8s9c9s9h')))
        self.assertEqual(OmahaEvaluator.evaluate_hand(
            parse_cards('6c7c8sAh'), parse_cards('As9cTc2sKs'),
        ), StandardHand(parse_cards('AhAsKsTc8s')))
        self.assertEqual(OmahaEvaluator.evaluate_hand(
            parse_cards('Ac9cKs9s'), parse_cards('AhKhQhJhTh'),
        ), StandardHand(parse_cards('AcKsQhJhTh')))

    def test_short_deck_evaluator_evaluate_hand(self):
        self.assertRaises(
            ValueError, ShortDeckEvaluator.evaluate_hand,
            parse_cards('AcKs'), parse_cards('4hAsKcJsTs'),
        )
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsKcJsTs'),
        ), ShortDeckHand(parse_cards('AcAhAsKcKs')))
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('Ac6s'), parse_cards('AhAsKcJcTc'),
        ), ShortDeckHand(parse_cards('AcAhAsKcJc')))
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('Ac6c'), parse_cards('AhAsKcJcTc'),
        ), ShortDeckHand(parse_cards('AcKcJcTc6c')))
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('6s7cKcKd'),
        ), ShortDeckHand(parse_cards('AcAdKcKd7c')))
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('Ac9d'), parse_cards('6s7s8c'),
        ), ShortDeckHand(parse_cards('Ac9d8c7s6s')))
        self.assertEqual(ShortDeckEvaluator.evaluate_hand(
            parse_cards('Ac9c'), parse_cards('AhKhQhJhTh'),
        ), ShortDeckHand(parse_cards('AhKhQhJhTh')))

    def test_lowball27_evaluator_evaluate_hand(self):
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcAdAhAsKc'), (),
        ), Lowball27Hand(parse_cards('AcAdAhAsKc')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQdQh'),
        ), Lowball27Hand(parse_cards('AhAsKcQdQh')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJsTs'),
        ), Lowball27Hand(parse_cards('AhAsQsJsTs')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQd'),
        ), Lowball27Hand(parse_cards('AcAdAhKcQd')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJs'),
        ), Lowball27Hand(parse_cards('AhAsKsQsJs')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQs'),
        ), Lowball27Hand(parse_cards('AcAhAsKsQs')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('Ac2d'), parse_cards('QdJdTh2sKs'),
        ), Lowball27Hand(parse_cards('KsQdJdTh2s')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('AsKs'), parse_cards('QsJdTs2c2s'),
        ), Lowball27Hand(parse_cards('KsQsJdTs2c')))
        self.assertEqual(Lowball27Evaluator.evaluate_hand(
            parse_cards('Ac9c'), parse_cards('AhKhQhJhTh'),
        ), Lowball27Hand(parse_cards('AcQhJhTh9c')))

    def test_lowballA5_evaluator_evaluate_hand(self):
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQdQh'),
        ), LowballA5Hand(parse_cards('AcAsQdQhKc')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJsTs'),
        ), LowballA5Hand(parse_cards('KsAsQsJsTs')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AcAd'), parse_cards('AhAsKcQd'),
        ), LowballA5Hand(parse_cards('AdAhAsKcQd')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQsJs'),
        ), LowballA5Hand(parse_cards('AhAsKsQsJs')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsQs'),
        ), LowballA5Hand(parse_cards('AcAhAsKsQs')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('Ac2d'), parse_cards('QdJdTh2sKs'),
        ), LowballA5Hand(parse_cards('AcQdJdTh2d')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('AsKs'), parse_cards('QsJsTs2c2s'),
        ), LowballA5Hand(parse_cards('AsQsJsTs2s')))
        self.assertEqual(LowballA5Evaluator.evaluate_hand(
            parse_cards('Ac9c'), parse_cards('AhKhQhJhTh'),
        ), LowballA5Hand(parse_cards('AhQhJhTh9c')))

    def test_badugi_evaluator_evaluate_hand(self):
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('2s4c5d6h'), (),
        ), BadugiHand(parse_cards('2s4c5d6h')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('As2d3d7h'), (),
        ), BadugiHand(parse_cards('As2d7h')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('4s4c4dKh'), (),
        ), BadugiHand(parse_cards('4sKh')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('2s3s4d7h'), (),
        ), BadugiHand(parse_cards('2s4d7h')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('As2d3s4h'), (),
        ), BadugiHand(parse_cards('As2d4h')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('KcKdKhKs'), (),
        ), BadugiHand(parse_cards('Ks')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('2s2c4d4h'), (),
        ), BadugiHand(parse_cards('2s4d')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('4s5s6dKh'), (),
        ), BadugiHand(parse_cards('4s6dKh')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('As2c3d3s'), (),
        ), BadugiHand(parse_cards('As2c3d')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('Ad2hKc3c'), (),
        ), BadugiHand(parse_cards('Ad2h3c')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('5d7cKcKh'), (),
        ), BadugiHand(parse_cards('5d7cKh')))
        self.assertEqual(BadugiEvaluator.evaluate_hand(
            parse_cards('2s3dKsKd'), (),
        ), BadugiHand(parse_cards('2s3d')))

    def test_rank_evaluator_evaluate_hand(self):
        self.assertEqual(RankEvaluator.evaluate_hand(
            parse_cards('AcKs'), parse_cards('AhAsKcJsTs'),
        ), LowIndexedHand(Rank.ACE.index))
        self.assertEqual(RankEvaluator.evaluate_hand(
            parse_cards('9c6c'), parse_cards('9h9sKcJcTc'),
        ), LowIndexedHand(Rank.KING.index))
        self.assertEqual(RankEvaluator.evaluate_hand(
            parse_cards('Tc2d'), (),
        ), LowIndexedHand(Rank.TEN.index))
        self.assertEqual(RankEvaluator.evaluate_hand(
            parse_cards('3c'), (),
        ), LowIndexedHand(Rank.THREE.index))


if __name__ == '__main__':
    main()
