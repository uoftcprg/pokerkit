from unittest import main

from auxiliary import ExtendedTestCase

from pokertools import HoleCard, parse_card, parse_cards, suited


class CardTestCase(ExtendedTestCase):
    def test_cards(self) -> None:
        self.assertEqual(repr(parse_card('4h')), '4h')
        self.assertEqual(str(parse_card('4h')), '4h')
        self.assertIterableEqual(map(str, parse_cards('4h4s4cAs')), ('4h', '4s', '4c', 'As'))

        self.assertTrue(suited(()))
        self.assertFalse(suited(parse_cards('4h4s4cAs')))
        self.assertTrue(suited(parse_cards('4sAs')))

    def test_hole_cards(self) -> None:
        self.assertEqual(repr(HoleCard(True, parse_card('As'))), 'As')
        self.assertEqual(repr(HoleCard(False, parse_card('As'))), '??')


if __name__ == '__main__':
    main()
