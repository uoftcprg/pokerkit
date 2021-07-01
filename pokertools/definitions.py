from abc import ABC, abstractmethod

from pokertools.cards import Card, Rank, Suit
from pokertools.decks import Deck, ShortDeck, StandardDeck
from pokertools.evaluators import (
    BadugiEvaluator, GreekEvaluator, Lowball27Evaluator, OmahaEvaluator, RankEvaluator, ShortDeckEvaluator,
    StandardEvaluator,
)
from pokertools.stages import BettingStage, BoardDealingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage


class Definition(ABC):
    """Definition is the abstract base class for all poker definitions."""

    @abstractmethod
    def create_stages(self, game):
        """Returns the stages of the poker game defined by this poker definition.

        :param game: The poker game.
        :return: The stages of this poker definition.
        """
        ...

    @abstractmethod
    def create_evaluators(self):
        """Returns the evaluators of the poker game defined by this poker definition.

        :return: The evaluators of this poker definition.
        """
        ...

    @abstractmethod
    def create_deck(self):
        """Creates a deck of the poker game defined by this poker definition.

        :return: The created deck of this poker definition.
        """
        ...


class StaticHoleDefinitionMixin(Definition, ABC):
    """StaticHoleDefinitionMixin is the mixin for all game definitions with a static number of hole cards."""

    @property
    @abstractmethod
    def hole_card_count(self):
        """Returns the number of hole cards belonging to each player.

        :return: The number of hole cards belonging to each player.
        """
        ...


class HoldEmDefinition(StaticHoleDefinitionMixin, Definition, ABC):
    """HoldEmDefinition is the abstract base class for all Hold'em game definitions."""

    def create_stages(self, game):
        return (
            HoleDealingStage(False, self.hole_card_count, game), BettingStage(False, game),
            BoardDealingStage(3, game), BettingStage(False, game),
            BoardDealingStage(1, game), BettingStage(True, game),
            BoardDealingStage(1, game), BettingStage(True, game),
            ShowdownStage(game),
        )


class TexasHoldEmDefinition(HoldEmDefinition):
    """TexasHoldEmDefinition is the class for Texas Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return StandardEvaluator(),

    def create_deck(self):
        return StandardDeck()


class OmahaHoldEmDefinition(HoldEmDefinition):
    """OmahaHoldEmDefinition is the class for Omaha Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 4

    def create_evaluators(self):
        return OmahaEvaluator(),

    def create_deck(self):
        return StandardDeck()


class FiveCardOmahaHoldEmDefinition(OmahaHoldEmDefinition):
    """FiveCardOmahaHoldEmDefinition is the class for 5-Card Omaha Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 5


class SixCardOmahaHoldEmDefinition(OmahaHoldEmDefinition):
    """SixCardOmahaHoldEmDefinition is the class for 6-Card Omaha Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 6


class GreekHoldEmDefinition(HoldEmDefinition):
    """GreekHoldEmDefinition is the class for Greek Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return GreekEvaluator(),

    def create_deck(self):
        return StandardDeck()


class ShortDeckHoldEmDefinition(HoldEmDefinition):
    """ShortDeckHoldEmDefinition is the class for Short-deck Hold'em game definitions."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return ShortDeckEvaluator(),

    def create_deck(self):
        return ShortDeck()


class DrawDefinition(StaticHoleDefinitionMixin, Definition, ABC):
    """DrawDefinition is the abstract base class for all draw game definitions."""
    ...


class SingleDrawDefinition(DrawDefinition, ABC):
    """SingleDrawDefinition is the abstract base class for all single draw game definitions."""

    def create_stages(self, game):
        return (
            HoleDealingStage(False, self.hole_card_count, game), BettingStage(False, game),
            DiscardDrawStage(game), BettingStage(True, game),
            ShowdownStage(game),
        )


class TripleDrawDefinition(DrawDefinition, ABC):
    """TripleDrawDefinition is the abstract base class for all triple draw game definitions."""

    def create_stages(self, game):
        return (
            HoleDealingStage(False, self.hole_card_count, game), BettingStage(False, game),
            DiscardDrawStage(game), BettingStage(False, game),
            DiscardDrawStage(game), BettingStage(True, game),
            DiscardDrawStage(game), BettingStage(True, game),
            ShowdownStage(game),
        )


class FiveCardDrawDefinition(SingleDrawDefinition):
    """FiveCardDrawDefinition is the class for Five-Card Draw game definitions."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return StandardEvaluator(),

    def create_deck(self):
        return StandardDeck()


class BadugiDefinition(TripleDrawDefinition):
    """BadugiDefinition is the class for Badugi game definitions."""

    @property
    def hole_card_count(self):
        return 4

    def create_evaluators(self):
        return BadugiEvaluator(),

    def create_deck(self):
        return StandardDeck()


class SingleDrawLowball27Definition(SingleDrawDefinition):
    """SingleDrawLowball27Definition is the class for 2-7 Single Draw Lowball game definitions."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return Lowball27Evaluator(),

    def create_deck(self):
        return StandardDeck()


class TripleDrawLowball27Definition(TripleDrawDefinition):
    """TripleDrawLowball27Definition is the class for 2-7 Triple Draw Lowball game definitions."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return Lowball27Evaluator(),

    def create_deck(self):
        return StandardDeck()


class KuhnPokerDefinition(Definition):
    """KuhnPokerDefinition is the class for Kuhn Poker game definitions."""

    def create_stages(self, game):
        return HoleDealingStage(False, 1, game), BettingStage(1, game), ShowdownStage(game)

    def create_evaluators(self):
        return RankEvaluator(),

    def create_deck(self):
        return Deck((Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE), Card(Rank.KING, Suit.SPADE)))
