from collections.abc import Mapping
from functools import partial
from operator import gt


class Stakes:
    """Stakes is the class for poker stakes. It contains information about various parameters of poker games, from ante,
    blinds to small bets and big bets.

    The term low-stakes, mid-stakes, and high-stakes just denote the magnitudes of the numeric values within the stakes.

    :param ante: The ante of this poker game.
    :param blinds: The blinds of this poker game.
    :param small_bet: The optional small bet of the poker stakes, defaults to the maximum numeric value supplied.
    :param big_bet: The optional big bet of the poker stakes, defaults to twice the small bet.
    """

    def __init__(self, ante, blinds, small_bet=None, big_bet=None):
        self.__ante = ante

        if isinstance(blinds, Mapping):
            self.__blinds = tuple(blinds[i] if i in blinds else 0 for i in range(max(blinds) + 1))
        else:
            self.__blinds = tuple(blinds)

        max_value = max(self.ante, max(self.blinds, default=0))

        self.__small_bet = max_value if small_bet is None else small_bet
        self.__big_bet = 2 * self.small_bet if big_bet is None else big_bet

        self._verify(max_value)

    @property
    def ante(self):
        """Returns the ante of this poker game.

        :return: The ante of this poker game.
        """
        return self.__ante

    @property
    def blinds(self):
        """Returns the blinds of this poker game.

        Forced bets such as straddles and bring-ins are included in this property.

        :return: The blinds of this poker game.
        """
        return self.__blinds

    @property
    def small_bet(self):
        """Returns the small bet of this poker game.

        :return: The small bet of this poker game.
        """
        return self.__small_bet

    @property
    def big_bet(self):
        """Returns the big bet of this poker game.

        :return: The big bet of this poker game.
        """
        return self.__big_bet

    def _verify(self, max_value):
        filtered_bets = list(filter(bool, self.blinds))

        if filtered_bets != sorted(filtered_bets):
            raise ValueError('Forced bets must be sorted (except zero values)')
        elif self.ante < 0:
            raise ValueError('The ante must be a positive value')
        elif any(map(partial(gt, 0), self.blinds)):
            raise ValueError('The blinds must be positive values')
        elif not max_value:
            raise ValueError('At least one positive value must be supplied as the ante or the blinds')
        elif not max_value <= self.small_bet <= self.big_bet:
            raise ValueError('The maximum forced bets must be less than or equal to the small bet which, in turn, '
                             'should be less than or equal to the big bet')
