from abc import ABC, abstractmethod
from functools import partial
from operator import contains, is_not
from random import sample

from auxiliary import distinct, rotated
from krieg.sequential import SequentialAction

from pokerface.game import PokerPlayer


class PokerAction(SequentialAction, ABC):
    def act(self):
        super().act()

        self.game._update()


class DealingAction(PokerAction, ABC):
    def __init__(self, actor, cards):
        super().__init__(actor)

        self.cards = None if cards is None else tuple(cards)

    @property
    def deal_count(self):
        return self.game.stage.deal_count

    def _verify(self):
        super()._verify()

        if not self.game.stage.is_dealing_stage():
            raise ValueError('not a dealing stage')

        if self.cards is not None:
            if not all(map(partial(contains, self.game.deck), self.cards)):
                raise ValueError('some or one cards not in deck')
            elif not distinct(self.cards):
                raise ValueError('duplicates in cards')
            elif len(self.cards) != self.deal_count:
                raise ValueError(f'number of deals not {self.deal_count}.')

    def _apply(self):
        super()._apply()

        if self.cards is None:
            self.cards = sample(self.game.deck, self.deal_count)
        else:
            self.cards = self.cards

        self.game._deck.draw(self.cards)
        self._deal()

    @abstractmethod
    def _deal(self):
        ...


class HoleDealingAction(DealingAction):
    @property
    def deal_player(self):
        return next(filter(self.can_deal, self.game.players))

    def can_deal(self, player):
        try:
            self._verify_player(player)
        except ValueError:
            return False

        return True

    def _verify_player(self, player):
        if player.is_mucked():
            raise ValueError('deal to mucked player')
        elif len(player.hole) >= self.game.stage.deal_target:
            raise ValueError('player already dealt')

    def _verify(self):
        super()._verify()

        if not self.game.stage.is_hole_dealing_stage():
            raise ValueError('not a hole dealing stage')

        self._verify_player(self.deal_player)

    def _deal(self):
        player = self.deal_player
        player._hole.extend(self.cards)
        player._seen.extend(self.cards)


class BoardDealingAction(DealingAction):
    def _verify(self):
        super()._verify()

        if not self.game.stage.is_board_dealing_stage():
            raise ValueError('not a board dealing stage')
        elif len(self.game.board) >= self.game.stage.deal_target:
            raise ValueError('board already dealt')

    def _deal(self):
        self.game._board.extend(self.cards)


class BettingAction(PokerAction, ABC):
    def _verify(self):
        super()._verify()

        if not self.game.stage.is_betting_stage():
            raise ValueError('not a betting round')


class FoldAction(BettingAction):
    def _verify(self):
        super()._verify()

        if self.actor.bet >= max(map(PokerPlayer.bet.fget, self.game.players)):
            raise ValueError('redundant fold')

    def _apply(self):
        super()._apply()

        self.actor._status = False


class CheckCallAction(BettingAction):
    @property
    def amount(self):
        return min(
            max(map(PokerPlayer.bet.fget, self.game.players)) - self.actor.bet,
            self.actor.stack,
        )

    def _apply(self):
        super()._apply()

        amount = self.amount

        self.actor._stack -= amount
        self.actor._bet += amount


class BetRaiseAction(BettingAction):
    def __init__(self, actor, amount):
        super().__init__(actor)

        self.amount = amount

    @property
    def min_amount(self):
        return self.game.limit._min_amount

    @property
    def max_amount(self):
        return self.game.limit._max_amount

    @property
    def pot_amount(self):
        return self.game.limit._pot_amount

    def _verify(self):
        super()._verify()

        if self.actor.total <= max(map(
                PokerPlayer.bet.fget, self.game.players,
        )):
            raise ValueError('player stack is covered')
        elif not any(map(PokerPlayer._is_relevant, filter(
                partial(is_not, self.actor), self.game.players,
        ))):
            raise ValueError('redundant bet/raise')
        elif self.game._bet_raise_count == self.game.limit._max_count:
            raise ValueError('too many bets/raises')

        if self.amount is not None:
            if self.amount < self.min_amount:
                raise ValueError('amount below min-bet/raise')
            elif self.amount > self.max_amount:
                raise ValueError('amount above max-bet/raise')

    def _apply(self):
        super()._apply()

        if self.amount is None:
            self.amount = self.min_amount

        self.game._aggressor = self.actor
        self.game._max_delta = max(
            self.amount - max(map(PokerPlayer.bet.fget, self.game.players)),
            self.game._max_delta,
        )
        self.game._bet_raise_count += 1

        self.actor._stack -= self.amount - self.actor.bet
        self.actor._bet = self.amount

        players = list(filter(PokerPlayer._is_relevant, rotated(
            self.game.players, self.actor.index,
        )))

        if players and players[0] is self.actor:
            self.game._queue = players[1:]
        else:
            self.game._queue = players


class DiscardDrawAction(PokerAction):
    def __init__(self, actor, discarded_cards, drawn_cards):
        super().__init__(actor)

        self.discarded_cards = tuple(discarded_cards)
        self.drawn_cards = None if drawn_cards is None else tuple(drawn_cards)

    @property
    def population(self):
        population = list(self.game.deck)

        if len(population) < len(self.discarded_cards):
            population.extend(self.game.muck)

        return population

    def _verify(self):
        super()._verify()

        if not self.game.stage.is_discard_draw_stage():
            raise ValueError('not a draw round')
        elif not all(map(
                partial(contains, self.actor.hole), self.discarded_cards,
        )):
            raise ValueError('hole cards not in actor hole')

        if self.drawn_cards is None:
            if not distinct(self.discarded_cards):
                raise ValueError('duplicates in cards')
        else:
            if not all(map(
                    partial(contains, self.population), self.drawn_cards,
            )):
                raise ValueError('cards not in deck or muck if not enough')
            elif any(map(
                    partial(contains, self.actor.seen), self.drawn_cards,
            )):
                raise ValueError('drawing card previously seen')
            elif not distinct(self.discarded_cards + self.drawn_cards):
                raise ValueError('duplicates in cards')
            elif len(self.discarded_cards) != len(self.drawn_cards):
                raise ValueError('cannot match discarded cards with draws')

    def _apply(self):
        super()._apply()

        if self.drawn_cards is None:
            self.drawn_cards = sample(
                tuple(set(self.population) - set(self.actor.seen)),
                len(self.discarded_cards),
            )

        self.game._deck.draw(filter(
            partial(contains, self.game.deck), self.drawn_cards,
        ))
        self.game._muck.draw(filter(
            partial(contains, self.game.muck), self.drawn_cards,
        ))
        self.game._muck.extend(self.discarded_cards)
        self.actor._seen.extend(self.drawn_cards)

        for discarded_card, drawn_card in zip(
                self.discarded_cards, self.drawn_cards,
        ):
            index = self.actor.hole.index(discarded_card)
            self.actor._hole[index] = drawn_card


class ShowdownAction(PokerAction):
    def __init__(self, actor, forced):
        super().__init__(actor)

        self.forced = forced

    def is_necessary(self):
        staked = [True] * len(self.game.evaluators)

        for player in filter(PokerPlayer.is_shown, self.game.players):
            for i, (actor_hand, player_hand) in enumerate(zip(
                    self.actor.hands, player.hands,
            )):
                if player_hand > actor_hand and player._put >= self.actor._put:
                    staked[i] = False

        return any(staked)

    def _verify(self):
        super()._verify()

        if not self.game.stage.is_showdown_stage():
            raise ValueError('not in showdown')

    def _apply(self):
        super()._apply()

        if self.forced is None:
            self.forced = self.is_necessary()

        self.actor._status = self.forced
