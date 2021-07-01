from abc import ABC

from pokertools.gameframe import PokerPlayer
from pokertools.limits import FixedLimit
from pokertools.utilities import _rotate


class Stage(ABC):
    """Stage is the abstract base class for all stages.

    :param game: The poker game that this stage belongs in.
    """

    def __init__(self, game):
        self._game = game

    def _is_done(self):
        return sum(map(PokerPlayer.is_active, self._game.players)) == 1

    def _open(self):
        self._game._stage = self

    def _close(self):
        self._game._stage = None


class DealingStage(Stage, ABC):
    """DealingStage is the class for dealing stages.

    :param deal_count: The number of cards to deal.
    """

    def __init__(self, deal_count, game):
        super().__init__(game)

        self._deal_count = deal_count

    @property
    def _deal_target(self):
        count = 0

        for stage in self._game.stages[:self._game.stages.index(self) + 1]:
            if isinstance(stage, type(self)):
                count += stage._deal_count

        return count

    def _open(self):
        super()._open()

        self._game._actor = self._game.nature


class HoleDealingStage(DealingStage):
    """HoleDealingStage is the class for hole card dealing stages.

    :param status: The status of the hole cards being dealt. True if the dealing is made face-up, False otherwise.
    :param deal_count: The number of hole cards to deal.
    """

    def __init__(self, status, deal_count, game):
        super().__init__(deal_count, game)

        self._status = status

    def _is_done(self):
        return super()._is_done() \
               or all(len(player.hole) == self._deal_target for player in self._game.players if player.is_active())


class BoardDealingStage(DealingStage):
    """BoardDealingStage is the class for board card dealing stages."""

    def _is_done(self):
        return super()._is_done() or len(self._game.board) == self._deal_target


class QueuedStage(Stage, ABC):
    """QueuedStage is the abstract base class for all stages where players act in queued order."""

    _deal_count = 0

    def _is_done(self):
        return super()._is_done() or (self._game.stage is self and not self._game._queue)

    def _close(self):
        super()._close()

        self._game._queue.clear()


class BettingStage(QueuedStage):
    """BettingStage is the class for betting stages.

    :param big: True if this betting stage's min-raise is the big bet, else False. (Only relevant in fixed-limit games)
    """

    def __init__(self, big, game):
        super().__init__(game)

        self._big = big

    def _is_done(self):
        return super()._is_done() or not any(map(PokerPlayer._is_relevant, self._game.players))

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer._is_relevant, self._game.players))

        self._game._aggressor = max(players, key=PokerPlayer.bet.fget)

        if any(map(PokerPlayer.bet.fget, players)):
            opener = players[(players.index(self._game._aggressor) + 1) % len(players)]
            self._game._bet_raise_count = 1
        else:
            opener = self._game._aggressor
            self._game._bet_raise_count = 0

        self._game._actor = opener
        self._game._queue = _rotate(players, players.index(opener))[1:]
        self._game._max_delta = max(self._game.ante, max(self._game.forced_bets, default=0))

        if self._big and isinstance(self._game.limit, FixedLimit):
            self._game._max_delta *= 2

    def _close(self):
        from pokertools._actions import collect
        super()._close()

        collect(self._game)


class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer.is_active, self._game.players))
        opener = next(filter(PokerPlayer.is_active, self._game.players))

        self._game._actor = opener
        self._game._queue = _rotate(players, players.index(opener))[1:]


class ShowdownStage(QueuedStage):
    """ShowdownStage is the class for showdown stages."""

    def _open(self):
        super()._open()

        players = list(filter(PokerPlayer.is_active, self._game.players))

        if self._game._aggressor is None or self._game._aggressor not in players:
            opener = players[0]
        else:
            opener = self._game._aggressor

        self._game._actor = opener
        self._game._queue = _rotate(players, players.index(opener))[1:]
