from collections.abc import Sequence
from typing import final

from pokertools import OmahaEvaluator, StandardDeck

from gameframe.poker.bases import Limit, Poker
from gameframe.poker.limits import FixedLimit, NoLimit, PotLimit
from poker.stages import BettingStage, BoardDealingStage, HoleDealingStage, ShowdownStage


class Courchevel(Poker):
    """Courchevel is the class for Courchevel games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, 5), BoardDealingStage(1), BettingStage(max_delta),
                BoardDealingStage(2), BettingStage(max_delta),
                BoardDealingStage(1), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                BoardDealingStage(1), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                ShowdownStage(),
            ),
            (OmahaEvaluator(),),
            StandardDeck(),
            limit,
            ante,
            blinds,
            starting_stacks,
        )


@final
class FixedLimitCourchevel(Courchevel):
    """FixedLimitCourchevel is the class for Fixed-Limit Courchevel games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitCourchevel(Courchevel):
    """PotLimitCourchevel is the class for Pot-Limit Courchevel games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitCourchevel(Courchevel):
    """NoLimitCourchevel is the class for No-Limit Courchevel games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)
