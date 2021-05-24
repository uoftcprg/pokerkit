from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from itertools import chain, combinations

from pokertools.cards import Card
from pokertools.hands import BadugiHand, Hand, Lowball27Hand, LowballA5Hand, ShortHand, StandardHand


class Evaluator(ABC):
    """Evaluator is the abstract class for all evaluators."""

    @staticmethod
    @abstractmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> Hand:
        """Evaluates the hand of the combinations of the hole cards and the board cards.

        :param hole_cards: The hole cards.
        :param board_cards: The board cards.
        :return: The hand of the combinations.
        :raises ValueError: If the number of cards are insufficient.
        """
        ...


class StandardEvaluator(Evaluator):
    """StandardEvaluator is the class for standard evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> StandardHand:
        return StandardHand(chain(hole_cards, board_cards))


class GreekEvaluator(Evaluator):
    """GreekEvaluator is the class for Greek evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        if isinstance(hole_cards, Iterator):
            hole_cards = tuple(hole_cards)

        return max(StandardEvaluator.hand(hole_cards, combination) for combination in combinations(board_cards, 3))


class OmahaEvaluator(Evaluator):
    """OmahaEvaluator is the class for Omaha evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card]) -> StandardHand:
        if isinstance(board_cards, Iterator):
            board_cards = tuple(board_cards)

        return max(GreekEvaluator.hand(combination, board_cards) for combination in combinations(hole_cards, 2))


class ShortEvaluator(Evaluator):
    """ShortEvaluator is the class for short evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> ShortHand:
        return ShortHand(chain(hole_cards, board_cards))


class BadugiEvaluator(Evaluator):
    """BadugiEvaluator is the class for Badugi evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> BadugiHand:
        return BadugiHand(chain(hole_cards, board_cards))


class LowballA5Evaluator(Evaluator):
    """LowballA5Evaluator is the class for Ace-to-five Lowball evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> LowballA5Hand:
        return LowballA5Hand(chain(hole_cards, board_cards))


class Lowball27Evaluator(Evaluator):
    """Lowball27Evaluator is the class for Deuce-to-seven Lowball evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> Lowball27Hand:
        return Lowball27Hand(chain(hole_cards, board_cards))


class RankEvaluator(Evaluator):
    """RankEvaluator is the class for rank evaluators."""

    @staticmethod
    def hand(hole_cards: Iterable[Card], board_cards: Iterable[Card] = ()) -> Hand:
        return Hand(-max(card.rank.index for card in chain(hole_cards, board_cards)))
