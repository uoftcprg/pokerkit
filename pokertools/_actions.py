from abc import ABC, abstractmethod
from functools import partial
from operator import is_not
from random import sample

from gameframe.exceptions import GameFrameError
from gameframe.sequential import _SequentialAction

from pokertools._utilities import distinct, rotate
from pokertools.gameframe import PokerPlayer
from pokertools.stages import (
    BettingStage, BoardDealingStage, DealingStage, DiscardDrawStage, HoleDealingStage, ShowdownStage,
)


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
            elif not distinct(self.cards):
                raise GameFrameError('Card must not have any duplicates')
            elif len(self.cards) != self.deal_count:
                raise GameFrameError(f'The number of dealt cards must be {self.deal_count}.')

    def apply(self):
        if self.cards is None:
            self.cards = sample(self.game.deck, self.deal_count)
        else:
            self.cards = self.cards

        self.game._deck.draw(self.cards)
        self.deal()

    @abstractmethod
    def deal(self):
        ...


class HoleDealingAction(DealingAction):
    @property
    def deal_player(self):
        return next(filter(self.can_deal, self.game.players))

    def verify_player(self, player):
        if player.is_mucked():
            raise GameFrameError('Cannot deal to a mucked player')
        elif len(player.hole) >= self.game.stage.deal_target:
            raise GameFrameError('The player must not have been dealt already')

    def can_deal(self, player):
        try:
            self.verify_player(player)
        except GameFrameError:
            return False
        else:
            return True

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, HoleDealingStage):
            raise GameFrameError('Hole card dealing is not allowed')

        self.verify_player(self.deal_player)

    def deal(self):
        player = self.deal_player
        player._hole.extend(self.cards)
        player._seen.extend(self.cards)


class BoardDealingAction(DealingAction):
    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, BoardDealingStage):
            raise GameFrameError('Board card dealing is not allowed')
        elif len(self.game.board) >= self.game.stage.deal_target:
            raise GameFrameError('The board must not have been dealt already')

    def deal(self):
        self.game._board.extend(self.cards)


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
            raise GameFrameError('Cannot bet/raise when the stack of the player is covered')
        elif not any(map(PokerPlayer._is_relevant, filter(partial(is_not, self.actor), self.game.players))):
            raise GameFrameError('Cannot bet/raise when redundant')
        elif self.game._bet_raise_count == self.game.limit._max_count:
            raise GameFrameError('Too many number of bets/raises')

        if self.amount is not None:
            if not self.min_amount <= self.amount <= self.max_amount:
                raise GameFrameError(
                    f'The bet/raise amount {self.amount} is not within [{self.min_amount}, {self.max_amount}]'
                )

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

        players = list(filter(PokerPlayer._is_relevant, rotate(self.game.players, self.actor.index)))
        self.game._queue = players[1:] if players and players[0] is self.actor else players


class DiscardDrawAction(PokerAction):
    def __init__(self, discarded_cards, drawn_cards, actor):
        super().__init__(actor)

        self.discarded_cards = tuple(discarded_cards)
        self.drawn_cards = None if drawn_cards is None else tuple(drawn_cards)

    @property
    def population(self):
        population = list(self.game.deck)

        if len(population) < len(self.discarded_cards):
            population.extend(self.game.muck)

        return population

    def verify(self):
        super().verify()

        if not isinstance(self.game.stage, DiscardDrawStage):
            raise GameFrameError('Not a draw round')
        elif not all(map(self.actor.hole.__contains__, self.discarded_cards)):
            raise GameFrameError('All hole cards must belong to the actor.')

        if self.drawn_cards is None:
            if not distinct(self.discarded_cards):
                raise GameFrameError('Duplicates in cards')
        else:
            if not all(map(self.population.__contains__, self.drawn_cards)):
                raise GameFrameError('All cards must be in deck (or the muck if insufficient)')
            elif any(map(self.actor.seen.__contains__, self.drawn_cards)):
                raise GameFrameError('The poker player should not draw any card they had before')
            elif not distinct(self.discarded_cards + self.drawn_cards):
                raise GameFrameError('Duplicates in cards')
            elif len(self.discarded_cards) != len(self.drawn_cards):
                raise GameFrameError('The discarded cards must be of same length as the drawn cards.')

    def apply(self):
        super().apply()

        if self.drawn_cards is None:
            self.drawn_cards = sample(set(self.population) - set(self.actor.seen), len(self.discarded_cards))

        self.game._deck.draw(filter(self.game.deck.__contains__, self.drawn_cards))
        self.game._muck.draw(filter(self.game.muck.__contains__, self.drawn_cards))

        self.game._muck.extend(self.discarded_cards)
        self.actor._seen.extend(self.drawn_cards)

        for discarded_card, drawn_card in zip(self.discarded_cards, self.drawn_cards):
            self.actor._hole[self.actor.hole.index(discarded_card)] = drawn_card


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
