from abc import ABC, abstractmethod

from gameframe.tests import GameFrameTestCaseMixin


class PokerTestCaseMixin(GameFrameTestCaseMixin, ABC):
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

    # @abstractmethod
    # def test_heads_up(self):
    #     ...
    #
    # @abstractmethod
    # def test_3_max(self):
    #     ...
    #
    # @abstractmethod
    # def test_6_max(self):
    #     ...
    #
    # @abstractmethod
    # def test_9_max(self):
    #     ...
