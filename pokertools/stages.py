from abc import ABC

from pokertools.limits import FixedLimit


class Stage(ABC):
    """Stage is the abstract base class for all stages."""

    def _is_done(self, game):
        return sum(player.active for player in game.players) == 1

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
               or all(len(player.hole) == self._get_deal_target(game) for player in game.players if player.active)


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
        return super()._is_done(game) or all(not player._relevant for player in game.players)

    def _open(self, game):
        super()._open(game)

        players = tuple(player for player in game.players if player._relevant)
        max_blinded_player = max(players, key=lambda player: (player.bet, player.index))

        opener_index = (max_blinded_player.index + 1) % len(players)

        game._actor = players[opener_index]
        game._queue = players[opener_index + 1:] + players[:opener_index]
        game._max_delta = max(game.ante, max(game.blinds, default=0))

        if self._big and isinstance(game.limit, FixedLimit):
            game._max_delta *= 2

        if any(player._bet for player in game.players):
            game._aggressor = max_blinded_player
            game._bet_raise_count = 1
        else:
            game._aggressor = game._actor
            game._bet_raise_count = 0

    def _close(self, game):
        from pokertools._actions import PokerAction
        super()._close(game)

        PokerAction.collect(game)


class DiscardDrawStage(QueuedStage):
    """DiscardDrawStage is the class for discard and draw stages."""

    def _open(self, game):
        super()._open(game)

        players = tuple(player for player in game.players if player.active)
        opener = next(player for player in game.players if player.active)

        game._actor = opener
        game._queue = players[opener.index + 1:] + players[:opener.index]


class ShowdownStage(QueuedStage):
    """ShowdownStage is the class for showdown stages."""

    def _open(self, game):
        super()._open(game)

        players = tuple(player for player in game.players if player.active)

        if game._aggressor is None or all(player.mucked or player.stack == 0 for player in game.players):
            opener = next(player for player in game.players if player.active)
        else:
            opener = game._aggressor

        game._actor = opener
        game._queue = players[opener.index + 1:] + players[:opener.index]
