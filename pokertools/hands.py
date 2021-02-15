from abc import ABC, abstractmethod
from collections import Hashable, Iterable
from functools import total_ordering
from typing import Any

from treys import Card as TreysCard, Evaluator as TreysEvaluator  # type: ignore

from pokertools.cards import CardLike, parse_card


@total_ordering  # type: ignore
class Hand(Hashable, ABC):
    """Hand is the abstract base class for all hands."""

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass


class TreysHand(Hand):
    treys_evaluator = TreysEvaluator()

    def __init__(self, hole_cards: Iterable[CardLike], board_cards: Iterable[CardLike]):
        self.__hand_rank = self.treys_evaluator.evaluate(list(map(self.translate, hole_cards)),
                                                         list(map(self.translate, board_cards)))

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, TreysHand):
            return self.__hand_rank > other.__hand_rank  # type: ignore
        else:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TreysHand):
            return self.__hand_rank == other.__hand_rank  # type: ignore
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__hand_rank)

    def __repr__(self) -> str:
        return self.treys_evaluator.class_to_string(self.treys_evaluator.get_rank_class(  # type: ignore
            self.__hand_rank))

    @staticmethod
    def translate(card_like: CardLike) -> int:
        card = parse_card(card_like)

        return TreysCard.new(card.rank.value + card.suit.value)  # type: ignore
