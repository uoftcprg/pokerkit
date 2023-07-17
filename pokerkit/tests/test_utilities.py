""":mod:`pokerkit.tests.test_utilities` implements unit tests for
:mod:`pokerkit.utilities`.
"""

from unittest import TestCase, main

from pokerkit.utilities import Card, Deck, Rank, RankOrder, Suit


class RankTestCase(TestCase):
    def test_members(self) -> None:
        self.assertEqual(''.join(Rank), 'A23456789TJQK')


class RankOrderTestCase(TestCase):
    def test_members(self) -> None:
        self.assertEqual(''.join(RankOrder.EIGHT_OR_BETTER_LOW), 'A2345678')
        self.assertEqual(''.join(RankOrder.STANDARD), '23456789TJQKA')
        self.assertEqual(''.join(RankOrder.SHORT_DECK_HOLDEM), '6789TJQKA')
        self.assertEqual(''.join(RankOrder.REGULAR), 'A23456789TJQK')


class SuitTestCase(TestCase):
    def test_members(self) -> None:
        self.assertEqual(''.join(Suit), 'cdhs')


class DeckTestCase(TestCase):
    def test_members(self) -> None:
        self.assertEqual(len(Deck.STANDARD), 52)
        self.assertCountEqual(
            Deck.STANDARD,
            Card.parse(
                '2c3c4c5c6c7c8c9cTcJcQcKcAc',
                '2d3d4d5d6d7d8d9dTdJdQdKdAd',
                '2h3h4h5h6h7h8h9hThJhQhKhAh',
                '2s3s4s5s6s7s8s9sTsJsQsKsAs',
            ),
        )
        self.assertEqual(len(Deck.REGULAR), 52)
        self.assertCountEqual(
            Deck.STANDARD,
            Card.parse(
                'Ac2c3c4c5c6c7c8c9cTcJcQcKc',
                'Ad2d3d4d5d6d7d8d9dTdJdQdKd',
                'Ah2h3h4h5h6h7h8h9hThJhQhKh',
                'As2s3s4s5s6s7s8s9sTsJsQsKs',
            ),
        )
        self.assertEqual(len(Deck.SHORT_DECK_HOLDEM), 36)
        self.assertCountEqual(
            Deck.SHORT_DECK_HOLDEM,
            Card.parse(
                '6c7c8c9cTcJcQcKcAc',
                '6d7d8d9dTdJdQdKdAd',
                '6h7h8h9hThJhQhKhAh',
                '6s7s8s9sTsJsQsKsAs',
            ),
        )


if __name__ == '__main__':
    main()
