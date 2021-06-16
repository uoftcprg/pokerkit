from typing import cast, final

from auxiliary import bind

from gameframe.poker.bases import Limit, Poker, PokerPlayer


@final
class FixedLimit(Limit):
    """FixedLimit is the class for fixed-limits."""

    _max_count = 4

    def _max_amount(self, game: Poker) -> int:
        return self._min_amount(game)


@final
class PotLimit(Limit):
    """PotLimit is the class for pot-limits."""

    _max_count = None

    def _max_amount(self, game: Poker) -> int:
        bets = tuple(player.bet for player in game.players)
        actor = cast(PokerPlayer, game.actor)

        return bind(max(bets) + game.pot + sum(bets) + max(bets) - actor.bet, self._min_amount(game), actor.total)


@final
class NoLimit(Limit):
    """NoLimit is the class for no-limits."""

    _max_count = None

    def _max_amount(self, game: Poker) -> int:
        return cast(PokerPlayer, game.actor).total
