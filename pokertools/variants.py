from abc import ABC, abstractmethod

from pokertools.cards import Card, Rank, Suit
from pokertools.decks import Deck, ShortDeck, StandardDeck
from pokertools.evaluators import (
    BadugiEvaluator, GreekEvaluator, Lowball27Evaluator, OmahaEvaluator, RankEvaluator, ShortDeckEvaluator,
    StandardEvaluator,
)
from pokertools.stages import BettingStage, BoardDealingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage


class Variant(ABC):
    """Variant is the abstract base class for all poker variants.

    Variants contain defines various information about their types of poker games.

    :param game: The game of this poker variant.
    """

    def __init__(self, game):
        self.__game = game

    @property
    def game(self):
        """Returns the game of this variant.

        :return: The game of this variant.
        """
        return self.__game

    @abstractmethod
    def create_stages(self):
        """Returns the stages of the poker game defined by this poker variant.

        :return: The stages of this poker variant.
        """
        ...

    @abstractmethod
    def create_evaluators(self):
        """Returns the evaluators of the poker game defined by this poker variant.

        :return: The evaluators of this poker variant.
        """
        ...

    @abstractmethod
    def create_deck(self):
        """Creates a deck of the poker game defined by this poker variant.

        :return: The created deck of this poker variant.
        """
        ...


class StaticHoleVariantMixin(Variant, ABC):
    """StaticHoleVariantMixin is the mixin for all game variants with a static number of hole cards."""

    @property
    @abstractmethod
    def hole_card_count(self):
        """Returns the number of hole cards belonging to each player.

        :return: The number of hole cards belonging to each player.
        """
        ...


class HoldEmVariant(StaticHoleVariantMixin, Variant, ABC):
    """HoldEmVariant is the abstract base class for all Hold'em game variants."""

    def create_stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count, self.game), BettingStage(False, self.game),
            BoardDealingStage(3, self.game), BettingStage(False, self.game),
            BoardDealingStage(1, self.game), BettingStage(True, self.game),
            BoardDealingStage(1, self.game), BettingStage(True, self.game),
            ShowdownStage(self.game),
        )


class TexasHoldEmVariant(HoldEmVariant):
    """TexasHoldEmVariant is the class for Texas Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return StandardEvaluator(),

    def create_deck(self):
        return StandardDeck()


class OmahaHoldEmVariant(HoldEmVariant):
    """OmahaHoldEmVariant is the class for Omaha Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 4

    def create_evaluators(self):
        return OmahaEvaluator(),

    def create_deck(self):
        return StandardDeck()


class FiveCardOmahaHoldEmVariant(OmahaHoldEmVariant):
    """FiveCardOmahaHoldEmVariant is the class for 5-Card Omaha Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 5


class SixCardOmahaHoldEmVariant(OmahaHoldEmVariant):
    """SixCardOmahaHoldEmVariant is the class for 6-Card Omaha Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 6


class GreekHoldEmVariant(HoldEmVariant):
    """GreekHoldEmVariant is the class for Greek Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return GreekEvaluator(),

    def create_deck(self):
        return StandardDeck()


class ShortDeckHoldEmVariant(HoldEmVariant):
    """ShortDeckHoldEmVariant is the class for Short-deck Hold'em game variants."""

    @property
    def hole_card_count(self):
        return 2

    def create_evaluators(self):
        return ShortDeckEvaluator(),

    def create_deck(self):
        return ShortDeck()


class DrawVariant(StaticHoleVariantMixin, Variant, ABC):
    """DrawVariant is the abstract base class for all draw game variants."""
    ...


class SingleDrawVariant(DrawVariant, ABC):
    """SingleDrawVariant is the abstract base class for all single draw game variants."""

    def create_stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count, self.game), BettingStage(False, self.game),
            DiscardDrawStage(self.game), BettingStage(True, self.game),
            ShowdownStage(self.game),
        )


class TripleDrawVariant(DrawVariant, ABC):
    """TripleDrawVariant is the abstract base class for all triple draw game variants."""

    def create_stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count, self.game), BettingStage(False, self.game),
            DiscardDrawStage(self.game), BettingStage(False, self.game),
            DiscardDrawStage(self.game), BettingStage(True, self.game),
            DiscardDrawStage(self.game), BettingStage(True, self.game),
            ShowdownStage(self.game),
        )


class FiveCardDrawVariant(SingleDrawVariant):
    """FiveCardDrawVariant is the class for Five-card Draw game variants."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return StandardEvaluator(),

    def create_deck(self):
        return StandardDeck()


class BadugiVariant(TripleDrawVariant):
    """BadugiVariant is the class for Badugi game variants."""

    @property
    def hole_card_count(self):
        return 4

    def create_evaluators(self):
        return BadugiEvaluator(),

    def create_deck(self):
        return StandardDeck()


class SingleDrawLowball27Variant(SingleDrawVariant):
    """SingleDrawLowball27Variant is the class for 2-7 Single Draw Lowball game variants."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return Lowball27Evaluator(),

    def create_deck(self):
        return StandardDeck()


class TripleDrawLowball27Variant(TripleDrawVariant):
    """TripleDrawLowball27Variant is the class for 2-7 Triple Draw Lowball game variants."""

    @property
    def hole_card_count(self):
        return 5

    def create_evaluators(self):
        return Lowball27Evaluator(),

    def create_deck(self):
        return StandardDeck()


class KuhnPokerVariant(Variant):
    """KuhnPokerVariant is the class for Kuhn Poker game variants."""

    def create_stages(self):
        return HoleDealingStage(False, 1, self.game), BettingStage(1, self.game), ShowdownStage(self.game)

    def create_evaluators(self):
        return RankEvaluator(),

    def create_deck(self):
        return Deck((Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE), Card(Rank.KING, Suit.SPADE)))
