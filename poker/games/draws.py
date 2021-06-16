from collections.abc import Sequence
from typing import final

from pokertools import (
    BadugiEvaluator, Card, Deck, Lowball27Evaluator, Rank, RankEvaluator, StandardDeck, StandardEvaluator, Suit,
)

from gameframe.poker.bases import Limit, Poker
from gameframe.poker.limits import FixedLimit, NoLimit, PotLimit
from poker.stages import BettingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage


class FiveCardDraw(Poker):
    """FiveCardDraw is the base class for all Five-Card Draw games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, 5), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(max_delta),
                ShowdownStage(),
            ),
            (StandardEvaluator(),),
            StandardDeck(),
            limit,
            ante,
            blinds,
            starting_stacks,
        )


@final
class FixedLimitFiveCardDraw(FiveCardDraw):
    """FixedLimitFiveCardDraw is the class for Fixed-Limit Five-Card Draw games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitFiveCardDraw(FiveCardDraw):
    """PotLimitFiveCardDraw is the class for Pot-Limit Five-Card Draw games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitFiveCardDraw(FiveCardDraw):
    """NoLimitFiveCardDraw is the class for No-Limit Five-Card Draw games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class Badugi(Poker):
    """Badugi is the class for Badugi games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, 4), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                DiscardDrawStage(), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                ShowdownStage(),
            ),
            (BadugiEvaluator(),),
            StandardDeck(),
            limit,
            ante,
            blinds,
            starting_stacks,
        )


@final
class FixedLimitBadugi(Badugi):
    """FixedLimitBadugi is the class for Fixed-Limit Badugi games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitBadugi(Badugi):
    """PotLimitBadugi is the class for Pot-Limit Badugi games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitBadugi(Badugi):
    """NoLimitBadugi is the class for No-Limit Badugi games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class SingleDrawLowball27(Poker):
    """SingleDrawLowball27 is the class for 2-7 Single Draw Lowball games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, 5), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(max_delta),
                ShowdownStage(),
            ),
            (Lowball27Evaluator(),),
            StandardDeck(),
            limit,
            ante,
            blinds,
            starting_stacks,
        )


@final
class FixedLimitSingleDrawLowball27(SingleDrawLowball27):
    """FixedLimitSingleDrawLowball27 is the class for Fixed-Limit 2-7 Single Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitSingleDrawLowball27(SingleDrawLowball27):
    """PotLimitSingleDrawLowball27 is the class for Pot-Limit 2-7 Single Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitSingleDrawLowball27(SingleDrawLowball27):
    """NoLimitSingleDrawLowball27 is the class for No-Limit 2-7 Single Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class TripleDrawLowball27(Poker):
    """TripleDrawLowball27 is the class for 2-7 Triple Draw Lowball games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, 5), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(max_delta),
                DiscardDrawStage(), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                DiscardDrawStage(), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                ShowdownStage(),
            ),
            (Lowball27Evaluator(),),
            StandardDeck(),
            limit,
            ante,
            blinds,
            starting_stacks,
        )


@final
class FixedLimitTripleDrawLowball27(TripleDrawLowball27):
    """FixedLimitTripleDrawLowball27 is the class for Fixed-Limit 2-7 Triple Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitTripleDrawLowball27(TripleDrawLowball27):
    """PotLimitTripleDrawLowball27 is the class for Pot-Limit 2-7 Triple Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitTripleDrawLowball27(TripleDrawLowball27):
    """NoLimitTripleDrawLowball27 is the class for No-Limit 2-7 Triple Draw Lowball games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


@final
class KuhnPoker(Poker):
    """KuhnPoker is the class for Kuhn Poker games."""

    def __init__(self) -> None:
        super().__init__(
            (
                HoleDealingStage(False, 1),
                BettingStage(1),
                ShowdownStage(),
            ),
            (RankEvaluator(),),
            Deck((Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE), Card(Rank.KING, Suit.SPADE))),
            FixedLimit(),
            1,
            (),
            (2, 2),
        )
