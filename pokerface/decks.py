from collections.abc import Iterator
from itertools import product, starmap
from random import shuffle

from pokerface.cards import Card, Ranks, Suit


class Deck(list):
    """The class for decks.

    :param cards: The cards in this deck, defaults to an empty tuple.
    """

    def __init__(self, cards=()):
        super().__init__(cards)

        shuffle(self)

    def draw(self, cards):
        """Draw the number of cards or the specified cards from this
        deck.

        :param cards: The number of cards or the specified cards to be
                      drawn.
        :return: The removed cards.
        """
        if isinstance(cards, int):
            if len(self) < cards:
                raise ValueError('not enough cards in deck')

            cards = self[:cards]
        elif isinstance(cards, Iterator):
            cards = tuple(cards)

        for card in cards:
            self.remove(card)

        return cards


class StandardDeck(Deck):
    """The class for standard decks."""

    def __init__(self):
        super().__init__(starmap(Card, product(Ranks.STANDARD.value, Suit)))


class ShortDeck(Deck):
    """The class for short decks.

    The minimum rank of cards in short decks is ``6``.
    """

    def __init__(self):
        super().__init__(starmap(Card, product(Ranks.SHORT_DECK.value, Suit)))
