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

    @property
    @abstractmethod
    def stages(self):
        """Returns the stages of the poker game defined by this poker definition.

        :return: The stages of this poker definition.
        """
        ...

    @property
    @abstractmethod
    def evaluators(self):
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


class StaticHoleMixin(Definition, ABC):
    """StaticHoleMixin is the mixin for all games with a static number of hole cards."""

    @property
    @abstractmethod
    def hole_card_count(self):
        """Returns the number of hole cards belonging to each player.

        :return: The number of hole cards belonging to each player.
        """
        ...


class HoldEm(StaticHoleMixin, Definition, ABC):
    """HoldEm is the abstract base class for all Hold'em games."""

    @property
    def stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count), BettingStage(False),
            BoardDealingStage(3), BettingStage(False),
            BoardDealingStage(1), BettingStage(True),
            BoardDealingStage(1), BettingStage(True),
            ShowdownStage(),
        )


class TexasHoldEm(HoldEm):
    """TexasHoldEm is the class for Texas Hold'em games."""

    @property
    def hole_card_count(self):
        return 2

    @property
    def evaluators(self):
        return StandardEvaluator()

    def create_deck(self):
        return StandardDeck()


class OmahaHoldEm(HoldEm):
    """OmahaHoldEm is the class for Omaha Hold'em games."""

    @property
    def hole_card_count(self):
        return 4

    @property
    def evaluators(self):
        return OmahaEvaluator()

    def create_deck(self):
        return StandardDeck()


class FiveCardOmahaHoldEm(OmahaHoldEm):
    """FiveCardOmahaHoldEm is the class for 5-Card Omaha Hold'em games."""

    @property
    def hole_card_count(self):
        return 5


class SixCardOmahaHoldEm(OmahaHoldEm):
    """SixCardOmahaHoldEm is the class for 6-Card Omaha Hold'em games."""

    @property
    def hole_card_count(self):
        return 6


class GreekHoldEm(HoldEm):
    """GreekHoldEm is the class for Greek Hold'em games."""

    @property
    def hole_card_count(self):
        return 2

    @property
    def evaluators(self):
        return GreekEvaluator()

    def create_deck(self):
        return StandardDeck()


class ShortDeckHoldEm(HoldEm):
    """ShortDeckHoldEm is the class for Short-deck Hold'em games."""

    @property
    def hole_card_count(self):
        return 2

    @property
    def evaluators(self):
        return ShortDeckEvaluator()

    def create_deck(self):
        return ShortDeck()


class Draw(StaticHoleMixin, Definition, ABC):
    """Draw is the abstract base class for all draw games."""
    ...


class SingleDraw(Draw, ABC):
    """SingleDraw is the abstract base class for all single draw games."""

    @property
    def stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count), BettingStage(False),
            DiscardDrawStage(), BettingStage(False),
            ShowdownStage(),
        )


class TripleDraw(Draw, ABC):
    """TripleDraw is the abstract base class for all triple draw games."""

    @property
    def stages(self):
        return (
            HoleDealingStage(False, self.hole_card_count), BettingStage(False),
            DiscardDrawStage(), BettingStage(False),
            DiscardDrawStage(), BettingStage(True),
            DiscardDrawStage(), BettingStage(True),
            ShowdownStage(),
        )


class FiveCardDraw(SingleDraw):
    """FiveCardDraw is the class for Five-Card Draw games."""

    @property
    def hole_card_count(self):
        return 5

    @property
    def evaluators(self):
        return StandardEvaluator()

    def create_deck(self):
        return StandardDeck()


class Badugi(TripleDraw):
    """Badugi is the class for Badugi games."""

    @property
    def hole_card_count(self):
        return 4

    @property
    def evaluators(self):
        return BadugiEvaluator()

    def create_deck(self):
        return StandardDeck()


class SingleDrawLowball27(SingleDraw):
    """SingleDrawLowball27 is the class for 2-7 Single Draw Lowball games."""

    @property
    def hole_card_count(self):
        return 5

    @property
    def evaluators(self):
        return Lowball27Evaluator()

    def create_deck(self):
        return StandardDeck()


class TripleDrawLowball27(TripleDraw):
    """TripleDrawLowball27 is the class for 2-7 Triple Draw Lowball games."""

    @property
    def hole_card_count(self):
        return 5

    @property
    def evaluators(self):
        return Lowball27Evaluator()

    def create_deck(self):
        return StandardDeck()


class Courchevel(Definition):
    """Courchevel is the class for Courchevel games."""

    @property
    def stages(self):
        return (
            HoleDealingStage(False, 5), BoardDealingStage(1), BettingStage(False),
            BoardDealingStage(2), BettingStage(False),
            BoardDealingStage(1), BettingStage(True),
            BoardDealingStage(1), BettingStage(True),
            ShowdownStage(),
        )

    @property
    def evaluators(self):
        return OmahaEvaluator()

    def create_deck(self):
        return StandardDeck()


class KuhnPoker(Definition):
    """KuhnPoker is the class for Kuhn Poker games."""

    @property
    def stages(self):
        return HoleDealingStage(False, 1), BettingStage(1), ShowdownStage()

    @property
    def evaluators(self):
        return RankEvaluator()

    def create_deck(self):
        return Deck((Card(Rank.JACK, Suit.SPADE), Card(Rank.QUEEN, Suit.SPADE), Card(Rank.KING, Suit.SPADE)))
