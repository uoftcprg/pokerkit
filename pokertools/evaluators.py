from abc import ABC, abstractmethod
from collections import Collection, Iterable
from itertools import chain, combinations

from pokertools.cards import Card
from pokertools.hands import Hand, ShortHand, StandardHand


class Evaluator(ABC):
    """Evaluator is the abstract base class for all evaluators."""

    @staticmethod
    @abstractmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        """Evaluates the hand of the combinations of the hole cards and the board cards.

        :param hole_cards: the hole cards
        :param board_cards: the board cards
        :return: the hand of the combinations
        :raise ValueError: if the number of cards are insufficient
        """
        ...


class StandardEvaluator(Evaluator):
    """StandardEvaluator is the class for standard evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        return StandardHand(chain(hole_cards, board_cards))


class GreekEvaluator(Evaluator):
    """GreekEvaluator is the class for Greek evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        if isinstance(hole_cards, Collection):
            return max(StandardEvaluator.hand(hole_cards, combination) for combination in combinations(board_cards, 3))
        else:
            return GreekEvaluator.hand(tuple(hole_cards), board_cards)


class OmahaEvaluator(Evaluator):
    """OmahaEvaluator is the class for Omaha evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        if isinstance(board_cards, Collection):
            return max(GreekEvaluator.hand(combination, board_cards) for combination in combinations(hole_cards, 2))
        else:
            return OmahaEvaluator.hand(hole_cards, tuple(board_cards))


class ShortEvaluator(Evaluator):
    """ShortEvaluator is the class for short evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> ShortHand:
        return ShortHand(chain(hole_cards, board_cards))
