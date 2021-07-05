from abc import ABC

from pokertools.gameframe import PokerPlayer
from pokertools.limits import FixedLimit
from pokertools.utilities import _rotate


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

    def _is_done(self):
        return sum(map(PokerPlayer.is_active, self.game.players)) == 1

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
    def deal_count(self):
        """Returns the number of cards to be dealt in this stage.

        :return: The number of cards to be dealt in this stage.
        """
        return self.__deal_count

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

    def _open(self):
        super()._open()

        self.game._actor = self.game.nature


class HoleDealingStage(DealingStage):
    """HoleDealingStage is the class for hole card dealing stages.

    :param status: True if the dealing is made face-up, False otherwise.
    :param deal_count: The number of hole cards to deal.
    """

    def __init__(self, status, deal_count, game):
        super().__init__(deal_count, game)

        self._status = status

    def _is_done(self):
        return super()._is_done() or all(
            len(player.hole) == self.deal_target for player in filter(PokerPlayer.is_active, self.game.players)
        )


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
        max_value = max(self.game.ante, max(self.game.blinds, default=0))

        if self.is_big() and isinstance(self.game.limit, FixedLimit):
            return max_value * 2
        else:
            return max_value

    def is_big(self):
        """Returns whether or not this betting stage is a big betting stage.

        :return: True if this betting stage is big, else False.
        """
        return self.__big

    def _is_done(self):  # TODO: use is_all_in method
        return super()._is_done() or not any(map(PokerPlayer._is_relevant, self.game.players))

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer._is_relevant, self.game.players))
        blinded = any(map(PokerPlayer.bet.fget, players))

        self.game._aggressor = max(players, key=PokerPlayer.bet.fget)

        if blinded:
            opener = players[(players.index(self.game._aggressor) + 1) % len(players)]
        else:
            opener = self.game._aggressor

        self.game._actor = opener
        self.game._queue = _rotate(players, players.index(opener))[1:]
        self.game._bet_raise_count = int(blinded)
        self.game._max_delta = self.initial_bet_amount

    def _close(self):  # TODO: Reveal cards if all in
        from pokertools._actions import collect
        super()._close()

        collect(self.game)

        self._bet_raise_count = None
        self._max_delta = None


class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer.is_active, self.game.players))

        self.game._actor = players[0]
        self.game._queue = players[1:]


class ShowdownStage(QueuedStage):
    """ShowdownStage is the class for showdown stages."""

    # TODO: for is_done, if all in, skip

    def _open(self):  # TODO: aggressor is probably always not none when changes made, also remove opener (messy)
        super()._open()

        players = list(filter(PokerPlayer.is_active, self.game.players))

        if self.game._aggressor is None or self.game._aggressor not in players:
            opener = players[0]
        else:
            opener = self.game._aggressor

        self.game._actor = opener
        self.game._queue = _rotate(players, players.index(opener))[1:]
