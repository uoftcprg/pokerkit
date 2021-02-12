from abc import ABC, abstractmethod
from collections import Collection, Iterable, Iterator, MutableSequence
from typing import Any

from pokertools.cards import Card, Rank, Suit


class Deck(Collection[Card], ABC):
    """Deck is the abstract base class for all decks."""

    def __init__(self) -> None:
        self.__cards = self._create_cards()

    def __iter__(self) -> Iterator[Card]:
        return iter(self.__cards)

    def __len__(self) -> int:
        return len(self.__cards)

    def __contains__(self, __x: Any) -> bool:
        return __x in self.__cards

    def remove(self, cards: Iterable[Card]) -> None:
        """Removes the cards from the deck.

        :param cards: the cards to be removed
        :return: a list of drawn cards
        """
        for card in cards:
            self.__cards.remove(card)

    @abstractmethod
    def _create_cards(self) -> MutableSequence[Card]:
        pass


class StandardDeck(Deck):
    """StandardDeck is the class for standard decks."""

    def _create_cards(self) -> MutableSequence[Card]:
        return [Card(rank, suit) for rank in Rank for suit in Suit]


class ShortDeck(Deck):
    """ShortDeck is the class for short decks.

    The minimum rank of cards in short decks is 6.
    """

    def _create_cards(self) -> MutableSequence[Card]:
        return [Card(rank, suit) for rank in Rank if rank.value.isalpha() or int(rank.value) >= 6 for suit in Suit]
