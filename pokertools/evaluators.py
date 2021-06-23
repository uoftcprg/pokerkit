from abc import ABC, abstractmethod
from collections.abc import Iterator
from functools import partial
from itertools import chain, combinations

from pokertools.cards import Card, Rank
from pokertools.hands import BadugiHand, LowIndexedHand, Lowball27Hand, LowballA5Hand, ShortDeckHand, StandardHand
from pokertools.utilities import rainbow


class Evaluator(ABC):
    """Evaluator is the abstract class for all evaluators."""

    @staticmethod
    @abstractmethod
    def evaluate(hole_cards, board_cards):
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
    def evaluate(hole_cards, board_cards=()):
        return max(map(StandardHand, combinations(chain(hole_cards, board_cards), 5)))


class GreekEvaluator(Evaluator):
    """GreekEvaluator is the class for Greek evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards):
        if isinstance(hole_cards, Iterator):
            hole_cards = tuple(hole_cards)

        return max(map(StandardHand, map(partial(chain, hole_cards), combinations(board_cards, 3))))


class OmahaEvaluator(Evaluator):
    """OmahaEvaluator is the class for Omaha evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards):
        if isinstance(board_cards, Iterator):
            board_cards = tuple(board_cards)

        return max(GreekEvaluator.evaluate(combination, board_cards) for combination in combinations(hole_cards, 2))


class ShortDeckEvaluator(Evaluator):
    """ShortDeckEvaluator is the class for Short-deck evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards=()):
        return max(map(ShortDeckHand, combinations(chain(hole_cards, board_cards), 5)))


class BadugiEvaluator(Evaluator):
    """BadugiEvaluator is the class for Badugi evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards=()):
        cards = tuple(chain(hole_cards, board_cards))

        return max(map(BadugiHand, filter(
            lambda sub_cards: rainbow(map(Card.rank.fget, sub_cards)) and rainbow(map(Card.suit.fget, sub_cards)),
            chain(*map(partial(combinations, cards), range(1, 5))),
        )))


class LowballA5Evaluator(Evaluator):
    """LowballA5Evaluator is the class for Ace-to-five Lowball evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards=()):
        return max(map(LowballA5Hand, combinations(chain(hole_cards, board_cards), 5)))


class Lowball27Evaluator(Evaluator):
    """Lowball27Evaluator is the class for Deuce-to-seven Lowball evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards=()):
        return max(map(Lowball27Hand, combinations(chain(hole_cards, board_cards), 5)))


class RankEvaluator(Evaluator):
    """RankEvaluator is the class for rank evaluators."""

    @staticmethod
    def evaluate(hole_cards, board_cards=()):
        return LowIndexedHand(max(map(Rank._index.fget, map(Card.rank.fget, chain(hole_cards, board_cards)))))
