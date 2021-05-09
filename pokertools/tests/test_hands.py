from unittest import TestCase, main

from auxiliary import windowed

from pokertools import Lowball27Evaluator, LowballA5Evaluator, StandardEvaluator, parse_cards


class HandTestCase(TestCase):
    def test_standard_data(self) -> None:
        with open('standard-hands.txt') as hands_file:
            hands = (StandardEvaluator.evaluate(parse_cards(line.rstrip()), ()) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertLessEqual(h1, h2)

    def test_lowballA5_data(self) -> None:
        with open('lowballA5-hands.txt') as hands_file:
            hands = (LowballA5Evaluator.evaluate(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertGreater(h1, h2)

    def test_lowball27_data(self) -> None:
        with open('lowball27-hands.txt') as hands_file:
            hands = (Lowball27Evaluator.evaluate(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertGreater(h1, h2)


if __name__ == '__main__':
    main()
