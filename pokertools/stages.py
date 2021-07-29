from abc import ABC
from functools import partial
from operator import eq

from auxiliary import rotate

from pokertools.game import PokerPlayer


class Stage(ABC):
    """Stage is the abstract base class for all stages.

    :param game: The poker game that this stage belongs in.
    """

    def __init__(self, game):
        self.__game = game

    @property
    def game(self):
        """Returns the game of this stage.

        :return: The game of this stage.
        """
        return self.__game

    def is_dealing_stage(self):
        """Returns whether or not this stage is a dealing stage.

        :return: True if this stage is a dealing stage, else False.
        """
        return isinstance(self, DealingStage)

    def is_hole_dealing_stage(self):
        """Returns whether or not this stage is a hole dealing stage.

        :return: True if this stage is a hole dealing stage, else False.
        """
        return isinstance(self, HoleDealingStage)

    def is_board_dealing_stage(self):
        """Returns whether or not this stage is a board dealing stage.

        :return: True if this stage is a board dealing stage, else False.
        """
        return isinstance(self, BoardDealingStage)

    def is_queued_stage(self):
        """Returns whether or not this stage is a queued stage.

        :return: True if this stage is a queued stage, else False.
        """
        return isinstance(self, QueuedStage)

    def is_betting_stage(self):
        """Returns whether or not this stage is a betting stage.

        :return: True if this stage is a betting stage, else False.
        """
        return isinstance(self, BettingStage)

    def is_discard_draw_stage(self):
        """Returns whether or not this stage is a discard and draw stage.

        :return: True if this stage is a discard and draw stage, else False.
        """
        return isinstance(self, DiscardDrawStage)

    def is_showdown_stage(self):
        """Returns whether or not this stage is a showdown stage.

        :return: True if this stage is a showdown stage, else False.
        """
        return isinstance(self, ShowdownStage)

    def _is_done(self):
        return self.game._is_folded()

    def _open(self):
        self.game._stage = self

    def _close(self):
        self.game._stage = None


class DealingStage(Stage, ABC):
    """DealingStage is the class for dealing stages.

    :param deal_count: The number of cards to be dealt in this stage.
    """

    def __init__(self, deal_count, game):
        super().__init__(game)

        self.__deal_count = deal_count

    @property
    def deal_target(self):
        """Returns the target number of cards to be dealt by the end of this stage.

        :return: The target number of cards to be dealt by the end of this stage.
        """
        count = 0

        for stage in self.game.stages[:self.game.stages.index(self) + 1]:
            if isinstance(stage, type(self)):
                count += stage.deal_count

        return count

    @property
    def deal_count(self):
        """Returns the number of cards to be dealt in this stage.

        :return: The number of cards to be dealt in this stage.
        """
        return self.__deal_count

    def _open(self):
        super()._open()

        self.game._actor = self.game.nature


class HoleDealingStage(DealingStage):
    """HoleDealingStage is the class for hole card dealing stages.

    :param status: The status of the hole card being dealt. True if the dealing is made face-up, False otherwise.
    :param deal_count: The number of hole cards to deal.
    """

    def __init__(self, status, deal_count, game):
        super().__init__(deal_count, game)

        self.__status = status

    @property
    def status(self):
        """Returns the status of the hole card being dealt in this hole dealing stage.

        True is returned if the dealing is made face-up. Otherwise, False is returned.

        :return: The status of the hole card being dealt.
        """
        return self.__status

    def _is_done(self):
        return super()._is_done() or all(map(
            partial(eq, self.deal_target),
            map(len, map(PokerPlayer.hole.fget, filter(PokerPlayer.is_active, self.game.players))),
        ))


class BoardDealingStage(DealingStage):
    """BoardDealingStage is the class for board card dealing stages."""

    def _is_done(self):
        return super()._is_done() or len(self.game.board) == self.deal_target


class QueuedStage(Stage, ABC):
    """QueuedStage is the abstract base class for all stages where players act in queued order."""

    def _is_done(self):
        return super()._is_done() or (self.game.stage is self and not self.game._queue)

    def _close(self):
        super()._close()

        self.game._queue.clear()


class BettingStage(QueuedStage):
    """BettingStage is the class for betting stages.

    :param big: True if this betting stage's min-raise is the big bet, else False. (Only relevant in fixed-limit games)
    """

    def __init__(self, big, game):
        super().__init__(game)

        self.__big = big

    @property
    def initial_bet_amount(self):
        """Returns the initial bet amount of this betting stage.

        The initial bet amount depends on the maximum value of the forced bets and whether or not this betting stage is
        a big betting stage and the game if fixed-limit.

        :return: The initial bet amount of this betting stage.
        """
        return self.game.big_bet if self.is_big() and self.game.limit.is_fixed_limit() else self.game.small_bet

    def is_big(self):
        """Returns whether or not this betting stage is a big betting stage.

        :return: True if this betting stage is big, else False.
        """
        return self.__big

    def _is_done(self):
        return super()._is_done() or self.game._is_all_in()

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer._is_relevant, self.game.players))
        blinded = any(map(PokerPlayer.bet.fget, players))

        self.game._aggressor = max(players, key=PokerPlayer.bet.fget)

        if blinded:
            opener = players[(players.index(self.game._aggressor) + 1) % len(players)]
        else:
            opener = self.game._aggressor

        self.game._actor, *self.game._queue = rotate(players, players.index(opener))
        self.game._bet_raise_count = int(blinded)
        self.game._max_delta = self.initial_bet_amount

    def _close(self):
        super()._close()

        self.game._collect()

        self._bet_raise_count = None
        self._max_delta = None

        if self.game._is_all_in():
            for player in filter(PokerPlayer.is_active, self.game.players):
                player._status = True


class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self):
        super()._open()

        self.game._actor, *self.game._queue = list(filter(PokerPlayer.is_active, self.game.players))


class ShowdownStage(QueuedStage):
    """ShowdownStage is the class for showdown stages."""

    def _is_done(self):
        return super()._is_done() or (self is not self.game.stage and self.game._is_all_in())

    def _open(self):
        super()._open()

        self.game._actor, *self.game._queue = list(filter(
            PokerPlayer.is_active,
            rotate(self.game.players, self.game._aggressor.index),
        ))
