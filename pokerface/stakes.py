from collections.abc import Mapping
from functools import partial
from operator import gt, truth

from auxiliary import MappingView


class Stakes:
    """The class for poker stakes. It contains information about various
    parameters of poker games, from ante, blinds to small bets and big
    bets.

    The term low-stakes, mid-stakes, and high-stakes just denote the
    magnitudes of the numeric values within the stakes.

    :param ante: The ante of this poker game.
    :param blinds: The blinds of this poker game.
    :param small_bet: The optional small bet of the poker stakes,
                      defaults to the maximum numeric value supplied.
    :param big_bet: The optional big bet of the poker stakes, defaults
                    to twice the small bet.
    """

    def __init__(self, ante, blinds, small_bet=None, big_bet=None):
        self._ante = ante

        if not isinstance(blinds, Mapping):
            blinds = enumerate(blinds)

        self._blinds = dict(blinds)

        max_value = max(self.ante, max(self.blinds.values(), default=0))

        if small_bet is None:
            self._small_bet = max_value
        else:
            self._small_bet = small_bet

        if big_bet is None:
            self._big_bet = 2 * self.small_bet
        else:
            self._big_bet = big_bet

        self._verify(max_value)

    @property
    def ante(self):
        """Return the ante of this poker game.

        :return: The ante of this poker game.
        """
        return self._ante

    @property
    def blinds(self):
        """Return the blinds of this poker game.

        Forced bets such as straddles and bring-ins are included in this
        property.

        :return: The blinds of this poker game.
        """
        return MappingView(self._blinds)

    @property
    def small_bet(self):
        """Return the small bet of this poker game.

        :return: The small bet of this poker game.
        """
        return self._small_bet

    @property
    def big_bet(self):
        """Return the big bet of this poker game.

        :return: The big bet of this poker game.
        """
        return self._big_bet

    def _verify(self, max_value):
        blinds = list(filter(truth, self.blinds.values()))

        if blinds != sorted(blinds):
            raise ValueError('non-zero blinds are not sorted')
        elif self.ante < 0:
            raise ValueError('ante is negative')
        elif any(map(partial(gt, 0), self.blinds.values())):
            raise ValueError('blind is negative')
        elif not max_value:
            raise ValueError('all values are zero')
        elif not max_value <= self.small_bet <= self.big_bet:
            raise ValueError('invalid configuration')
