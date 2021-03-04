from unittest import TestCase, main

from auxiliary import window

from pokertools import StandardEvaluator, parse_cards


class HandTestCase(TestCase):
    def test_data(self) -> None:
        hand = StandardEvaluator.hand

        with open('standard-hands.txt') as hands_file:
            hands = (hand(parse_cards(line.rstrip()), ()) for line in hands_file.readlines())

            for h1, h2 in window(hands, 2):
                self.assertLessEqual(h1, h2)


if __name__ == '__main__':
    main()
