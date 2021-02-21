from abc import ABC
from collections import Collection, Iterable, Iterator
from typing import Any

from pokertools.cards import Card, Rank, Suit


class Deck(Collection[Card], ABC):
    """Deck is the abstract base class for all decks."""

    def __init__(self, cards: Iterable[Card]) -> None:
        self.__cards = set(cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self.__cards)

    def __contains__(self, __x: Any) -> bool:
        return __x in self.__cards

    def __len__(self) -> int:
        return len(self.__cards)

    def remove(self, *cards: Card) -> None:
        """Removes the cards from this deck.

        :param cards: the cards to be removed
        :return: None
        """
        self.__cards -= set(cards)


class StandardDeck(Deck):
    """StandardDeck is the class for standard decks."""

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in Rank for suit in Suit)


class ShortDeck(Deck):
    """ShortDeck is the class for short decks.

    The minimum rank of cards in short decks is 6.
    """

    def __init__(self) -> None:
        super().__init__(Card(rank, suit) for rank in Rank if not rank < Rank.SIX for suit in Suit)
