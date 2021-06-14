from unittest import TestCase, main

from pokertools import Lowball27Evaluator, LowballA5Evaluator, StandardEvaluator, parse_cards


class HandTestCase(TestCase):
    def test_standard_data(self):
        with open('standard-hands.txt') as hands_file:
            hands = tuple(StandardEvaluator.hand(parse_cards(line.rstrip()), ()) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertLessEqual(h1, h2)

    def test_lowballA5_data(self):
        with open('lowballA5-hands.txt') as hands_file:
            hands = tuple(LowballA5Evaluator.hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertGreater(h1, h2)

    def test_lowball27_data(self):
        with open('lowball27-hands.txt') as hands_file:
            hands = tuple(Lowball27Evaluator.hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertGreater(h1, h2)


if __name__ == '__main__':
    main()
