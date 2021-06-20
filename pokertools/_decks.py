from collections.abc import Iterator
from random import shuffle

from pokertools._cards import Card, Ranks, Suit


class Deck(list):
    """Deck is the class for decks.

    :param cards: The cards in this deck, defaults to an empty tuple.
    """

    def __init__(self, cards=()):
        super().__init__(cards)

        shuffle(self)

    def draw(self, cards):
        """Draws the number of cards or the specified cards from this deck.

        :param cards: The number of cards or the specified cards to be drawn.
        :return: None.
        """
        if isinstance(cards, int):
            cards = self[:cards]
        elif isinstance(cards, Iterator):
            cards = tuple(cards)

        for card in cards:
            self.remove(card)

        return cards


class StandardDeck(Deck):
    """StandardDeck is the class for standard decks."""

    def __init__(self):
        super().__init__(Card(rank, suit) for rank in Ranks.STANDARD_RANKS.value for suit in Suit)


class ShortDeck(Deck):
    """ShortDeck is the class for short decks.

    The minimum rank of cards in short decks is 6.
    """

    def __init__(self):
        super().__init__(Card(rank, suit) for rank in Ranks.SHORT_DECK_RANKS.value for suit in Suit)
