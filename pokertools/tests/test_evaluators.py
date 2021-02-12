from unittest import TestCase, main

from pokertools import StandardEvaluator, GreekEvaluator, OmahaEvaluator, parse_card


class EvaluatorTestCase(TestCase):
    def test_standard(self) -> None:
        evaluator = StandardEvaluator()

        self.assertLess(evaluator.hand(['Ac', 'Ad'], ['Ah', 'As', 'Kc', 'Kd', 'Kh']),
                        evaluator.hand(['Ac', 'Ks'], ['Ah', 'As', 'Qs', 'Js', 'Ts']))
        self.assertGreater(evaluator.hand(['Ac', 'Ad'], ['Ah', 'As', 'Kc', 'Kd']),
                           evaluator.hand(['Ac', 'Ks'], ['Ah', 'As', 'Qs', 'Js']))
        self.assertGreater(evaluator.hand(['Ac', 'Ad'], ['Ah', 'As', 'Kc']),
                           evaluator.hand(['Ac', 'Ks'], ['Ah', 'As', 'Qs']))
        self.assertEqual(evaluator.hand([parse_card('Ac'), '2d'], [parse_card('Qd'), 'Jd', 'Th', '2s', 'Ks']),
                         evaluator.hand([parse_card('As'), 'Ks'], [parse_card('Qd'), 'Jd', 'Th', '2s', '2s']))

    def test_greek(self) -> None:
        evaluator = GreekEvaluator()

        self.assertLess(evaluator.hand([parse_card('Ac'), '2d'], [parse_card('Qd'), 'Jd', 'Th', '2s', 'Ks']),
                        evaluator.hand([parse_card('As'), 'Ks'], [parse_card('Qd'), 'Jd', 'Th', '2s', '2d']))

    def test_omaha(self) -> None:
        evaluator = OmahaEvaluator()

        self.assertLess(evaluator.hand(['6c', '7c', '8c', '9c'], ['8s', '9s', 'Tc']),
                        evaluator.hand(['6c', '7c', '8s', '9s'], ['8c', '9c', 'Tc']))
        self.assertLess(evaluator.hand(['6c', '7c', '8c', '9c'], ['8s', '9s', 'Tc', '2s', 'Ks']),
                        evaluator.hand(['6c', '7c', '8s', '9s'], ['8c', '9c', 'Tc', '2s', 'Ks']))


if __name__ == '__main__':
    main()
