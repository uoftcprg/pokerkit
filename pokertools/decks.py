from collections.abc import Iterable
from random import shuffle

from pokertools.cards import Card, SHORT_DECK_RANKS, STANDARD_RANKS, Suit


class Deck(list[Card]):
    """Deck is the class for decks.

    :param cards: The cards in this deck.
    """

    def __init__(self, cards: Iterable[Card]):
        super().__init__(cards)

        shuffle(self)

    def draw(self, cards: Iterable[Card]) -> None:
        """Draws the cards from this deck.

        :param cards: The cards to be drawn.
        :return: None.
        """
        for card in cards:
            self.remove(card)


class StandardDeck(Deck):
    """StandardDeck is the class for standard decks."""

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in STANDARD_RANKS for suit in Suit)


class ShortDeck(Deck):
    """ShortDeck is the class for short decks.

    The minimum rank of cards in short decks is 6.
    """

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in SHORT_DECK_RANKS for suit in Suit)
