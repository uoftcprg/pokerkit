from abc import ABC, abstractmethod
from collections import Iterable
from itertools import chain, combinations

from auxiliary import retain_iter

from pokertools.cards import Card
from pokertools.hands import Hand, ShortHand, StandardHand


class Evaluator(ABC):
    """Evaluator is the abstract base class for all evaluators."""

    @staticmethod
    @abstractmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        """Evaluates the hand of the combinations of the hole cards and the board cards.

        :param hole_cards: The hole cards.
        :param board_cards: The board cards.
        :return: The hand of the combinations.
        :raise ValueError: If the number of cards are insufficient.
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
    @retain_iter
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        return max(StandardEvaluator.hand(hole_cards, combination) for combination in combinations(board_cards, 3))


class OmahaEvaluator(Evaluator):
    """OmahaEvaluator is the class for Omaha evaluators."""

    @staticmethod
    @retain_iter
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        return max(GreekEvaluator.hand(combination, board_cards) for combination in combinations(hole_cards, 2))


class ShortEvaluator(Evaluator):
    """ShortEvaluator is the class for short evaluators."""

    @staticmethod
    @retain_iter
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> ShortHand:
        return ShortHand(chain(hole_cards, board_cards))


class RankEvaluator(Evaluator):
    """RankEvaluator is the class for rank evaluators."""

    @staticmethod
    @retain_iter
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        return Hand(-max(card.rank.index for card in chain(hole_cards, board_cards)))
