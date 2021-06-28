from abc import ABC, abstractmethod

from gameframe.tests import GameFrameTestCaseMixin


class PokerTestCaseMixin(GameFrameTestCaseMixin, ABC):
    GAME_TYPE = None

    @classmethod
    def assert_terminal_poker_game(cls, game, statuses, stacks):
        assert game.is_terminal()

        for player, status, stack in zip(game.players, statuses, stacks):
            assert player._status == status
            assert player.stack == stack

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
    def test_heads_up(self):
        ...

    @abstractmethod
    def test_3_max(self):
        ...

    @abstractmethod
    def test_4_max(self):
        ...

    @abstractmethod
    def test_6_max(self):
        ...

    @abstractmethod
    def test_9_max(self):
        ...
