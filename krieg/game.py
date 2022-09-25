"""This module defines the abstract base classes for all components of
games in Krieg.

These components are as follows:

- :class:`Game`
- :class:`Actor`
- :class:`Action`

All elements of games in Krieg should inherit from the above classes.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from auxiliary import SequenceView


class Game(ABC):
    """The abstract base class for all games.

    Every game has to define its nature and players.

    :param nature: The nature of this game.
    :param players: The players of this game.
    """

    def __init__(self, nature, players):
        self._nature = nature
        self._players = list(players)
        self._actions = []

    def __repr__(self):
        return f'<{type(self).__name__}>'

    @property
    def nature(self):
        """Return the nature of this game.

        Note that some games do not have nature.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.nature is None
        True

        :return: The nature of this game.
        """
        return self._nature

    @property
    def players(self):
        """Return the players of this game.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players
        SequenceView([X, O])

        :return: The players of this game.
        """
        return SequenceView(self._players)

    @property
    def actions(self):
        """Return the sequence of actions applied to this game.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.actions
        SequenceView([])
        >>> game.mark((0, 0), (0, 1))
        <TicTacToeGame>
        >>> game.actions
        SequenceView([<X: Mark 0, 0>, <O: Mark 0, 1>])

        :return: The number of actions applied to this game.
        """
        return SequenceView(self._actions)

    @property
    def action_count(self):
        """Return the number of actions applied to this game.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.action_count
        0
        >>> game.mark((0, 0), (0, 1))
        <TicTacToeGame>
        >>> game.action_count
        2

        :return: The number of actions applied to this game.
        """
        return len(self.actions)

    @abstractmethod
    def is_terminal(self):
        """Return the terminal status of this game.

        >>> from krieg.rockpaperscissors import (
        ...     RockPaperScissorsGame, RockPaperScissorsHand,
        ... )
        >>> game = RockPaperScissorsGame()
        >>> game.is_terminal()
        False
        >>> game.throw(RockPaperScissorsHand.PAPER, RockPaperScissorsHand.ROCK)
        <RockPaperScissorsGame>
        >>> game.is_terminal()
        True

        :return: ``True`` if this game is terminal, else ``False``.
        """
        ...


class Actor(Iterator):
    """The class for actors.

    :param game: The game of this actor.
    """

    def __init__(self, game):
        self._game = game

    def __next__(self):
        if self.is_player():
            return self.game.players[(self.index + 1) % len(self.game.players)]

        raise ValueError('no next player for nature')

    def __repr__(self):
        if self.is_nature():
            return f'<{type(self).__name__}>'
        elif self.is_player():
            return f'<{type(self).__name__} {self.index}>'

        raise ValueError('unknown actor type')

    @property
    def game(self):
        """Return the game of this actor.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[0].game is game
        True

        :return: The game of this actor.
        """
        return self._game

    @property
    def actions(self):
        """Return the sequence of actions applied by this actor.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[0].actions
        SequenceView([])
        >>> game.players[1].actions
        SequenceView([])
        >>> game.mark((0, 0), (0, 1), (0, 2))
        <TicTacToeGame>
        >>> game.players[0].actions
        SequenceView([<X: Mark 0, 0>, <X: Mark 0, 2>])
        >>> game.players[1].actions
        SequenceView([<O: Mark 0, 1>])

        :return: The number of actions applied to this game.
        """
        actions = []

        for action in self.game.actions:
            if action.actor == self:
                actions.append(action)

        return SequenceView(actions)

    @property
    def action_count(self):
        """Return the number of actions applied by this actor.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[0].action_count
        0
        >>> game.players[1].action_count
        0
        >>> game.mark((0, 0), (0, 1), (0, 2))
        <TicTacToeGame>
        >>> game.players[0].action_count
        2
        >>> game.players[1].action_count
        1

        :return: The number of actions applied to this game.
        """
        return len(self.actions)

    @property
    def index(self):
        """Return the optional index of this actor.

        If this actor is the nature, ``ValueError`` is thrown.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> print(game.players[0].index)
        0

        :return: ``None`` if this actor is the nature, else the index of
                 this player.
        """
        if self.is_player():
            return self.game.players.index(self)

        raise ValueError('no next player for nature')

    def is_nature(self):
        """Return whether if this actor is the nature.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[1].is_nature()
        False

        :return: ``True`` if this actor is the nature, else ``False``.
        """
        return self is self.game.nature

    def is_player(self):
        """Return whether if this actor is one of the players.

        >>> from krieg.tictactoe import TicTacToeGame
        >>> game = TicTacToeGame()
        >>> game.players[1].is_player()
        True

        :return: ``True`` if this actor is one of the players, else
                 ``False``.
        """
        return self in self.game.players


class Action(ABC):
    """The abstract base class for all actions."""

    @classmethod
    def create_methods(cls):
        act, can_act = (
            lambda *args, **kwargs: cls(*args, **kwargs).act(),
            lambda *args, **kwargs: cls(*args, **kwargs).can_act(),
        )

        act.__doc__ = f'Verify and apply :class:`{cls.__qualname__}` onto ' \
                      f'the game. {cls.__doc__}:return: ``None``.'

        can_act.__doc__ = f'Return whether if :class:`{cls.__qualname__}` ' \
                          f'can be applied onto the game. {cls.__doc__}' \
                          ':return: ``True`` if the action can be applied ' \
                          'onto the game, else ``False``.'

        return act, can_act

    def __init__(self, actor):
        self._actor = actor
        self._index = self.game.action_count

    @property
    def actor(self):
        """Return the actor of this action.

        :return: The actor of this action.
        """
        return self._actor

    @property
    def game(self):
        """Return the game of this action.

        :return: The game of this action.
        """
        return self.actor.game

    def act(self):
        """Verify and apply this action onto the game.

        :return: ``None``.
        """
        self._verify()
        self._apply()

    def can_act(self):
        """Return whether if this action can be applied onto the game.

        :return: ``True`` if this action can be applied onto the game,
                 else ``False``.
        """
        try:
            self._verify()
        except ValueError:
            return False

        return True

    def _verify(self):
        if self._index != self.game.action_count:
            raise ValueError('action outdated')
        elif self.game.is_terminal():
            raise ValueError('action on terminal game')

    def _apply(self):
        self.game._actions.append(self)
