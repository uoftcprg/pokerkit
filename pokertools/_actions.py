from abc import ABC, abstractmethod
from functools import partial
from operator import contains, is_not
from random import sample

from auxiliary import distinct, rotated
from gameframe.exceptions import GameFrameError
from gameframe.sequential import _SequentialAction

from pokertools.game import PokerPlayer


class PokerAction(_SequentialAction, ABC):
    def act(self):
        super().act()

        self.actor.game._update()


class DealingAction(PokerAction, ABC):
    def __init__(self, cards, actor):
        super().__init__(actor)

        self.cards = None if cards is None else tuple(cards)

    @property
    def deal_count(self):
        return self.actor.game.stage.deal_count

    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_dealing_stage():
            raise GameFrameError('not a dealing stage')

        if self.cards is not None:
            if not all(map(
                    partial(contains, self.actor.game.deck), self.cards,
            )):
                raise GameFrameError('some or one cards not in deck')
            elif not distinct(self.cards):
                raise GameFrameError('duplicates in cards')
            elif len(self.cards) != self.deal_count:
                raise GameFrameError(f'number of deals not {self.deal_count}.')

    def apply(self):
        if self.cards is None:
            self.cards = sample(self.actor.game.deck, self.deal_count)
        else:
            self.cards = self.cards

        self.actor.game._deck.draw(self.cards)
        self.deal()

    @abstractmethod
    def deal(self):
        ...


class HoleDealingAction(DealingAction):
    @property
    def deal_player(self):
        return next(filter(self.can_deal, self.actor.game.players))

    def can_deal(self, player):
        try:
            self.verify_player(player)
        except GameFrameError:
            return False

        return True

    def verify_player(self, player):
        if player.is_mucked():
            raise GameFrameError('deal to mucked player')
        elif len(player.hole) >= self.actor.game.stage.deal_target:
            raise GameFrameError('player already dealt')

    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_hole_dealing_stage():
            raise GameFrameError('not a hole dealing stage')

        self.verify_player(self.deal_player)

    def deal(self):
        player = self.deal_player
        player._hole.extend(self.cards)
        player._seen.extend(self.cards)


class BoardDealingAction(DealingAction):
    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_board_dealing_stage():
            raise GameFrameError('not a board dealing stage')
        elif len(self.actor.game.board) >= self.actor.game.stage.deal_target:
            raise GameFrameError('board already dealt')

    def deal(self):
        self.actor.game._board.extend(self.cards)


class BettingAction(PokerAction, ABC):
    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_betting_stage():
            raise GameFrameError('not a betting round')


class FoldAction(BettingAction):
    def verify(self):
        super().verify()

        if self.actor.bet >= max(map(
                PokerPlayer.bet.fget, self.actor.game.players,
        )):
            raise GameFrameError('redundant fold')

    def apply(self):
        self.actor._status = False


class CheckCallAction(BettingAction):
    @property
    def amount(self):
        return min(self.actor.stack, max(map(
            PokerPlayer.bet.fget, self.actor.game.players,
        )) - self.actor.bet)

    def apply(self):
        amount = self.amount

        self.actor._stack -= amount
        self.actor._bet += amount


class BetRaiseAction(BettingAction):
    def __init__(self, amount, actor):
        super().__init__(actor)

        self.amount = amount

    @property
    def min_amount(self):
        return self.actor.game.limit._min_amount

    @property
    def max_amount(self):
        return self.actor.game.limit._max_amount

    @property
    def pot_amount(self):
        return self.actor.game.limit._pot_amount

    def verify(self):
        super().verify()

        if self.actor.total <= max(map(
                PokerPlayer.bet.fget, self.actor.game.players,
        )):
            raise GameFrameError('player stack is covered')
        elif not any(map(PokerPlayer._is_relevant, filter(
                partial(is_not, self.actor), self.actor.game.players,
        ))):
            raise GameFrameError('redundant bet/raise')
        elif self.actor.game._bet_raise_count \
                == self.actor.game.limit._max_count:
            raise GameFrameError('too many bets/raises')

        if self.amount is not None:
            if self.amount < self.min_amount:
                raise GameFrameError('amount below min-bet/raise')
            elif self.amount > self.max_amount:
                raise GameFrameError('amount above max-bet/raise')

    def apply(self):
        if self.amount is None:
            self.amount = self.min_amount

        self.actor.game._aggressor = self.actor
        self.actor.game._max_delta = max(self.amount - max(map(
            PokerPlayer.bet.fget, self.actor.game.players,
        )), self.actor.game._max_delta)
        self.actor.game._bet_raise_count += 1

        self.actor._stack -= self.amount - self.actor.bet
        self.actor._bet = self.amount

        players = list(filter(PokerPlayer._is_relevant, rotated(
            self.actor.game.players, self.actor.index,
        )))

        if players and players[0] is self.actor:
            self.actor.game._queue = players[1:]
        else:
            self.actor.game._queue = players


class DiscardDrawAction(PokerAction):
    def __init__(self, discarded_cards, drawn_cards, actor):
        super().__init__(actor)

        self.discarded_cards = tuple(discarded_cards)
        self.drawn_cards = None if drawn_cards is None else tuple(drawn_cards)

    @property
    def population(self):
        population = list(self.actor.game.deck)

        if len(population) < len(self.discarded_cards):
            population.extend(self.actor.game.muck)

        return population

    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_discard_draw_stage():
            raise GameFrameError('not a draw round')
        elif not all(map(
                partial(contains, self.actor.hole), self.discarded_cards,
        )):
            raise GameFrameError('hole cards not in actor hole')

        if self.drawn_cards is None:
            if not distinct(self.discarded_cards):
                raise GameFrameError('duplicates in cards')
        else:
            if not all(map(
                    partial(contains, self.population), self.drawn_cards,
            )):
                raise GameFrameError('cards not in deck or muck if not enough')
            elif any(map(
                    partial(contains, self.actor.seen), self.drawn_cards,
            )):
                raise GameFrameError('drawing card previously seen')
            elif not distinct(self.discarded_cards + self.drawn_cards):
                raise GameFrameError('duplicates in cards')
            elif len(self.discarded_cards) != len(self.drawn_cards):
                raise GameFrameError('cannot match discarded cards with draws')

    def apply(self):
        if self.drawn_cards is None:
            self.drawn_cards = sample(
                tuple(set(self.population) - set(self.actor.seen)),
                len(self.discarded_cards),
            )

        self.actor.game._deck.draw(filter(
            partial(contains, self.actor.game.deck), self.drawn_cards,
        ))
        self.actor.game._muck.draw(filter(
            partial(contains, self.actor.game.muck), self.drawn_cards,
        ))
        self.actor.game._muck.extend(self.discarded_cards)
        self.actor._seen.extend(self.drawn_cards)

        for discarded_card, drawn_card in zip(
                self.discarded_cards, self.drawn_cards,
        ):
            index = self.actor.hole.index(discarded_card)
            self.actor._hole[index] = drawn_card


class ShowdownAction(PokerAction):
    def __init__(self, forced, actor):
        super().__init__(actor)

        self.forced = forced

    def is_necessary(self):
        staked = [True] * len(self.actor.game.evaluators)

        for player in self.actor.game.players:
            if player.is_shown():
                for i, (actor_hand, player_hand) in enumerate(zip(
                        self.actor.hands, player.hands,
                )):
                    if player_hand > actor_hand \
                            and player._put >= self.actor._put:
                        staked[i] = False

        return any(staked)

    def verify(self):
        super().verify()

        if not self.actor.game.stage.is_showdown_stage():
            raise GameFrameError('not in showdown')

    def apply(self):
        if self.forced is None:
            self.forced = self.is_necessary()

        self.actor._status = self.forced
