from abc import ABC, abstractmethod
from functools import partial
from random import sample

from gameframe.exceptions import GameFrameError
from gameframe.sequential import _SequentialAction

from pokertools.cards import HoleCard
from pokertools.gameframe import PokerPlayer
from pokertools.stages import (
    BettingStage, BoardDealingStage, DealingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage,
)
from pokertools.utilities import _rotate, _unique


class PokerAction(_SequentialAction, ABC):
    def act(self):
        super().act()

        self.game._update()


class DealingAction(PokerAction, ABC):
    def __init__(self, cards, actor):
        super().__init__(actor)

        self.cards = None if cards is None else tuple(cards)

    @property
    def deal_count(self):
        return self.game.stage.deal_count

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, DealingStage):
            raise GameFrameError('Dealing is only allowed in dealing stages')

        if self.cards is not None:
            if not all(map(self.game.deck.__contains__, self.cards)):
                raise GameFrameError('All cards dealt must be in deck')
            elif not _unique(self.cards):
                raise GameFrameError('Card must not have any duplicates')
            elif len(self.cards) != self.deal_count:
                raise GameFrameError(f'The number of dealt cards must be {self.deal_count}.')

    def apply(self):
        if self.cards is None:
            self.cards = sample(self.game.deck, self.deal_count)
        else:
            self.cards = self.cards

        self.game._deck.draw(self.cards)
        self.deal(self.cards)

    @abstractmethod
    def deal(self, cards):
        ...


class HoleDealingAction(DealingAction):
    def __init__(self, player, cards, actor):
        super().__init__(cards, actor)

        self.player = player

    @property
    def dealable_players(self):
        return filter(self.actor.can_deal_hole, self.game.players)

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, HoleDealingStage):
            raise GameFrameError('Hole card dealing is not allowed')

        if self.player is not None:
            if self.player.is_mucked():
                raise GameFrameError('Cannot deal to a mucked player')
            elif len(self.player.hole) >= self.game.stage.deal_target:
                raise GameFrameError('The player must not have been dealt already')
        elif self.cards is not None:
            raise GameFrameError('The player to deal to must be specified if cards are supplied')

    def deal(self, cards):
        if self.player is None:
            self.player = next(self.actor.dealable_players)

        self.player._hole.extend(map(partial(HoleCard, self.game.stage.status), cards))


class BoardDealingAction(DealingAction):
    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, BoardDealingStage):
            raise GameFrameError('Board card dealing is not allowed')
        elif len(self.game.board) >= self.game.stage.deal_target:
            raise GameFrameError('The board must not have been dealt already')

    def deal(self, cards):
        self.game._board.extend(cards)


class BettingAction(PokerAction, ABC):
    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, BettingStage):
            raise GameFrameError('Not a betting round')


class FoldAction(BettingAction):
    def verify(self):
        super().verify()

        if self.actor.bet >= max(map(PokerPlayer.bet.fget, self.game.players)):
            raise GameFrameError('Folding action must not be redundant')

    def apply(self):
        super().apply()

        self.actor._status = False


class CheckCallAction(BettingAction):
    @property
    def amount(self):
        return min(self.actor.stack, max(map(PokerPlayer.bet.fget, self.game.players)) - self.actor.bet)

    def apply(self):
        super().apply()

        amount = self.amount

        self.actor._stack -= amount
        self.actor._bet += amount


class BetRaiseAction(BettingAction):
    def __init__(self, amount, actor):
        super().__init__(actor)

        self.amount = amount

    @property
    def min_amount(self):
        return self.game.limit._min_amount

    @property
    def max_amount(self):
        return self.game.limit._max_amount

    def verify(self):
        super().verify()

        if max(map(PokerPlayer.bet.fget, self.game.players)) >= self.actor.total:
            raise GameFrameError('Cannot call when the stack of the player is covered')
        elif not any(map(PokerPlayer._is_relevant, self.game.players)):
            raise GameFrameError('Cannot bet/raise when redundant')
        elif self.game._bet_raise_count == self.game.limit._max_count:
            raise GameFrameError('Too many number of bets/raises')

        if self.amount is not None:
            if not self.min_amount <= self.amount <= self.max_amount:
                raise GameFrameError('The bet/raise amount must be within allowed bounds')

    def apply(self):
        super().apply()

        if self.amount is None:
            self.amount = self.min_amount

        self.game._aggressor = self.actor
        self.game._max_delta = max(
            self.game._max_delta,
            self.amount - max(map(PokerPlayer.bet.fget, self.game.players)),
        )
        self.game._bet_raise_count += 1

        self.actor._stack -= self.amount - self.actor.bet
        self.actor._bet = self.amount

        players = list(filter(PokerPlayer._is_relevant, _rotate(self.game.players, self.actor.index)))
        self.game._queue = players[1:] if players and players[0] is self.actor else players


class DiscardDrawAction(PokerAction):
    def __init__(self, discarded_cards, drawn_cards, actor):
        super().__init__(actor)

        self.discarded_cards = tuple(discarded_cards)
        self.drawn_cards = None if drawn_cards is None else tuple(drawn_cards)

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, DiscardDrawStage):
            raise GameFrameError('Not a draw round')
        elif not all(map(self.actor.hole.__contains__, self.discarded_cards)):
            raise GameFrameError('All hole cards must belong to the actor.')

        if self.drawn_cards is None:
            if not _unique(self.discarded_cards):
                raise GameFrameError('Duplicates in cards')
        else:
            if not all(map(self.game.deck.__contains__, self.drawn_cards)):
                raise GameFrameError('Card not in deck')
            elif not _unique(self.discarded_cards + self.drawn_cards):
                raise GameFrameError('Duplicates in cards')
            elif len(self.discarded_cards) != len(self.drawn_cards):
                raise GameFrameError('The from cards must be of same length as to cards.')

    def apply(self):
        super().apply()

        if self.drawn_cards is None:
            self.drawn_cards = sample(self.game.deck, len(self.discarded_cards))

        self.game._deck.draw(self.drawn_cards)

        for discarded_card, drawn_card in zip(self.discarded_cards, self.drawn_cards):
            index = self.actor.hole.index(discarded_card)
            self.actor._hole[index] = HoleCard(self.actor.hole[index].status, drawn_card)


class ShowdownAction(PokerAction):
    def __init__(self, forced, actor):
        super().__init__(actor)

        self.forced = forced

    def is_necessary(self):
        staked = [True] * len(self.game.evaluators)

        for player in self.game.players:
            if player.is_shown():
                for i, (actor_hand, player_hand) in enumerate(zip(self.actor.hands, player.hands)):
                    if player_hand > actor_hand and player._put >= self.actor._put:
                        staked[i] = False

        return any(staked)

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, ShowdownStage):
            raise GameFrameError('Game not in showdown')

    def apply(self):
        super().apply()

        if self.forced is None:
            self.forced = self.is_necessary()

        self.actor._status = self.forced
