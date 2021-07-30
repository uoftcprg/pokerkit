Sample Hands with PokerTools
============================

Using the attributes, properties, and methods shown in the previous
section, you have all the knowledge you need to play games on
PokerTools.

Example Hand with Showdown
--------------------------

This is a sample hand that serves as a good introduction to the
PokerTools package.

.. code-block:: python

   from pokertools import *

   game = NoLimitTexasHoldEm(Stakes(0, (1, 2)), (200, 200, 200))
   sb, bb, btn = game.players

   # Pre-flop

   game.nature.deal_hole(parse_cards('AcKd'))
   game.nature.deal_hole(parse_cards('7h8h'))
   game.nature.deal_hole(parse_cards('3s5s'))

   btn.fold()
   sb.bet_raise(6)
   bb.bet_raise(18)
   sb.check_call()

   # Flop

   game.nature.deal_board(parse_cards('Jc3d5c'))

   sb.check_call()
   bb.check_call()

   # Turn

   game.nature.deal_board(parse_cards('4h'))

   sb.check_call()
   bb.check_call()

   # River

   game.nature.deal_board(parse_cards('Jh'))

   sb.check_call()
   bb.bet_raise(30)
   sb.check_call()

   # Showdown

   bb.showdown()
   sb.showdown()

All non-all-in pots that reach the end of the game **must** showdown.
Only after the showdown can the pot be distributed to the winners.

Typically, showdowns are started by the aggressor. If you are not sure
who is in turn to showdown, you can access the ``actor`` attribute.

An exception to the showdowns are all-in pots. Indeed, as per the WSOP
rule, all players involved in an all-in pot are forced to show their
hands no matter what. The idea is to prevent collusion and chip dumping.
As a result, in all-in pots, showdowns are unnecessary, as cards are
exposed by default without any action taken by the players.

Again, to summarize, you **absolutely must not** forget to showdown in
non-all-in pots that reach the end of the game. Otherwise, the pot will
not be distributed to the rightful owners. This allow people to muck or
show on purpose, which allow people to surrender their pots even if they
win.

Dwan vs Ivey
------------

This shows the 1.1 million dollar No-Limit Texas Hold'em pot played
between Dwan and Ivey.

Video: `<https://www.youtube.com/watch?v=GnxFohpljqM>`_

.. code-block:: python

   from pokertools import *

   game = NoLimitTexasHoldEm(
       Stakes(500, (1000, 2000)), (1125600, 2000000, 553500),
   )  # Antonius's stack is unknown
   ivey, antonius, dwan = game.players

   # Pre-flop

   game.nature.deal_hole(parse_cards('Ac2d'))
   game.nature.deal_hole(parse_cards('5h7s'))  # Unknown
   game.nature.deal_hole(parse_cards('7h6h'))

   dwan.bet_raise(7000)
   ivey.bet_raise(23000)
   antonius.fold()
   dwan.check_call()

   # Flop

   game.nature.deal_board(parse_cards('Jc3d5c'))

   ivey.bet_raise(35000)
   dwan.check_call()

   # Turn

   game.nature.deal_board(parse_cards('4h'))

   ivey.bet_raise(90000)
   dwan.bet_raise(232600)
   ivey.bet_raise(1067100)
   dwan.check_call()

   # River

   game.nature.deal_board(parse_cards('Jh'))

The result of this poker game is as follows:

.. code-block:: console

   Pot: 1109500  (1000 was probably collected as rake)
   Players:

   - Ivey: PokerPlayer(0, 572100, Ac2d)
   - Antonius: PokerPlayer(0, 1997500)
   - Dwan: PokerPlayer(0, 1109500, 7h6h)

   Board: Jc3d5c4hJh

Antonius vs Isildur
-------------------

This shows the 1.3 million dollar Pot-Limit Omaha Hold'em pot played
between Antonius and Isildur.

The integral values are multiplied by 100 to represent cents in dollars.

Video: `<https://www.youtube.com/watch?v=UMBm66Id2AA>`_

.. code-block:: python

   from pokertools import *

   game = PotLimitOmahaHoldEm(
       Stakes(0, (50000, 100000)), (125945025, 67847350),
   )
   antonius, isildur = game.players

   # Pre-flop

   game.nature.deal_hole(parse_cards('Ah3sKsKh'))
   game.nature.deal_hole(parse_cards('6d9s7d8h'))

   isildur.bet_raise(300000)
   antonius.bet_raise(900000)
   isildur.bet_raise(2700000)
   antonius.bet_raise(8100000)
   isildur.check_call()

   # Flop

   game.nature.deal_board(parse_cards('4s5c2h'))

   antonius.bet_raise(9100000)
   isildur.bet_raise(43500000)
   antonius.bet_raise(77900000)
   isildur.check_call()

   # Turn and River

   game.nature.deal_board(parse_cards('5h'))
   game.nature.deal_board(parse_cards('9c'))

The result of this poker game is as follows:

.. code-block:: console

   Pot: 135694700 (50 was probably collected as rake)
   Players:

   - Antonius: PokerPlayer(0, 193792375, Ah3sKsKh)
   - Isildur: PokerPlayer(0, 0)

   Board: 4s5c2h5h9c

Xuan vs Phua
------------

This shows the 800K dollar No-Limit Short-Deck Hold'em pot played
between Xuan and Phua. This time, the
:meth:`pokertools.game.PokerGame.parse` method will be used to replace
function calls with commands parses for applying actions.

Video: `<https://www.youtube.com/watch?v=QlgCcphLjaQ>`_

.. code-block:: python

   from pokertools import *

   game = NoLimitShortDeckHoldEm(
       Stakes(3000, {5: 3000}),
       (495000, 232000, 362000, 403000, 301000, 204000),
   )

   game.parse(
       # Pre-flop
       'dh Th8h', 'dh QsJd', 'dh QhQd', 'dh 8d7c', 'dh KhKs', 'dh 8c7h',
       'cc', 'cc', 'br 35000', 'f', 'br 298000', 'f', 'f', 'f', 'cc',
       # Flop
       'db 9h6cKc',
       # Turn
       'db Jh',
       # River
       'db Ts',
   )

Although not shown, a command for showdown is `'s'`, `'s 0'`, `'s 1'`,
for automatic showdowns, forced mucks, and forced shows, respectively.

The result of this poker game is as follows:

.. code-block:: console

   Pot: 623000
   Players:

   - Badziakouski: PokerPlayer(0, 489000)
   - Zhong: PokerPlayer(0, 226000)
   - Xuan: PokerPlayer(0, 684000, QhQd)
   - Jun: PokerPlayer(0, 400000)
   - Phua: PokerPlayer(0, 0, KhKs)
   - Koon: PokerPlayer(0, 198000)

   Board: 9h6cKcJhTs

Yockey vs Arieh
---------------

This shows the Triple Draw 2-to-7 Lowball pot between Yockey and Arieh
during which an insane bad beat occurred.

Video: `<https://www.youtube.com/watch?v=pChCqb2FNxY>`_

.. code-block:: python

   from pokertools import *

   game = FixedLimitTripleDrawLowball27(
       Stakes(0, (75000, 150000)), (1180000, 4340000, 5910000, 10765000),
   )

   game.parse(
       'dh 7h6c4c3d2c', 'dh JsJcJdJhTs', 'dh KsKcKdKhTh', 'dh AsQs6s5c3c',
       'f', 'br 300000', 'br 450000', 'f', 'cc',

       'dd', 'dd AsQs 2hQh',
       'br 150000', 'cc',

       'dd', 'dd Qh 4d',
       'br 300000', 'cc',

       'dd', 'dd 6s 7c',
       'br 280000', 'cc',
   )

The result of this poker game is as follows:

.. code-block:: console

   Pot: 2510000
   Players:

   - Yockey: PokerPlayer(0, 0, 7h6c4c3d2c)
   - Hui: PokerPlayer(0, 4190000)
   - Esposito: PokerPlayer(0, 5910000)
   - Arieh: PokerPlayer(0, 12095000, 2h4d7c5c3c)

   Board:
