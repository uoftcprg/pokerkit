from operator import le
from unittest import TestCase, main

from pokerface import (
    BadugiHand, HighIndexedHand, LowIndexedHand, Lowball27Hand, LowballA5Hand,
    ShortDeckHand, StandardHand, parse_cards,
)


class HandTestCase(TestCase):
    def test_total_ordering(self):
        quad = StandardHand(parse_cards('AcAdAhAsKs'))
        straight_flush = StandardHand(parse_cards('TsJsQsKsAs'))
        wheel = Lowball27Hand(parse_cards('2c3d4h5s7c'))

        self.assertLess(quad, straight_flush)
        self.assertLessEqual(quad, straight_flush)
        self.assertGreater(straight_flush, quad)
        self.assertGreaterEqual(straight_flush, quad)
        self.assertEqual(quad, quad)
        self.assertEqual(straight_flush, straight_flush)
        self.assertNotEqual(quad, straight_flush)
        self.assertNotEqual(straight_flush, wheel)

        self.assertRaises(TypeError, le, quad, wheel)

    def test_high_indexed_hand(self):
        self.assertLessEqual(HighIndexedHand(1), HighIndexedHand(0))

    def test_low_indexed_hand(self):
        self.assertGreaterEqual(LowIndexedHand(1), LowIndexedHand(0))

    def test_standard_hand(self):
        self.assertRaises(ValueError, StandardHand, parse_cards(
            '9sTsJsQsKsAs'
        ))
        self.assertRaises(ValueError, StandardHand, parse_cards(
            '4c5dThJsAcKh2h'
        ))
        self.assertRaises(ValueError, StandardHand, parse_cards(
            'AcAdAhAsAc'
        ))

        hands = tuple(map(StandardHand, map(parse_cards, (
            '6c7d8h9sJc', '4c5d9hJsKc', '4c5dThJsKc', '4c5dThJsAc',
            '4c6dThJsAc', '9cTdJhQsAc', '9cTdJhKsAc', '2c2dThJsQc',
            '3c3dThJsQc', '3c3dThJsKc', '3c3dJhQsKc', '3c3d2hKsAc',
            'AcAd2hJsQc', 'AcAdKhQsJc', '2c2dThTsQc', '3c3dThTsQc',
            '3c3dThTsKc', '3c3dQhQsKc', '2c2dKhKsAc', 'AcAd2h2sQc',
            'AcAdKhKsQc', '2c2d2hTsJc', '3c3d3hTsQc', '3c3d3hTsKc',
            '3c3d3hQsKc', 'KcKdKh2sAc', 'AcAdAh2sQc', 'AcAdAhKsQc',
            'Ac2d3h4s5c', '2c3d4h5s6c', '3c4d5h6s7c', '4c5d6h7s8c',
            '5c6d7h8s9c', '9cTdJhQsKc', 'TcJdQhKsAc', '6c7c8c9cJc',
            '4d5d9dJdKd', '4h5hThJhKh', '4s5sTsJsAs', '4c6cTcJcAc',
            '9dTdJdQdAd', '9sTsJsKsAs', '2c2d2hTsTc', '3c3d3hTsTc',
            '3c3d3hKsKc', '3c3d3hAsAc', 'KcKdKhAsAc', 'AcAdAhQsQc',
            'AcAdAhKsKc', '2c2d2h2s3c', '2c2d2h2sTc', '3c3d3h3sKc',
            '3c3d3h3sAc', 'KcKdKhKsAc', 'AcAdAhAsQc', 'AcAdAhAsKc',
            'Ac2c3c4c5c', '2d3d4d5d6d', '3h4h5h6h7h', '4s5s6s7s8s',
            '5c6c7c8c9c', '9dTdJdQdKd', 'TsJsQsKsAs',
        ))))

        self.assertSequenceEqual(hands, sorted(hands))

    def test_short_deck_hand(self):
        self.assertRaises(ValueError, ShortDeckHand, parse_cards(
            '9sTsJsQsKsAs'
        ))
        self.assertRaises(ValueError, ShortDeckHand, parse_cards(
            '6c7dThJsAcKh8h'
        ))
        self.assertRaises(ValueError, ShortDeckHand, parse_cards(
            'AcAdAhAsAc'
        ))
        self.assertRaises(ValueError, ShortDeckHand, parse_cards(
            'Ac2c3c4c5c'
        ))

        hands = tuple(map(ShortDeckHand, map(parse_cards, (
            '6c7d8h9sJc', '6c7d8h9sQc', '6c7d8h9sKc', '6c7d8hTsAc',
            '6c7d9hTsAc', '6c8d9hTsAc', '9cJdQhKsAc', '6c6dThJsQc',
            '7c7dThJsQc', '7c7dThJsKc', '7c7dJhQsKc', '7c7d6hKsAc',
            'AcAd6hJsQc', 'AcAdKhQsJc', '6c6dThTsQc', '7c7dThTsQc',
            '7c7dThTsKc', '7c7dQhQsKc', '6c6dKhKsAc', 'AcAd6h6sQc',
            'AcAdKhKsQc', '6c6d6hTsJc', '7c7d7hTsQc', '7c7d7hTsKc',
            '7c7d7hQsKc', 'KcKdKh6sAc', 'AcAdAh6sQc', 'AcAdAhKsQc',
            'Ac6d7h8s9c', '6c7d8h9sTc', '7c8d9hTsJc', '8c9dThJsQc',
            '9cTdJhQsKc', 'TcJdQhKsAc', '6c6d6hTsTc', '7c7d7hTsTc',
            '7c7d7hKsKc', '7c7d7hAsAc', 'KcKdKhAsAc', 'AcAdAhQsQc',
            'AcAdAhKsKc', '6c7c8c9cJc', '6d7d9dJdKd', '6h7hThJhKh',
            '6s7sTsJsAs', '6c8cTcJcAc', '9dTdJdQdAd', '9sTsJsKsAs',
            '6c6d6h6s7c', '6c6d6h6sTc', '7c7d7h7sKc', '7c7d7h7sAc',
            'KcKdKhKsAc', 'AcAdAhAsQc', 'AcAdAhAsKc', 'Ac6c7c8c9c',
            '6d7d8d9dTd', '7h8h9hThJh', '8s9sTsJsQs', '9cTcJcQcKc',
            'TdJdQdKdAd',
        ))))

        self.assertSequenceEqual(hands, sorted(hands))

    def test_lowball27_hand(self):
        self.assertRaises(ValueError, Lowball27Hand, parse_cards(
            '9sTsJsQsKsAs'
        ))
        self.assertRaises(ValueError, Lowball27Hand, parse_cards(
            '4c5dThJsAcKh2h'
        ))
        self.assertRaises(ValueError, Lowball27Hand, parse_cards(
            'AcAdAhAsAc'
        ))

        hands = tuple(map(Lowball27Hand, map(parse_cards, (
            '7c5d4h3s2c', '7c6d4h3s2c', '7c6d5h3s2c', '7c6d5h4s2c',
            '8c5d4h3s2c', '8c6d4h3s2c', '8c6d5h3s2c', '8c6d5h4s2c',
            '8c6d5h4s3c', '8c7d4h3s2c', '8c7d5h3s2c', '8c7d5h4s2c',
            '8c7d5h4s3c', '8c7d6h3s2c', '8c7d6h4s2c', '8c7d6h4s3c',
            '8c7d6h5s2c', '8c7d6h5s3c', '9c5d4h3s2c', 'KsKcAhQsJs',
            'AhAc2c3c4c', 'AhAc2c3c5c', '2c2d3s3c4s', 'AcAdKsKcTs',
            'AcAdKsKcJs', 'QcQsQhAhKh', 'AcAsAd2s4s', 'AcAsAd3s4s',
            'Ac2s3d4s5s', '2c3s4d5s6s', 'TcJsQdKsAs', '9c5c4c3c2c',
            'Kc5c4c3c2c', 'KhKsKdAhAc', 'AcAdAsKhKs', '2c2d2h2sQs',
            '2c2d2h2sKs', 'AcAdAhAsKs', '2c3c4c5c6c', '3d4d5d6d7d',
            '9sTsJsQsKs', 'TsJsQsKsAs',
        ))))

        self.assertSequenceEqual(hands, sorted(hands, reverse=True))

    def test_lowballA5_hand(self):
        self.assertRaises(ValueError, LowballA5Hand, parse_cards(
            '9sTsJsQsKsAs'
        ))
        self.assertRaises(ValueError, LowballA5Hand, parse_cards(
            '4c5dThJsAcKh2h'
        ))
        self.assertRaises(ValueError, LowballA5Hand, parse_cards(
            'AcAdAhAsAc'
        ))

        hands = tuple(map(LowballA5Hand, map(parse_cards, (
            'Ac2c3c4c5c', '6c4d3h2sAc', '6c5d3h2sAc', '6c5c4c2cAc',
            '6c5d4h3sAc', '6c5d4h3s2c', '7c4d3h2sAc', '7c5d3h2sAc',
            '7c6d5h4s3c', '8c5d4h3sAc', '8c5d4h3s2c', '9c7d6h4s3c',
            'KcJd8h6s4c', 'AcAd9h5s3c', '2c2d5h4s3c', '3c3d6h4s2c',
            '3c3d6h5sAc', '2s2c3s3cAh', 'AcAdAsKhQs', 'KhKsKcAcAd',
            'KhKsKcKdAc',
        ))))

        self.assertSequenceEqual(hands, sorted(hands, reverse=True))

    def test_badugi_hand(self):
        self.assertRaises(ValueError, BadugiHand, parse_cards('Ac2d3c4s5c'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('AcAc'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('Ac2d3c'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('As2s'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('Ad2d3d4d'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('Ad2d3c4h'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('AcAd'))
        self.assertRaises(ValueError, BadugiHand, parse_cards('AcAd3h4s'))

        hands = tuple(map(BadugiHand, map(parse_cards, (
            'Ac2d3h4s', 'Ac2d3h5s', 'Ac2d4h5s', 'Ac3d4h5s', 'Ac3d6h9s',
            'Ac3d6hTs', '7c8d9hTs', '7c8d9hJs', 'TcJdQhKs', 'Ac2d3h', 'As2c4d',
            'Ah3s4c', '2d3h4s', '4c5d6h', '4s5c8d', '4h5sTc', '4d8hTs',
            '4c8dKh', 'JsQcKd', 'Ac2d', 'Ah3s', '2c3d', '2h4s', '2c5d', '2h8s',
            '7c8d', '2hJs', '3cJd', 'ThJs', 'TcKd', 'JhKs', 'QhKs', 'Ac', '2d',
            '3h', '4s', '5c', '6d', '7h', '8s', '9c', 'Td', 'Jh', 'Qs', 'Kc',
        ))))

        self.assertSequenceEqual(hands, sorted(hands, reverse=True))


if __name__ == '__main__':
    main()
