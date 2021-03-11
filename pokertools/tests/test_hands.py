from unittest import TestCase, main, skip

from auxiliary import windowed

from pokertools import LBA5Evaluator, StdEvaluator, LB27Evaluator, parse_cards


class HandTestCase(TestCase):
    @skip('')
    def test_std_data(self) -> None:
        with open('std-hands.txt') as hands_file:
            hands = (StdEvaluator.hand(parse_cards(line.rstrip()), ()) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertLessEqual(h1, h2)

    def test_lbA5_data(self) -> None:
        with open('lbA5-hands.txt') as hands_file:
            hands = tuple(LBA5Evaluator.hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertGreater(h1, h2)

    def test_lb27_data(self) -> None:
        with open('lb27-hands.txt') as hands_file:
            hands = (LB27Evaluator.hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in windowed(hands, 2):
                self.assertGreater(h1, h2)


if __name__ == '__main__':
    main()
