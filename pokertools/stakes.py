from collections.abc import Mapping


class Stakes:
    """Stakes is the class for poker stakes. It contains information about various parameters of poker games, from ante,
    blinds to small bets and big bets.

    The term low-stakes, mid-stakes, and high-stakes just denote the magnitudes of the numeric values within the stakes.

    :param ante: The ante of this poker game.
    :param blinds: The blinds of this poker game.
    :param small_bet: The optional small bet of the poker stakes, defaults to the maximum numeric value supplied.
    :param big_bet: The optional big bet of the poker stakes, defaults to twice the maximum numeric value supplied.
    """

    def __init__(self, ante, blinds, small_bet=None, big_bet=None):
        self.__ante = ante

        if isinstance(blinds, Mapping):
            self.__blinds = tuple(blinds[i] if i in blinds else 0 for i in range(max(blinds) + 1))
        else:
            self.__blinds = tuple(blinds)

        max_value = max(self.ante, max(self.blinds, default=0))

        self.__small_bet = max_value if small_bet is None else small_bet
        self.__big_bet = 2 * max_value if big_bet is None else big_bet

    @property
    def ante(self):
        return self.__ante

    @property
    def blinds(self):
        return self.__blinds

    @property
    def small_bet(self):
        return self.__small_bet

    @property
    def big_bet(self):
        return self.__big_bet
