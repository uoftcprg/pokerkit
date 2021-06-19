Interacting with Games
======================

In order to use the gameframe package in your project, you must first import it.

.. code-block:: python

   from gameframe import ...


All games implemented in gameframe share some attributes.

.. code-block:: python

   from gameframe.poker import NoLimitTexasHoldEm

   # Create a no-limit Texas Hold'em game.
   game = NoLimitTexasHoldEm(0, (1, 2), (200, 200, 200))

   # Get the nature.
   game.nature
   # Get the players.
   game.players
   # True if the game is terminal, else False.
   game.terminal


Interacting with Sequential games
---------------------------------

Almost all games (currently except rock paper scissors) are sequential games. They have an extra actor attribute that
can be accessed. It represents the current player to act.

.. code-block:: python

   from gameframe.poker import NoLimitTexasHoldEm

   # Create a no-limit Texas Hold'em game.
   game = NoLimitTexasHoldEm(0, (1, 2), (200, 200, 200))

   # Get the current actor (either None, the nature or one of the players).
   game.actor


Interacting with Poker games
----------------------------

Poker games in GameFrame uses `pokertools <https://pokertools.readthedocs.io/>`_ as the back-end framework for hand
evaluations and various types.

Actions in poker can be applied by calling the corresponding methods:

.. code-block:: python

   from pokertools import parse_cards

   from gameframe.poker import NoLimitTexasHoldEm

   # Create a no-limit Texas Hold'em game.
   game = NoLimitTexasHoldEm(0, (1, 2), (200, 200, 200))

   # Get the nature.
   nature = game.nature
   # Get the player.
   player = game.players[0]

   # Deal random hole cards to the player.
   nature.deal_hole(player)
   # Deal specified hole cards to the player.
   nature.deal_hole(player, parse_cards('Ac2d'))
   # Deal random cards to the board.
   nature.deal_board()
   # Deal specified cards to the board.
   nature.deal_board(parse_cards('KsKcKh'))

   # Fold
   player.fold()
   # Check/call
   player.check_call()
   # Min-bet/raise.
   player.bet_raise()
   # Bet/raise 30.
   player.bet_raise(30)
   # Show hand if necessary to win the pot.
   player.showdown()
   # Exact same as line above.
   player.showdown(False)
   # Show hand even if the player loses anyway
   player.showdown(True)
   # Stand pat.
   player.discard_draw()
   # Discard the specified cards and draw random cards.
   player.discard_draw(parse_cards('KsKcKh'))
   # Discard the specified cards and draw the specified cards.
   player.discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))


Whether each action can be applied can also be queried through the corresponding methods:

.. code-block:: python

   from pokertools import parse_cards

   from gameframe.poker import NoLimitTexasHoldEm

   game = NoLimitTexasHoldEm(0, (1, 2), (200, 200, 200))

   nature = game.nature
   player = game.players[0]

   # The stages of the game.
   game.stages
   # The evaluators of the game.
   game.evaluators
   # The limit of the game.
   game.limit
   # The ante of the game.
   game.ante
   # The blinds of the game.
   game.blinds
   # The starting stacks of the game.
   game.starting_stacks

   # The deck of the game.
   game.deck
   # The current stage of the game.
   game.stage
   # The pot of the game.
   game.pot
   # The board of the game.
   game.board
   # The side pots of the game.
   game.side_pots

   # An iterator of players that can be dealt hole cards.
   nature.dealable_players
   # The number of hole cards to be dealt to each player.
   nature.hole_deal_count
   # The number of cards to be dealt to the board.
   nature.board_deal_count

   # True if the nature can deal hole cards to any player, else False.
   nature.can_deal_hole()
   # True if the nature can deal hole cards to the specified player, else False.
   nature.can_deal_hole(player)
   # True if the nature can deal the specified hole cards to the specified player, else False.
   nature.can_deal_hole(player, parse_cards('Ac2d'))

   # True if the nature can deal cards to the board, else False.
   nature.can_deal_board()
   # True if the nature can deal the specified cards to the board, else False.
   nature.can_deal_board(parse_cards('KsKcKh'))

   # The bet of the player.
   player.bet
   # The stack of the player.
   player.stack
   # The hole cards of the player.
   player.hole
   # The starting stack of the player.
   player.starting_stack
   # The total amount the player has in front.
   player.total
   # The effective stack of the player.
   player.effective_stack
   # The amount put into the pot by the player.
   player.put
   # An iterator of the hands of the player.
   player.hands
   # Most poker games only have one evaluator. Get the first hand.
   next(player.hands)
   # True if the player has mucked, else False.
   player.mucked
   # True if the player has shown, else False.
   player.shown
   # True if the player is in the hand, else False.
   player.active

   # The check/call amount.
   player.check_call_amount
   # The maximum bet/raise amount.
   player.max_bet_raise_amount
   # The minimum bet/raise amount.
   player.min_bet_raise_amount
   # True if the player has to showdown to attempt to win the pot.
   player.showdown_necessary

   # True if the player can fold, else False.
   player.can_fold()
   # True if the player can check/call, else False.
   player.can_check_call()
   # True if the player can bet/raise any amount, else False.
   player.can_bet_raise()
   # True if the player can bet/raise the specified amount, else False.
   player.can_bet_raise(30)
   # True if the player can showdown, else False.
   player.can_showdown()
   # True if the player can showdown while showing if necessary (same as above), else False.
   player.can_showdown(False)
   # True if the player can showdown while force showing, else False.
   player.can_showdown(True)
   # True if the player can stand pat, else False.
   player.can_discard_draw()
   # True if the player can discard the specified cards and draw random cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'))
   # True if the player can discard the specified cards and draw the specified cards, else False.
   player.can_discard_draw(parse_cards('KsKcKh'), parse_cards('AsAcAh'))


Note that can_showdown(), can_showdown(False) and can_showdown(True) are basically the same things. They were just added
for the symmetry with actions.

The following code demonstrates interacting with No-Limit Texas Hold'em games.

.. literalinclude:: examples/dwan_ivey.py
   :language: python


The result of this poker game is as follows:

.. code-block:: console

   Pot: 1109500
   Players:
   Ivey: PokerPlayer(0, 572100, Ac2d)
   Antonius: PokerPlayer(0, 1997500)
   Dwan: PokerPlayer(0, 1109500, 7h6h)
   Board: Jc3d5c4hJh


Note that the pot is zero, as it is distributed back to the winning player.

The following code demonstrates interacting with Pot-Limit Omaha Hold'em games.

.. literalinclude:: examples/antonius_isildur.py
   :language: python


The result of this poker game is as follows:

.. code-block:: console

   Pot: 135694700
   Players:
   Antonius: PokerPlayer(0, 193792375, Ah3sKsKh)
   Isildur: PokerPlayer(0, 0)
   Board: 4s5c2h5h9c


The following code demonstrates interacting with No-Limit Short-Deck Hold'em games.

.. literalinclude:: examples/xuan_phua.py
   :language: python


The result of this poker game is as follows:

.. code-block:: console

   Pot: 623000
   Players:
   Badziakouski: PokerPlayer(0, 489000)
   Zhong: PokerPlayer(0, 226000)
   Xuan: PokerPlayer(0, 684000, QhQd)
   Jun: PokerPlayer(0, 400000)
   Phua: PokerPlayer(0, 0, KhKs)
   Koon: PokerPlayer(0, 198000)
   Board: 9h6cKcJhTs


All poker games can be interacted in an alternative way, using parsers. The following game is equivalent to the game
between Xuan and Phua shown just above.

.. literalinclude:: examples/xuan_phua_parser.py
   :language: python


The following code demonstrates interacting with Triple Draw 2 to 7 Lowball games.

.. literalinclude:: examples/yockey_arieh.py
   :language: python


The result of this poker game is as follows:

.. code-block:: console

   Pot: 2510000
   Players:
   Yockey: PokerPlayer(0, 0, 7h6c4c3d2c)
   Hui: PokerPlayer(0, 4190000)
   Esposito: PokerPlayer(0, 5910000)
   Arieh: PokerPlayer(0, 12095000, 2h4d7c5c3c)
   Board:


The following game is equivalent to the game between Yockey and Arieh shown just above.

.. literalinclude:: examples/yockey_arieh_parser.py
   :language: python


Interacting with Tic Tac Toe games
----------------------------------

I don't expect people to use GameFrame for Tic Tac Toe games, but this section will explain how to play tic tac toe
games.

.. code-block:: python

   from gameframe.tictactoe import TicTacToe

   game = TicTacToe()

   player = game.players[0]

   # Mark the coordinate.
   player.mark(1, 1)
   # True if the player can mark any coordinate.
   player.can_mark()
   # True if the player can mark the corresponding coordinate.
   player.can_mark(0, 0)

   # The board of the game.
   game.board
   # An iterator of empty coordinates of the game.
   game.empty_coordinates
   # The winner of the game (either None or one of the players).
   game.winner


The code below demonstrates a sample tic tac toe game.

.. literalinclude:: examples/tictactoe.py
   :language: python

The game result is as follows:

.. code-block:: console

   Board:
   X O X
   X O O
   O X O
   Winner: None


You can also use the parser, as demonstrated below:

.. literalinclude:: examples/tictactoe_parser.py
   :language: python


The game result is as follows:

.. code-block:: console

   Board:
   O    O    O
   X    X    None
   None None None
   Winner: O


Note that each poker player has a string representation of either 'X' or 'O'.


Interacting with Rock Paper Scissors games
------------------------------------------

Rock Paper Scissors game is the simplest game implemented on GameFrame. The following codes demonstrates how to use it.

.. code-block:: python

   from gameframe.rockpaperscissors import RockPaperScissors, RockPaperScissorsHand

   game = RockPaperScissors()
   player = game.players[0]

   # Throw the specified hand.
   player.throw(RockPaperScissorsHand.ROCK)
   # True if the player can throw any hand.
   player.can_throw()
   # True if the player can throw the specified hand.
   player.can_throw(RockPaperScissorsHand.SCISSORS)

   # The winner of the game (either None or one of the players).
   game.winner
   # The hand of the player.
   player.hand


This is a sample game.

.. literalinclude:: examples/rockpaperscissors.py
   :language: python


This code results in the following:

.. code-block:: console

   Hands: RockPaperScissorsHand.ROCK RockPaperScissorsHand.PAPER
   Winner: Second


For more information, you can look at the gameframe API documentations.
