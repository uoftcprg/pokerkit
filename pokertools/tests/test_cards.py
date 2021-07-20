from functools import partial
from itertools import product, starmap
from unittest import TestCase, main

from auxiliary import reverse_args

from pokertools import (
    Card, HoleCard, Rank, Ranks, ShortDeck, StandardDeck, Suit, parse_card, parse_cards, parse_range, rainbow, suited,
)


class CardTestCase(TestCase):
    def test_lt(self):
        self.assertSequenceEqual(
            tuple(map(str, sorted(StandardDeck()))),
            tuple(map(str, starmap(reverse_args(Card), product(Suit, Ranks.STANDARD.value)))),
        )
        self.assertSequenceEqual(
            tuple(map(str, sorted(ShortDeck()))),
            tuple(map(str, starmap(reverse_args(Card), product(Suit, Ranks.SHORT_DECK.value)))),
        )

    def test_card(self):
        self.assertEqual(repr(Card(Rank.TWO, Suit.CLUB)), '2c')
        self.assertEqual(str(Card(Rank.TWO, Suit.CLUB)), '2c')

        self.assertEqual(repr(Card(Rank.ACE, Suit.SPADE)), 'As')
        self.assertEqual(str(Card(Rank.ACE, Suit.SPADE)), 'As')

        self.assertEqual(repr(Card(Rank.ACE, None)), 'A?')
        self.assertEqual(str(Card(Rank.ACE, None)), 'A?')
        self.assertEqual(repr(Card(None, Suit.SPADE)), '?s')
        self.assertEqual(str(Card(None, Suit.SPADE)), '?s')
        self.assertEqual(repr(Card(None, None)), '??')
        self.assertEqual(str(Card(None, None)), '??')

    def test_hole_card(self):
        self.assertEqual(repr(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(str(HoleCard(True, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(repr(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '2c')
        self.assertEqual(str(HoleCard(False, Card(Rank.TWO, Suit.CLUB))), '??')

        self.assertEqual(repr(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(str(HoleCard(True, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(repr(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), 'As')
        self.assertEqual(str(HoleCard(False, Card(Rank.ACE, Suit.SPADE))), '??')

        self.assertEqual(repr(HoleCard(True, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(repr(HoleCard(True, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(repr(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(repr(HoleCard(False, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(repr(HoleCard(False, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(repr(HoleCard(False, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(True, Card(None, Suit.SPADE))), '?s')
        self.assertEqual(str(HoleCard(True, Card(Rank.ACE, None))), 'A?')
        self.assertEqual(str(HoleCard(True, Card(None, None))), '??')
        self.assertEqual(str(HoleCard(False, Card(None, Suit.SPADE))), '??')
        self.assertEqual(str(HoleCard(False, Card(Rank.ACE, None))), '??')
        self.assertEqual(str(HoleCard(False, Card(None, None))), '??')

    def test_rainbow(self):
        self.assertTrue(rainbow(()))
        self.assertTrue(rainbow(parse_cards('Ac')))
        self.assertTrue(rainbow(parse_cards('AhJsQc')))
        self.assertTrue(rainbow(parse_cards('AhAsJdQc')))
        self.assertFalse(rainbow(parse_cards('AhAsJsQhAh')))
        self.assertFalse(rainbow(parse_cards('AhAsJsQh')))

    def test_suited(self):
        self.assertTrue(suited(()))
        self.assertTrue(suited((parse_card('Ah'),)))
        self.assertTrue(suited(parse_cards('AhKhQhJhTh')))
        self.assertFalse(suited(parse_cards('AhKhQhJhTs')))
        self.assertFalse(suited(parse_cards('AsKc')))
        self.assertFalse(suited(parse_cards('AsKcQdJhTs')))

    def test_parse_card(self):
        self.assertEqual(parse_card('Ah'), Card(Rank.ACE, Suit.HEART))
        self.assertEqual(parse_card('Kd'), Card(Rank.KING, Suit.DIAMOND))
        self.assertEqual(parse_card('?h'), Card(None, Suit.HEART))
        self.assertEqual(parse_card('A?'), Card(Rank.ACE, None))
        self.assertEqual(parse_card('??'), Card(None, None))

    def test_parse_cards(self):
        self.assertCountEqual(parse_cards('AcAdAhAs'), map(partial(Card, Rank.ACE), Suit))
        self.assertCountEqual(parse_cards('Kh???sJhA?????2c'), (
            Card(Rank.KING, Suit.HEART), Card(None, None), Card(None, Suit.SPADE), Card(Rank.JACK, Suit.HEART),
            Card(Rank.ACE, None), Card(None, None), Card(None, None), Card(Rank.TWO, Suit.CLUB),
        ))

    def test_parse_range(self):
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('QTs'))), {
            frozenset({'Qc', 'Tc'}), frozenset({'Qd', 'Td'}), frozenset({'Qh', 'Th'}), frozenset({'Qs', 'Ts'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AKo'))), {
            frozenset({'Ac', 'Kd'}), frozenset({'Ac', 'Kh'}), frozenset({'Ac', 'Ks'}),
            frozenset({'Ad', 'Kc'}), frozenset({'Ad', 'Kh'}), frozenset({'Ad', 'Ks'}),
            frozenset({'Ah', 'Kc'}), frozenset({'Ah', 'Kd'}), frozenset({'Ah', 'Ks'}),
            frozenset({'As', 'Kc'}), frozenset({'As', 'Kd'}), frozenset({'As', 'Kh'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AK'))), {
            frozenset({'Ac', 'Kd'}), frozenset({'Ac', 'Kh'}), frozenset({'Ac', 'Ks'}),
            frozenset({'Ad', 'Kc'}), frozenset({'Ad', 'Kh'}), frozenset({'Ad', 'Ks'}),
            frozenset({'Ah', 'Kc'}), frozenset({'Ah', 'Kd'}), frozenset({'Ah', 'Ks'}),
            frozenset({'As', 'Kc'}), frozenset({'As', 'Kd'}), frozenset({'As', 'Kh'}),
            frozenset({'Ac', 'Kc'}), frozenset({'Ad', 'Kd'}), frozenset({'Ah', 'Kh'}), frozenset({'As', 'Ks'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JJ'))), {
            frozenset({'Jc', 'Jd'}), frozenset({'Jc', 'Jh'}), frozenset({'Jc', 'Js'}),
            frozenset({'Jd', 'Jh'}), frozenset({'Jd', 'Js'}), frozenset({'Jh', 'Js'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('AsKh'))), {
            frozenset({'As', 'Kh'})
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JJ+'))), {
            frozenset({'Jc', 'Jd'}), frozenset({'Jc', 'Jh'}), frozenset({'Jc', 'Js'}),
            frozenset({'Jd', 'Jh'}), frozenset({'Jd', 'Js'}), frozenset({'Jh', 'Js'}),
            frozenset({'Qc', 'Qd'}), frozenset({'Qc', 'Qh'}), frozenset({'Qc', 'Qs'}),
            frozenset({'Qd', 'Qh'}), frozenset({'Qd', 'Qs'}), frozenset({'Qh', 'Qs'}),
            frozenset({'Kc', 'Kd'}), frozenset({'Kc', 'Kh'}), frozenset({'Kc', 'Ks'}),
            frozenset({'Kd', 'Kh'}), frozenset({'Kd', 'Ks'}), frozenset({'Kh', 'Ks'}),
            frozenset({'Ac', 'Ad'}), frozenset({'Ac', 'Ah'}), frozenset({'Ac', 'As'}),
            frozenset({'Ad', 'Ah'}), frozenset({'Ad', 'As'}), frozenset({'Ah', 'As'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('JTo+'))), {
            frozenset({'Jc', 'Td'}), frozenset({'Jc', 'Th'}), frozenset({'Jc', 'Ts'}),
            frozenset({'Jd', 'Tc'}), frozenset({'Jd', 'Th'}), frozenset({'Jd', 'Ts'}),
            frozenset({'Jh', 'Tc'}), frozenset({'Jh', 'Td'}), frozenset({'Jh', 'Ts'}),
            frozenset({'Js', 'Tc'}), frozenset({'Js', 'Td'}), frozenset({'Js', 'Th'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('QT+'))), {
            frozenset({'Qc', 'Td'}), frozenset({'Qc', 'Th'}), frozenset({'Qc', 'Ts'}),
            frozenset({'Qd', 'Tc'}), frozenset({'Qd', 'Th'}), frozenset({'Qd', 'Ts'}),
            frozenset({'Qh', 'Tc'}), frozenset({'Qh', 'Td'}), frozenset({'Qh', 'Ts'}),
            frozenset({'Qs', 'Tc'}), frozenset({'Qs', 'Td'}), frozenset({'Qs', 'Th'}),
            frozenset({'Qc', 'Tc'}), frozenset({'Qd', 'Td'}), frozenset({'Qh', 'Th'}), frozenset({'Qs', 'Ts'}),
            frozenset({'Qc', 'Jd'}), frozenset({'Qc', 'Jh'}), frozenset({'Qc', 'Js'}),
            frozenset({'Qd', 'Jc'}), frozenset({'Qd', 'Jh'}), frozenset({'Qd', 'Js'}),
            frozenset({'Qh', 'Jc'}), frozenset({'Qh', 'Jd'}), frozenset({'Qh', 'Js'}),
            frozenset({'Qs', 'Jc'}), frozenset({'Qs', 'Jd'}), frozenset({'Qs', 'Jh'}),
            frozenset({'Qc', 'Jc'}), frozenset({'Qd', 'Jd'}), frozenset({'Qh', 'Jh'}), frozenset({'Qs', 'Js'}),
        })
        self.assertSetEqual(frozenset(map(lambda cards: frozenset(map(str, cards)), parse_range('9T+'))), set())


if __name__ == '__main__':
    main()
