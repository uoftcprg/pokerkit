from collections.abc import Collection, Iterable, Iterator
from typing import Any

from pokertools.cards import Card, SHORT_RANKS, STANDARD_RANKS, Suit


class Deck(Collection[Card]):
    """Deck is the class for decks."""

    def __init__(self, cards: Iterable[Card]):
        self.__cards = set(cards)

    def draw(self, cards: Iterable[Card]) -> None:
        """Draws the cards from this deck.

        :param cards: The cards to be drawn.
        :return: None.
        """
        self.__cards -= set(cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self.__cards)

    def __contains__(self, __x: Any) -> bool:
        return __x in self.__cards

    def __len__(self) -> int:
        return len(self.__cards)


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
