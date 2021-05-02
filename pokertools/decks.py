from collections.abc import Iterable

from pokertools.cards import Card, SHORT_RANKS, STANDARD_RANKS, Suit


class Deck(set[Card]):
    """Deck is the class for decks."""

    def draw(self, cards: Iterable[Card]) -> None:
        """Draws the cards from this deck.

        :param cards: The cards to be drawn.
        :return: None.
        """
        self.__isub__(set(cards))


class StandardDeck(Deck):
    """StandardDeck is the class for standard decks."""

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in STANDARD_RANKS for suit in Suit)


class ShortDeck(Deck):
    """ShortDeck is the class for short decks.

       The minimum rank of cards in short decks is 6.
    """

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in SHORT_RANKS for suit in Suit)
