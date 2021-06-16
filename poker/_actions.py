from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from random import sample
from typing import Optional, TypeVar, cast

from auxiliary import rotated, unique
from pokertools import Card, HoleCard

from gameframe.exceptions import GameFrameError
from gameframe.poker.bases import Poker, PokerNature, PokerPlayer
from poker.stages import (
    BettingStage, BoardDealingStage, DealingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage,
)
from gameframe.poker.utilities import _update
from gameframe.sequential import _SequentialAction

A = TypeVar('A', PokerNature, PokerPlayer)


class PokerAction(_SequentialAction[Poker, A], ABC):
    def act(self) -> None:
        super().act()

        _update(self.game)


class DealingAction(PokerAction[PokerNature], ABC):
    def __init__(self, cards: Optional[Iterable[Card]], actor: PokerNature):
        super().__init__(actor)

        self.cards: Optional[Sequence[Card]] = None if cards is None else tuple(cards)

    def verify(self) -> None:
        super().verify()

        if not isinstance(self.game.stage, DealingStage):
            raise GameFrameError('Dealing is only allowed in dealing stages')

        if self.cards is not None:
            if any(card not in self.game.deck for card in self.cards):
                raise GameFrameError('All cards dealt must be in deck')
            elif not unique(self.cards):
                raise GameFrameError('Card must not have any duplicates')
            elif len(self.cards) != self.game.stage._deal_count:
                raise GameFrameError(f'The number of dealt cards must be {self.game.stage._deal_count}.')

    def apply(self) -> None:
        super().apply()

        if self.cards is None:
            self.cards = sample(self.game.deck, self.game.stage._deal_count)
        else:
            self.cards = self.cards

        self.game._deck.draw(self.cards)
        self.deal(self.cards)

    @abstractmethod
    def deal(self, cards: Sequence[Card]) -> None:
        ...


class HoleDealingAction(DealingAction):
    def __init__(
            self,
            player: Optional[PokerPlayer],
            cards: Optional[Iterable[Card]],
            actor: PokerNature,
    ):
        super().__init__(cards, actor)

        self.player = player

    def verify(self) -> None:
        super().verify()

        if not isinstance(self.game.stage, HoleDealingStage):
            raise GameFrameError('Hole card dealing is not allowed')

        if self.player is not None:
            if self.player.mucked:
                raise GameFrameError('Cannot deal to a mucked player')
            elif len(self.player.hole) >= self.game.stage._deal_target(self.game):
                raise GameFrameError('The player must not have been dealt already')

    def deal(self, cards: Sequence[Card]) -> None:
        if self.player is None:
            self.player = next(self.actor.dealable_players)

        self.player._hole.extend(HoleCard(cast(HoleDealingStage, self.game.stage)._status, card) for card in cards)


class BoardDealingAction(DealingAction):
    def verify(self) -> None:
        super().verify()

        if not isinstance(self.game.stage, BoardDealingStage):
            raise GameFrameError('Board card dealing is not allowed')
        elif len(self.game.board) >= self.game.stage._deal_target(self.game):
            raise GameFrameError('The board must not have been dealt already')

    def deal(self, cards: Sequence[Card]) -> None:
        self.game._board.extend(cards)


class BettingAction(PokerAction[PokerPlayer], ABC):
    def verify(self) -> None:
        super().verify()

        if not isinstance(self.actor.game.stage, BettingStage):
            raise GameFrameError('Not a betting round')


class FoldAction(BettingAction):
    def verify(self) -> None:
        super().verify()

        if self.actor.bet >= max(player.bet for player in self.game.players):
            raise GameFrameError('Folding action must not be redundant')

    def apply(self) -> None:
        super().apply()

        self.actor._status = False


class CheckCallAction(BettingAction):
    def apply(self) -> None:
        super().apply()

        amount = self.actor.check_call_amount

        self.actor._stack -= amount
        self.actor._bet += amount


class BetRaiseAction(BettingAction):
    def __init__(self, amount: Optional[int], actor: PokerPlayer):
        super().__init__(actor)

        self.amount = amount

    def verify(self) -> None:
        super().verify()

        if max(player.bet for player in self.game.players) >= self.actor.total:
            raise GameFrameError('Cannot call when the stack of the player is covered')
        elif all(not player._relevant for player in self.game.players if player is not self.actor):
            raise GameFrameError('Cannot bet/raise when redundant')
        elif self.game._bet_raise_count == self.game.limit._max_count:
            raise GameFrameError('Too many number of bets/raises')

        if self.amount is not None:
            if not self.actor.min_bet_raise_amount <= self.amount <= self.actor.max_bet_raise_amount:
                raise GameFrameError('The bet/raise amount must be within allowed bounds')

    def apply(self) -> None:
        super().apply()

        if self.amount is None:
            self.amount = self.actor.min_bet_raise_amount

        self.game._aggressor = self.actor
        self.game._max_delta = max(self.game._max_delta, self.amount - max(player.bet for player in self.game.players))
        self.game._bet_raise_count += 1

        self.actor._stack -= self.amount - self.actor.bet
        self.actor._bet = self.amount

        players = [
            player for player in rotated(self.game.players, self.game.players.index(self.actor)) if player._relevant
        ]
        self.game._queue = players[1:] if players and players[0] is self.actor else players


class DiscardDrawAction(PokerAction[PokerPlayer]):
    def __init__(
            self,
            discarded_cards: Iterable[Card],
            drawn_cards: Optional[Iterable[Card]],
            actor: PokerPlayer,
    ) -> None:
        super().__init__(actor)

        self.discarded_cards = tuple(discarded_cards)
        self.drawn_cards = None if drawn_cards is None else tuple(drawn_cards)

    def verify(self) -> None:
        super().verify()

        if not isinstance(self.game.stage, DiscardDrawStage):
            raise GameFrameError('Not a draw round')
        elif any(card not in self.actor.hole for card in self.discarded_cards):
            raise GameFrameError('All hole cards must belong to the actor.')

        if self.drawn_cards is None:
            if not unique(self.discarded_cards):
                raise GameFrameError('Duplicates in cards')
        else:
            if any(card not in self.game.deck for card in self.drawn_cards):
                raise GameFrameError('Card not in deck')
            elif not unique(self.discarded_cards + self.drawn_cards):
                raise GameFrameError('Duplicates in cards')
            elif len(self.discarded_cards) != len(self.drawn_cards):
                raise GameFrameError('The from cards must be of same length as to cards.')

    def apply(self) -> None:
        super().apply()

        if self.drawn_cards is None:
            self.drawn_cards = tuple(sample(self.game.deck, len(self.discarded_cards)))

        self.game._deck.draw(self.drawn_cards)

        for discarded_card, drawn_card in zip(self.discarded_cards, self.drawn_cards):
            index = self.actor.hole.index(discarded_card)
            self.actor._hole[index] = HoleCard(self.actor.hole[index].status, drawn_card)


class ShowdownAction(PokerAction[PokerPlayer]):
    def __init__(self, forced_status: Optional[bool], actor: PokerPlayer) -> None:
        super().__init__(actor)

        self.forced_status = forced_status

    def verify(self) -> None:
        super().verify()

        if not isinstance(self.game.stage, ShowdownStage):
            raise GameFrameError('Game not in showdown')

    def apply(self) -> None:
        super().apply()

        if self.forced_status is None:
            self.forced_status = self.actor.showdown_necessary

        self.actor._status = self.forced_status
