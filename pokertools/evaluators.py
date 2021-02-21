from abc import ABC, abstractmethod
from collections import Iterable
from itertools import chain, combinations

from pokertools.cards import Card
from pokertools.hands import Hand, ShortHand, StandardHand


class Evaluator(ABC):
    """Evaluator is the abstract base class for all evaluators."""

    @abstractmethod
    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        """Evaluates the hand of the combinations of the hole cards and the board cards.

        :param hole_cards: the hole cards
        :param board_cards: the board cards
        :return: the hand of the combinations
        :raise ValueError: if the number of cards are insufficient
        """
        pass


class StandardEvaluator(Evaluator):
    """StandardEvaluator is the class for standard evaluators."""

    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        return StandardHand(*chain(hole_cards, board_cards))


class GreekEvaluator(StandardEvaluator):
    """GreekEvaluator is the class for Greek evaluators."""

    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        hole_cards = list(hole_cards)

        return max(super(GreekEvaluator, self).hand(hole_cards, combo) for combo in combinations(board_cards, 3))


class OmahaEvaluator(GreekEvaluator):
    """OmahaEvaluator is the class for Omaha evaluators."""

    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        board_cards = list(board_cards)

        return max(super(OmahaEvaluator, self).hand(combo, board_cards) for combo in combinations(hole_cards, 2))


class ShortEvaluator(Evaluator):
    """ShortEvaluator is the class for short evaluators."""

    def hand(self, hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> ShortHand:
        return ShortHand(*chain(hole_cards, board_cards))
