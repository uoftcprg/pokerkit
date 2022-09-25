Base Game Classes
=================

All games implemented in krieg share some attributes. In general, there
are two classes of games:

  - Non-sequential games: :mod:`krieg.game`
  - Sequential games: :mod:`krieg.sequential`

All games implemented on krieg are of the above game types.

Non-sequential Games
--------------------

Non-sequential games are of type :class:`krieg.game.Game`. The games
contain actors (a nature, and players) that are of type
:class:`krieg.game.Actor`. They have the following attributes,
properties, and methods that can be accessed from the game and actor
instances.

.. code-block:: python

   from krieg.rockpaperscissors import RockPaperScissorsGame

   # Create a game.
   game = RockPaperScissorsGame()

   # Get the nature.
   game.nature
   # Get the players.
   game.players
   # True if the game is terminal, else False.
   game.is_terminal()

   # Get the first player.
   actor = game.players[0]

   # The game of this actor.
   actor.game
   # None if this actor is the nature, else the index of this player.
   actor.index
   # True if the actor is the nature, else False.
   actor.is_nature()
   # True if the actor is one of the players, else False.
   actor.is_player()

Natures represent an element of chance or a neutral observer. Currently,
all implemented games have natures that are irrelevant to the gameplay.
However, in many games, one such example being poker, the nature play a
crucial role in the gameplay.

Sequential Games
----------------

Sequential games are of type :class:`krieg.sequential.SequentialGame`,
which inherits from :class:`krieg.game.Game`. So, all attributes and
methods present in those base classes are also present in sequential
game instances. The same applies to sequential actors, which are of type
:class:`krieg.sequential.SequentialActor`.

Sequential game instances have an extra attribute called
:attr:`krieg.sequential.SequentialGame.actor`. It represents the current
player to act. This property is ``None`` when the game is terminal.

.. code-block:: python

   from krieg.tictactoe import TicTacToeGame

   # Create a sequential game.
   game = TicTacToeGame()

   # Get the current actor (None if terminal).
   game.actor

   # Get the second player.
   actor = game.players[1]

   # True if this actor is in turn to act, else False.
   actor.is_actor()

Game Implementations
--------------------

The above classes provide a basic framework on top of which you can
build basic games on. Game actions are typically implemented as methods
of a nature or players in the games. Some example games are already
implemented and are explained in the later section.
