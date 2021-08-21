from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import partial
from itertools import chain, combinations

from auxiliary import reverse_args

from pokerface.cards import Card
from pokerface.hands import (
    BadugiHand, LowIndexedHand, Lowball27Hand, LowballA5Hand, ShortDeckHand,
    StandardHand,
)


class Evaluator(ABC):
    """The abstract class for all evaluators."""

    @classmethod
    @abstractmethod
    def evaluate_hand(cls, hole, board):
        """Evaluate the hand of the combinations of the hole cards and
        the board cards.

        :param hole: The hole cards.
        :param board: The board cards.
        :return: The hand of the combinations.
        :raises ValueError: If the number of cards are insufficient.
        """
        ...


class StandardEvaluator(Evaluator):
    """The class for standard evaluators."""

    _hand_type = StandardHand

    @classmethod
    def evaluate_hand(cls, hole, board):
        return max(map(cls._hand_type, combinations(chain(hole, board), 5)))


class GreekEvaluator(StandardEvaluator):
    """The class for Greek evaluators."""

    @classmethod
    def evaluate_hand(cls, hole, board):
        if isinstance(hole, Iterator):
            hole = tuple(hole)

        return max(map(cls._hand_type, map(
            partial(chain, hole), combinations(board, 3),
        )))


class OmahaEvaluator(GreekEvaluator):
    """The class for Omaha evaluators."""

    @classmethod
    def evaluate_hand(cls, hole, board):
        if isinstance(board, Iterator):
            board = tuple(board)

        return max(map(
            partial(reverse_args(super().evaluate_hand), board),
            combinations(hole, 2),
        ))


class ShortDeckEvaluator(StandardEvaluator):
    """The class for Short-deck evaluators."""

    _hand_type = ShortDeckHand


class Lowball27Evaluator(StandardEvaluator):
    """The class for Deuce-to-seven Lowball evaluators."""

    _hand_type = Lowball27Hand


class LowballA5Evaluator(StandardEvaluator):
    """The class for Ace-to-five Lowball evaluators."""

    _hand_type = LowballA5Hand


class BadugiEvaluator(Evaluator):
    """The class for Badugi evaluators."""

    @classmethod
    def evaluate_hand(cls, hole, board):
        cards = tuple(chain(hole, board))
        hands = []

        for count in range(1, 5):
            for combination in combinations(cards, count):
                if BadugiHand._is_valid(combination):
                    hands.append(BadugiHand(combination))

        return max(hands)


class RankEvaluator(Evaluator):
    """The class for rank evaluators."""

    @classmethod
    def evaluate_hand(cls, hole, board):
        return LowIndexedHand(
            max(map(Card.rank.fget, chain(hole, board))).index
        )
