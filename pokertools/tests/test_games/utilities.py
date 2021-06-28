from abc import ABC, abstractmethod
from itertools import zip_longest

from gameframe.tests import GameFrameTestCaseMixin


class PokerTestCaseMixin(GameFrameTestCaseMixin, ABC):
    GAME_TYPE = None

    @classmethod
    def assert_terminal_poker_game(cls, game, statuses, stacks):
        assert game.is_terminal(), 'Game is not terminal'

        for player, status, stack in zip_longest(game.players, statuses, stacks):
            assert player._status == status, f'Status of player {player.index}: {player._status} does not equal {status}'
            assert player.stack == stack, f'Stack of player {player.index}: {player.stack} does not equal {stack}'

    def test_monte_carlo(self):
        ...

    def test_speed(self):
        ...

    def create_game(self):
        ...

    def act(self, game):
        ...

    def verify(self, game):
        ...

    @abstractmethod
    def test_hands(self):
        ...
