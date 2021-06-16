from collections.abc import Sequence
from typing import final

from pokertools import (
    Deck, Evaluator, GreekEvaluator, OmahaEvaluator, ShortDeck, ShortDeckEvaluator, StandardDeck, StandardEvaluator,
)

from gameframe.poker.bases import Limit, Poker
from gameframe.poker.limits import FixedLimit, NoLimit, PotLimit
from poker.stages import BettingStage, BoardDealingStage, HoleDealingStage, ShowdownStage


class HoldEm(Poker):
    """HoldEm is the class for Hold'em games."""

    def __init__(
            self,
            hole_card_count: int,
            evaluators: Sequence[Evaluator],
            deck: Deck,
            limit: Limit,
            ante: int,
            blinds: Sequence[int],
            starting_stacks: Sequence[int],
    ):
        max_delta = max(ante, max(blinds, default=0))

        super().__init__(
            (
                HoleDealingStage(False, hole_card_count), BettingStage(max_delta),
                BoardDealingStage(3), BettingStage(max_delta),
                BoardDealingStage(1), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                BoardDealingStage(1), BettingStage(2 * max_delta if isinstance(limit, FixedLimit) else max_delta),
                ShowdownStage(),
            ),
            evaluators,
            deck,
            limit,
            ante,
            blinds,
            starting_stacks,
        )


class TexasHoldEm(HoldEm):
    """TexasHoldEm is the class for Texas Hold'em games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(2, (StandardEvaluator(),), StandardDeck(), limit, ante, blinds, starting_stacks)


@final
class FixedLimitTexasHoldEm(TexasHoldEm):
    """FixedLimitTexasHoldEm is the class for Fixed-Limit Texas Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitTexasHoldEm(TexasHoldEm):
    """PotLimitTexasHoldEm is the class for Pot-Limit Texas Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitTexasHoldEm(TexasHoldEm):
    """NoLimitTexasHoldEm is the class for No-Limit Texas Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class OmahaHoldEm(HoldEm):
    """OmahaHoldEm is the class for Omaha Hold'em games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(4, (OmahaEvaluator(),), StandardDeck(), limit, ante, blinds, starting_stacks)


@final
class FixedLimitOmahaHoldEm(OmahaHoldEm):
    """FixedLimitOmahaHoldEm is the class for Fixed-Limit Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitOmahaHoldEm(OmahaHoldEm):
    """PotLimitOmahaHoldEm is the class for Pot-Limit Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitOmahaHoldEm(OmahaHoldEm):
    """NoLimitOmahaHoldEm is the class for No-Limit Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class FiveCardOmahaHoldEm(HoldEm):
    """FiveCardOmahaHoldEm is the class for 5-Card Omaha Hold'em games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(5, (OmahaEvaluator(),), StandardDeck(), limit, ante, blinds, starting_stacks)


@final
class FixedLimitFiveCardOmahaHoldEm(FiveCardOmahaHoldEm):
    """FixedLimitFiveCardOmahaHoldEm is the class for Fixed-Limit 5-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitFiveCardOmahaHoldEm(FiveCardOmahaHoldEm):
    """PotLimitFiveCardOmahaHoldEm is the class for Pot-Limit 5-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitFiveCardOmahaHoldEm(FiveCardOmahaHoldEm):
    """NoLimitFiveCardOmahaHoldEm is the class for No-Limit 5-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class SixCardOmahaHoldEm(HoldEm):
    """SixCardOmahaHoldEm is the class for 6-Card Omaha Hold'em games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(6, (OmahaEvaluator(),), StandardDeck(), limit, ante, blinds, starting_stacks)


@final
class FixedLimitSixCardOmahaHoldEm(SixCardOmahaHoldEm):
    """FixedLimitSixCardOmahaHoldEm is the class for Fixed-Limit 6-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitSixCardOmahaHoldEm(SixCardOmahaHoldEm):
    """PotLimitSixCardOmahaHoldEm is the class for Pot-Limit 6-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitSixCardOmahaHoldEm(SixCardOmahaHoldEm):
    """NoLimitSixCardOmahaHoldEm is the class for No-Limit 6-Card Omaha Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class GreekHoldEm(HoldEm):
    """GreekHoldEm is the class for Greek Hold'em games."""

    def __init__(self, limit: Limit, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(2, (GreekEvaluator(),), StandardDeck(), limit, ante, blinds, starting_stacks)


@final
class FixedLimitGreekHoldEm(GreekHoldEm):
    """FixedLimitGreekHoldEm is the class for Fixed-Limit Greek Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, blinds, starting_stacks)


@final
class PotLimitGreekHoldEm(GreekHoldEm):
    """PotLimitGreekHoldEm is the class for Pot-Limit Greek Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, blinds, starting_stacks)


@final
class NoLimitGreekHoldEm(GreekHoldEm):
    """NoLimitGreekHoldEm is the class for No-Limit Greek Hold'em games."""

    def __init__(self, ante: int, blinds: Sequence[int], starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, blinds, starting_stacks)


class ShortDeckHoldEm(HoldEm):
    """ShortDeckHoldEm is the class for Short-deck Hold'em games."""

    def __init__(self, limit: Limit, ante: int, button_blind: int, starting_stacks: Sequence[int]):
        super().__init__(
            2,
            (ShortDeckEvaluator(),),
            ShortDeck(),
            limit,
            ante,
            (0,) * (len(starting_stacks) - 1) + (button_blind,),
            starting_stacks,
        )


@final
class FixedLimitShortDeckHoldEm(ShortDeckHoldEm):
    """FixedLimitShortDeckHoldEm is the class for Fixed-Limit Short-deck Hold'em games."""

    def __init__(self, ante: int, button_blind: int, starting_stacks: Sequence[int]):
        super().__init__(FixedLimit(), ante, button_blind, starting_stacks)


@final
class PotLimitShortDeckHoldEm(ShortDeckHoldEm):
    """PotLimitShortDeckHoldEm is the class for Pot-Limit Short-deck Hold'em games."""

    def __init__(self, ante: int, button_blind: int, starting_stacks: Sequence[int]):
        super().__init__(PotLimit(), ante, button_blind, starting_stacks)


@final
class NoLimitShortDeckHoldEm(ShortDeckHoldEm):
    """NoLimitShortDeckHoldEm is the class for No-Limit Short-deck Hold'em games."""

    def __init__(self, ante: int, button_blind: int, starting_stacks: Sequence[int]):
        super().__init__(NoLimit(), ante, button_blind, starting_stacks)
