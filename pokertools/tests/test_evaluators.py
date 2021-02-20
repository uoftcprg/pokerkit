from unittest import TestCase, main

from pokertools import GreekEvaluator, OmahaEvaluator, StandardEvaluator, parse_card
from pokertools._utils import window


class EvaluatorTestCase(TestCase):
    def test_standard(self) -> None:
        evaluator = StandardEvaluator()

        self.assertRaises(ValueError, lambda: evaluator.hand([], []))
        self.assertLess(evaluator.hand(map(parse_card, ['Ac', 'Ad']), map(parse_card, ['Ah', 'As', 'Kc', 'Kd', 'Kh'])),
                        evaluator.hand(map(parse_card, ['Ac', 'Ks']), map(parse_card, ['Ah', 'As', 'Qs', 'Js', 'Ts'])))
        self.assertGreater(evaluator.hand(map(parse_card, ['Ac', 'Ad']), map(parse_card, ['Ah', 'As', 'Kc', 'Kd'])),
                           evaluator.hand(map(parse_card, ['Ac', 'Ks']), map(parse_card, ['Ah', 'As', 'Qs', 'Js'])))
        self.assertGreater(evaluator.hand(map(parse_card, ['Ac', 'Ad']), map(parse_card, ['Ah', 'As', 'Kc'])),
                           evaluator.hand(map(parse_card, ['Ac', 'Ks']), map(parse_card, ['Ah', 'As', 'Qs'])))
        self.assertEqual(evaluator.hand(map(parse_card, ['Ac', '2d']), map(parse_card, ['Qd', 'Jd', 'Th', '2s', 'Ks'])),
                         evaluator.hand(map(parse_card, ['As', 'Ks']), map(parse_card, ['Qd', 'Jd', 'Th', '2s', '2s'])))

    def test_greek(self) -> None:
        evaluator = GreekEvaluator()

        self.assertLess(evaluator.hand(map(parse_card, ['Ac', '2d']), map(parse_card, ['Qd', 'Jd', 'Th', '2s', 'Ks'])),
                        evaluator.hand(map(parse_card, ['As', 'Ks']), map(parse_card, ['Qd', 'Jd', 'Th', '2s', '2d'])))

    def test_omaha(self) -> None:
        evaluator = OmahaEvaluator()

        self.assertLess(evaluator.hand(map(parse_card, ['6c', '7c', '8c', '9c']), map(parse_card, ['8s', '9s', 'Tc'])),
                        evaluator.hand(map(parse_card, ['6c', '7c', '8s', '9s']), map(parse_card, ['8c', '9c', 'Tc'])))
        self.assertLess(evaluator.hand(map(parse_card, ['6c', '7c', '8c', '9c']),
                                       map(parse_card, ['8s', '9s', 'Tc', '2s', 'Ks'])),
                        evaluator.hand(map(parse_card, ['6c', '7c', '8s', '9s']),
                                       map(parse_card, ['8c', '9c', 'Tc', '2s', 'Ks'])))

    def test_data(self) -> None:
        evaluator = StandardEvaluator()

        with open('hands.txt', 'r') as file:
            hands = [evaluator.hand(map(parse_card, line.split()), []) for line in file.readlines()]

            for h1, h2 in window(hands, 2):
                self.assertLessEqual(h1, h2)


if __name__ == '__main__':
    main()
