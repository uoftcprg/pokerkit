from abc import ABC
from typing import final

from auxiliary import after, rotated

from gameframe.poker.bases import Poker, Stage
from gameframe.poker.utilities import _collect


class DealingStage(Stage, ABC):
    """DealingStage is the class for dealing stages.

    :param deal_count: The number of cards to deal.
    """

    def __init__(self, deal_count: int):
        self._deal_count = deal_count

    def _open(self, game: Poker) -> None:
        super()._open(game)

        game._actor = game.nature


@final
class HoleDealingStage(DealingStage):
    """HoleDealingStage is the class for hole card dealing stages.

    :param status: The status of the hole cards being dealt. True if the dealing is made face-up, False otherwise.
    :param deal_count: The number of hole cards to deal.
    """

    def __init__(self, status: bool, deal_count: int):
        super().__init__(deal_count)

        self._status = status

    def _done(self, game: Poker) -> bool:
        return super()._done(game) \
               or all(len(player.hole) == self._deal_target(game) for player in game.players if player.active)


@final
class BoardDealingStage(DealingStage):
    """BoardDealingStage is the class for board card dealing stages."""

    def _done(self, game: Poker) -> bool:
        return super()._done(game) or len(game.board) == self._deal_target(game)


class QueuedStage(Stage):
    """QueuedStage is the class for stages where players act in queued order."""

    _deal_count = 0

    def _done(self, game: Poker) -> bool:
        return super()._done(game) or (game.stage is self and not game._queue)

    def _close(self, game: Poker) -> None:
        super()._close(game)

        game._queue.clear()


@final
class BettingStage(QueuedStage, ABC):
    """BettingStage is the class for betting stages.

    :param initial_max_delta: The initial min-raise amount.
    """

    def __init__(self, initial_max_delta: int):
        self.__initial_max_delta = initial_max_delta

    def _done(self, game: Poker) -> bool:
        return super()._done(game) or all(not player._relevant for player in game.players)

    def _open(self, game: Poker) -> None:
        super()._open(game)

        players = tuple(player for player in game.players if player._relevant)
        opener = after(players, max(players, key=lambda player: (player.bet, game.players.index(player))), True)

        game._actor = opener
        game._queue = list(rotated(players, players.index(opener)))[1:]
        game._max_delta = self.__initial_max_delta

        if any(player._bet for player in game.players):
            game._bet_raise_count = 1
        else:
            game._aggressor = opener
            game._bet_raise_count = 0

    def _close(self, game: Poker) -> None:
        super()._close(game)

        _collect(game)


@final
class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self, game: Poker) -> None:
        super()._open(game)

        players = tuple(player for player in game.players if player.active)
        opener = next(player for player in game.players if player.active)

        game._actor = opener
        game._queue = list(rotated(players, players.index(opener)))[1:]


@final
class ShowdownStage(QueuedStage):
    def _open(self, game: Poker) -> None:
        super()._open(game)

        players = tuple(player for player in game.players if player.active)

        if game._aggressor is None or all(player.mucked or player.stack == 0 for player in game.players):
            opener = next(player for player in game.players if player.active)
        else:
            opener = game._aggressor

        game._actor = opener
        game._queue = list(rotated(players, players.index(opener)))[1:]
