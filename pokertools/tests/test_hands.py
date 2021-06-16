from os.path import exists
from unittest import TestCase, main, skipUnless

from pokertools import Lowball27Hand, LowballA5Hand, StandardHand, parse_cards


class HandTestCase(TestCase):
    @skipUnless(exists('standard-hands.txt'), 'The standard hand file does not exist')
    def test_standard_data(self):
        with open('standard-hands.txt') as hands_file:
            hands = tuple(StandardHand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertLessEqual(h1, h2)

    @skipUnless(exists('lowballA5-hands.txt'), 'The lowballA5 hand file does not exist')
    def test_lowballA5_data(self):
        with open('lowballA5-hands.txt') as hands_file:
            hands = tuple(LowballA5Hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertGreater(h1, h2)

    @skipUnless(exists('lowball27-hands.txt'), 'The lowball27 hand file does not exist')
    def test_lowball27_data(self):
        with open('lowball27-hands.txt') as hands_file:
            hands = tuple(Lowball27Hand(parse_cards(line.rstrip())) for line in hands_file.readlines())

            for h1, h2 in zip(hands, hands[1:]):
                self.assertGreater(h1, h2)


if __name__ == '__main__':
    main()
