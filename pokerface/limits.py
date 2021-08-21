from abc import ABC, abstractmethod

from auxiliary import clip

from pokerface.game import PokerPlayer


class Limit(ABC):
    """The abstract base class for all limits."""

    def __init__(self, game):
        self._game = game

    @property
    def game(self):
        """Return the game of this limit.

        :return: The game of this limit.
        """
        return self._game

    @property
    def _min_amount(self):
        max_bet = 0

        for player in self.game.players:
            max_bet = max(max_bet, player.bet)

        return min(max_bet + self.game._max_delta, self.game.actor.total)

    @property
    def _pot_amount(self):
        return clip(self._pot_amount_raw, self._min_amount, self._max_amount)

    @property
    def _pot_amount_raw(self):
        bets = tuple(map(PokerPlayer.bet.fget, self.game.players))

        return 2 * max(bets) + sum(bets) - self.game.actor.bet + self.game.pot

    @property
    @abstractmethod
    def _max_amount(self): ...

    @property
    @abstractmethod
    def _max_count(self): ...

    def is_fixed_limit(self):
        """Return whether or not this limit is a fixed limit.

        :return: ``True`` if this limit is a fixed limit, else
                 ``False``.
        """
        return isinstance(self, FixedLimit)

    def is_pot_limit(self):
        """Return whether or not this limit is a pot limit.

        :return: ``True`` if this limit is a pot limit, else ``False``.
        """
        return isinstance(self, PotLimit)

    def is_no_limit(self):
        """Return whether or not this limit is a no limit.

        :return: ``True`` if this limit is a no limit, else ``False``.
        """
        return isinstance(self, NoLimit)


class FixedLimit(Limit):
    """The class for fixed-limits."""

    @property
    def _max_amount(self):
        return self._min_amount

    @property
    def _max_count(self):
        return 4


class PotLimit(Limit):
    """The class for pot-limits."""

    @property
    def _max_amount(self):
        return clip(
            self._pot_amount_raw, self._min_amount, self.game.actor.total,
        )

    @property
    def _max_count(self):
        return None


class NoLimit(Limit):
    """The class for no-limits."""

    @property
    def _max_amount(self):
        return self.game.actor.total

    @property
    def _max_count(self):
        return None
