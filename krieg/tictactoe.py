"""This module defines various components of tic-tac-toe."""

from random import choice

from auxiliary import SequenceView, next_or_none

from krieg.sequential import SequentialAction, SequentialActor, SequentialGame


class TicTacToeGame(SequentialGame):
    """The class for tic-tac-toe games."""

    def __init__(self):
        players = TicTacToePlayer(self), TicTacToePlayer(self)

        super().__init__(None, players, players[0])

        self._board = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

    @property
    def board(self):
        """Return the board of this tic-tac-toe game.

        >>> game = TicTacToeGame()
        >>> for row in game.board:
        ...     print('| ', end='')
        ...     for cell in row:
        ...         print('.' if cell is None else cell, end=' ')
        ...     print('|')
        ...
        | . . . |
        | . . . |
        | . . . |
        >>> game.mark((0, 0), (0, 1), (1, 0))
        <TicTacToeGame>
        >>> for row in game.board:
        ...     print('| ', end='')
        ...     for cell in row:
        ...         print('.' if cell is None else cell, end=' ')
        ...     print('|')
        ...
        | X O . |
        | X . . |
        | . . . |

        :return: The board of this tic-tac-toe game.
        """
        return SequenceView(list(map(SequenceView, self._board)))

    @property
    def winner(self):
        """Return the winner of this tic-tac-toe game.

        >>> game = TicTacToeGame()
        >>> game.winner is None
        True
        >>> game.mark((0, 0), (0, 1), (1, 0), (1, 1), (2, 0))
        <TicTacToeGame>
        >>> for row in game.board:
        ...     print('| ', end='')
        ...     for cell in row:
        ...         print('.' if cell is None else cell, end=' ')
        ...     print('|')
        ...
        | X O . |
        | X O . |
        | X . . |
        >>> game.winner
        X

        :return: The winning player of the tic-tac-toe game if there is
                 one, else ``None``.
        """
        for i in range(3):
            if self.board[i][0] is self.board[i][1] is self.board[i][2] \
                    is not None:
                return self.board[i][0]
            elif self.board[0][i] is self.board[1][i] is self.board[2][i] \
                    is not None:
                return self.board[0][i]

        if self.board[1][1] is not None and (
                self.board[0][0] is self.board[1][1] is self.board[2][2]
                or self.board[0][2] is self.board[1][1] is self.board[2][0]
        ):
            return self.board[1][1]

        return None

    @property
    def loser(self):
        """Return the loser of this tic-tac-toe game.

        >>> game = TicTacToeGame()
        >>> game.loser is None
        True
        >>> game.mark((0, 0), (1, 0), (0, 1), (1, 1), (0, 2))
        <TicTacToeGame>
        >>> for row in game.board:
        ...     print('| ', end='')
        ...     for cell in row:
        ...         print('.' if cell is None else cell, end=' ')
        ...     print('|')
        ...
        | X X X |
        | O O . |
        | . . . |
        >>> game.loser
        O

        :return: The losing player of the tic-tac-toe game if there is
                 one, else ``None``.
        """
        return None if self.winner is None else next(self.winner)

    @property
    def empty_cell_locations(self):
        """Return the empty cell locations of the board of this
        tic-tac-toe game.

        >>> game = TicTacToeGame()
        >>> game.mark((2, 2))
        <TicTacToeGame>
        >>> tuple(game.empty_cell_locations)
        ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1))
        >>> game.mark((0, 0), (0, 1), (1, 0))
        <TicTacToeGame>
        >>> tuple(game.empty_cell_locations)
        ((0, 2), (1, 1), (1, 2), (2, 0), (2, 1))

        :return: An iterator of the empty coordinates of the board.
        """
        for r in range(3):
            for c in range(3):
                if self.board[r][c] is None:
                    yield r, c

    def mark(self, *locations):
        """Mark the cells corresponding to the given locations in the
        board of this tic-tac-toe game.

        >>> game = TicTacToeGame()
        >>> game.mark((1, 1), (0, 0), (0, 2), (2, 0), (1, 0))
        <TicTacToeGame>
        >>> for row in game.board:
        ...     print('| ', end='')
        ...     for cell in row:
        ...         print('.' if cell is None else cell, end=' ')
        ...     print('|')
        ...
        | O . X |
        | X X . |
        | O . . |

        :param locations: The locations to mark.
        :return: This game.
        """
        for r, c in locations:
            self.actor.mark(int(r), int(c))

        return self


class MarkingAction(SequentialAction):
    """MarkingAction is a class for marking actions in tic-tac-toe
    games.

    Note that the marked cell locations are optionally passed as
    arguments to the function. Either both the row and column
    coordinates or none of them must be specified.

    :param r: The optional row coordinate of the marked cell.
    :param c: The optional column coordinate of the marked cell.
    """

    def __init__(self, actor, r=None, c=None):
        super().__init__(actor)

        self.r = r
        self.c = c

    def __repr__(self):
        return f'<{self.actor.symbol}: Mark {self.r}, {self.c}>'

    def _verify(self):
        super()._verify()

        if self.r is not None and self.c is not None:
            if not (0 <= self.r < 3 and 0 <= self.c < 3):
                raise ValueError('coordinates exceed bounds of [0, 3)')
            elif self.game.board[self.r][self.c] is not None:
                raise ValueError('cell not empty')
        elif self.r is not None or self.c is not None:
            raise ValueError('only one of r and c provided')

    def _apply(self):
        super()._apply()

        if self.r is None or self.c is None:
            self.r, self.c = choice(tuple(self.game.empty_cell_locations))

        self.game._board[self.r][self.c] = self.actor

        if next_or_none(self.game.empty_cell_locations) is not None \
                and self.game.winner is None:
            self.game._actor = next(self.actor)
        else:
            self.game._actor = None


class TicTacToePlayer(SequentialActor):
    """The class for tic-tac-toe players."""

    mark, can_mark = MarkingAction.create_methods()

    def __repr__(self):
        return self.symbol

    @property
    def symbol(self):
        """Return the symbol of this tic-tac-toe player either ``X`` or
        ``O``.

        :return: ``X`` if this player is the first player, ``O``
                 otherwise.
        """
        return 'X' if self.game.players[0] is self else 'O'
