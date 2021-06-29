from abc import ABC

from pokertools.gameframe import PokerPlayer
from pokertools.limits import FixedLimit
from pokertools.utilities import _rotate


class Stage(ABC):
    """Stage is the abstract base class for all stages."""

    def _is_done(self, game):
        return sum(map(PokerPlayer.is_active, game.players)) == 1

    def _open(self, game): ...

    def _close(self, game): ...


class DealingStage(Stage, ABC):
    """DealingStage is the class for dealing stages.

    :param deal_count: The number of cards to deal.
    """

    def __init__(self, deal_count):
        self._deal_count = deal_count

    def _get_deal_target(self, game):
        count = 0

        for stage in game.stages[:game.stages.index(self) + 1]:
            if isinstance(stage, type(self)):
                count += stage._deal_count

        return count

    def _open(self, game):
        super()._open(game)

        game._actor = game.nature


class HoleDealingStage(DealingStage):
    """HoleDealingStage is the class for hole card dealing stages.

    :param status: The status of the hole cards being dealt. True if the dealing is made face-up, False otherwise.
    :param deal_count: The number of hole cards to deal.
    """

    def __init__(self, status, deal_count):
        super().__init__(deal_count)

        self._status = status

    def _is_done(self, game):
        return super()._is_done(game) \
               or all(len(player.hole) == self._get_deal_target(game) for player in game.players if player.is_active())


class BoardDealingStage(DealingStage):
    """BoardDealingStage is the class for board card dealing stages."""

    def _is_done(self, game):
        return super()._is_done(game) or len(game.board) == self._get_deal_target(game)


class QueuedStage(Stage, ABC):
    """QueuedStage is the abstract base class for all stages where players act in queued order."""

    _deal_count = 0

    def _is_done(self, game):
        return super()._is_done(game) or (game.stage is self and not game._queue)

    def _close(self, game):
        super()._close(game)

        game._queue.clear()


class BettingStage(QueuedStage):
    """BettingStage is the class for betting stages.

    :param big: True if this betting stage's min-raise is the big bet, else False. (Only relevant in fixed-limit games)
    """

    def __init__(self, big):
        self._big = big

    def _is_done(self, game):
        return super()._is_done(game) or not any(map(PokerPlayer._is_relevant, game.players))

    def _open(self, game):
        super()._open(game)

        players = list(filter(PokerPlayer._is_relevant, game.players))
        max_blinded_player = max(players, key=lambda player: (player.bet, player.index))

        opener_index = (players.index(max_blinded_player) + 1) % len(players)

        game._actor = players[opener_index]
        game._queue = _rotate(players, opener_index)[1:]
        game._max_delta = max(game.ante, max(game.blinds, default=0))

        if self._big and isinstance(game.limit, FixedLimit):
            game._max_delta *= 2

        if any(map(PokerPlayer.bet.fget, game.players)):
            game._aggressor = max_blinded_player
            game._bet_raise_count = 1
        else:
            game._aggressor = game._actor
            game._bet_raise_count = 0

    def _close(self, game):
        from pokertools._actions import collect
        super()._close(game)

        collect(game)


class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self, game):
        super()._open(game)

        players = list(filter(PokerPlayer.is_active, game.players))
        opener = next(filter(PokerPlayer.is_active, game.players))

        game._actor = opener
        game._queue = _rotate(players, players.index(opener))[1:]


class ShowdownStage(QueuedStage):
    """ShowdownStage is the class for showdown stages."""

    def _open(self, game):
        super()._open(game)

        players = list(filter(PokerPlayer.is_active, game.players))

        if game._aggressor is None:
            opener = next(filter(PokerPlayer.is_active, game.players))
        else:
            opener = game._aggressor

        game._actor = opener
        game._queue = _rotate(players, players.index(opener))[1:]
