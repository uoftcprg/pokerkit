"""This module defines the abstract base classes for all elements of
sequential games in Krieg.

All elements of sequential games in Krieg should inherit from the
classes defined here.
"""

from abc import ABC

from krieg.game import Action, Actor, Game


class SequentialGame(Game, ABC):
    """The abstract base class for all sequential games.

    In sequential games, only one actor can act at a time. The current
    actor information is stored in the actor property. If a sequential
    game is terminal, its actor attribute must be set to ``None`` to
    denote such.

    :param nature: The nature of this game.
    :param players: The players of this game.
    :param actor: The initial actor of this game.
    """

    def __init__(self, nature, players, actor):
        super().__init__(nature, players)

        self._actor = actor

    @property
    def actor(self):
        """Return the current actor of this sequential game.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.actor
        X
        >>> game.actor.mark(0, 0)
        >>> game.actor
        O

        :return: ``None`` if this game is terminal, else the current
                 actor of this sequential game.
        """
        return self._actor

    def is_terminal(self):
        return self.actor is None


class SequentialActor(Actor):
    """The class for sequential actors.

    Sequential actors can only act in turn.
    """

    def is_actor(self):
        """Return whether if this actor is in turn to act.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[0].is_actor()
        True
        >>> game.players[1].is_actor()
        False
        >>> game.actor.mark(0, 0)
        >>> game.players[0].is_actor()
        False
        >>> game.players[1].is_actor()
        True

        :return: ``True`` if this actor is in turn to act, else
                 ``False``.
        """
        return self is self.game.actor


class SequentialAction(Action, ABC):
    """The abstract base class for all sequential actions."""

    def _verify(self):
        super()._verify()

        if not self.actor.is_actor():
            raise ValueError('actor out of turn')
