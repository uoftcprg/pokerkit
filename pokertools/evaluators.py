from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import partial
from itertools import chain, combinations

from auxiliary import reverse_args

from pokertools.cards import Card
from pokertools.hands import (
    BadugiHand, LowIndexedHand, Lowball27Hand, LowballA5Hand, ShortDeckHand,
    StandardHand,
)


class Evaluator(ABC):
    """Evaluator is the abstract class for all evaluators."""

    @classmethod
    @abstractmethod
    def evaluate(cls, hole_cards, board_cards):
        """Evaluate the hand of the combinations of the hole cards and
        the board cards.

        :param hole_cards: The hole cards.
        :param board_cards: The board cards.
        :return: The hand of the combinations.
        :raises ValueError: If the number of cards are insufficient.
        """
        ...


class StandardEvaluator(Evaluator):
    """The class for standard evaluators."""

    _hand_type = StandardHand

    @classmethod
    def evaluate(cls, hole_cards, board_cards):
        return max(map(cls._hand_type, combinations(
            chain(hole_cards, board_cards), 5,
        )))


class GreekEvaluator(StandardEvaluator):
    """The class for Greek evaluators."""

    @classmethod
    def evaluate(cls, hole_cards, board_cards):
        if isinstance(hole_cards, Iterator):
            hole_cards = tuple(hole_cards)

        return max(map(cls._hand_type, map(
            partial(chain, hole_cards), combinations(board_cards, 3),
        )))


class OmahaEvaluator(GreekEvaluator):
    """The class for Omaha evaluators."""

    @classmethod
    def evaluate(cls, hole_cards, board_cards):
        if isinstance(board_cards, Iterator):
            board_cards = tuple(board_cards)

        return max(map(
            partial(reverse_args(super().evaluate), board_cards),
            combinations(hole_cards, 2),
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
    def evaluate(cls, hole_cards, board_cards):
        cards = tuple(chain(hole_cards, board_cards))
        hands = []

        for count in range(1, 5):
            for combination in combinations(cards, count):
                if BadugiHand._is_valid(combination):
                    hands.append(BadugiHand(combination))

        return max(hands)


class RankEvaluator(Evaluator):
    """The class for rank evaluators."""

    @classmethod
    def evaluate(cls, hole_cards, board_cards):
        return LowIndexedHand(max(map(Card.rank.fget, chain(
            hole_cards, board_cards,
        ))).index)
