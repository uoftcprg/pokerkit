from abc import ABC, abstractmethod


class Limit(ABC):
    """Limit is the abstract base class for all limits."""

    @property
    @abstractmethod
    def _max_count(self): ...

    def _get_min_amount(self, game):
        return min(max(player.bet for player in game.players) + game._max_delta, game.actor.total)

    @abstractmethod
    def _get_max_amount(self, game): ...


class FixedLimit(Limit):
    """FixedLimit is the class for fixed-limits."""

    _max_count = 4

    def _get_max_amount(self, game):
        return self._get_min_amount(game)


class PotLimit(Limit):
    """PotLimit is the class for pot-limits."""

    _max_count = None

    def _get_max_amount(self, game):
        bets = tuple(player.bet for player in game.players)
        amount = max(bets) + game.pot + sum(bets) + max(bets) - game.actor.bet
        min_amount = self._get_min_amount(game)
        max_amount = game.actor.total

        if amount < min_amount:
            return min_amount
        elif amount > max_amount:
            return max_amount
        else:
            return amount


class NoLimit(Limit):
    """NoLimit is the class for no-limits."""

    _max_count = None

    def _get_max_amount(self, game):
        return game.actor.total