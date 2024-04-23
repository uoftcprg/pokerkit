Motivational Examples
=====================

The functionalities of PokerKit primarily fall into two categories: game simulations, hand evaluations, and statistical analysis. Game simulations encompass creating an environment where poker games can be played out programmatically, simulating real-world scenarios with high fidelity. On the other hand, hand evaluations are concerned with determining the strength of particular poker hands. Statistical analysis helps review hand histories or analyze certain poker situations.

Game Simulation
---------------

Some motivational examples of poker games being played through PokerKit are shown in this section.

A Fixed-Limit Texas Hold'em Hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows a heads-up hand that folds around.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitTexasHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.CARD_BURNING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     2,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('AcAs')  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(Ac, As), statuse...
   >>> state.deal_hole('7h6h')  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(7h, 6h), statuse...

   >>> state.complete_bet_or_raise_to()
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount=6)
   >>> state.fold()
   Folding(commentary=None, player_index=1)

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [204, 196]

Multi-Runout in an All-In Situation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows the 4-runout hand between Phil Hellmuth and the Loose Cannon Ernest Wiggins.
   
Link: https://youtu.be/cnjJv7x0HMY?si=4l05Ez7lQVczt8DI&t=638
   
.. code-block:: pycon

   >>> from pokerkit import Automation, Mode, NoLimitTexasHoldem
   >>> state = NoLimitTexasHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     False,
   ...     {-1: 600},
   ...     (200, 400, 800),
   ...     400,
   ...     (999999, 116400, 86900, 999999, 50000, 999999),
   ...     6,
   ...     mode=Mode.CASH_GAME,
   ... )
   
Below are the pre-flop dealings and actions.
   
.. code-block:: pycon

   >>> state.deal_hole('JsTh')  # Tony G  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(Js, Th), statuse...
   >>> state.deal_hole('Ah9d')  # Hellmuth  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(Ah, 9d), statuse...
   >>> state.deal_hole('KsKc')  # Wiggins  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=2, cards=(Ks, Kc), statuse...
   >>> state.deal_hole('5c2h')  # Negreanu  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(5c, 2h), statuse...
   >>> state.deal_hole('6h5h')  # Brunson  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=4, cards=(6h, 5h), statuse...
   >>> state.deal_hole('6s3s')  # Laak  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=5, cards=(6s, 3s), statuse...
   >>> state.fold()  # Negreanu
   Folding(commentary=None, player_index=3)
   >>> state.complete_bet_or_raise_to(
   ...     2800,
   ... )  # Brunson  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=4, amount...
   >>> state.fold()  # Laak
   Folding(commentary=None, player_index=5)
   >>> state.check_or_call()  # Tony G
   CheckingOrCalling(commentary=None, player_index=0, amount=2600)
   >>> state.complete_bet_or_raise_to(
   ...     12600,
   ... )  # Hellmuth  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.check_or_call()  # Wiggins
   CheckingOrCalling(commentary=None, player_index=2, amount=11800)
   >>> state.check_or_call()  # Brunson
   CheckingOrCalling(commentary=None, player_index=4, amount=9800)
   >>> state.check_or_call()  # Tony G
   CheckingOrCalling(commentary=None, player_index=0, amount=9800)
   
Below are the flop dealing and actions.
   
.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('9hTs9s')
   BoardDealing(commentary=None, cards=(9h, Ts, 9s))
   >>> state.check_or_call()  # Tony G
   CheckingOrCalling(commentary=None, player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to(
   ...     17000,
   ... )  # Hellmuth  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.complete_bet_or_raise_to(
   ...     36000,
   ... )  # Wiggins  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
   >>> state.fold()  # Brunson
   Folding(commentary=None, player_index=4)
   >>> state.fold()  # Tony G
   Folding(commentary=None, player_index=0)
   >>> state.complete_bet_or_raise_to(
   ...     103800,
   ... )  # Hellmuth  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.check_or_call()  # Wiggins
   CheckingOrCalling(commentary=None, player_index=2, amount=38300)
   
Below is selecting the number of runouts.
   
.. code-block:: pycon

   >>> state.select_runout_count(4)  # Hellmuth
   RunoutCountSelection(commentary=None, player_index=1, runout_count=4)
   >>> state.select_runout_count(None)  # Wiggins  # doctest: +ELLIPSIS
   RunoutCountSelection(commentary=None, player_index=2, runout_count=N...
   
Below is the first runout.
   
.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Jh')  # Turn
   BoardDealing(commentary=None, cards=(Jh,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Ad')  # River
   BoardDealing(commentary=None, cards=(Ad,))
   
Below is the second runout.
   
.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Kh')  # Turn
   BoardDealing(commentary=None, cards=(Kh,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('3c')  # River
   BoardDealing(commentary=None, cards=(3c,))
   
Below is the third runout.
   
.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('7s')  # Turn
   BoardDealing(commentary=None, cards=(7s,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('8s')  # River
   BoardDealing(commentary=None, cards=(8s,))
   
Below is the fourth runout.
   
.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Qc')  # Turn
   BoardDealing(commentary=None, cards=(Qc,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Kd')  # River
   BoardDealing(commentary=None, cards=(Kd,))
   
Below are the final stacks.
   
.. code-block:: pycon

   >>> state.stacks
   [987399, 79400, 149700, 999999, 37400, 999399]

A Sample No-Limit Texas Hold'em Hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows the first televised million-dollar pot between Tom Dwan and Phil Ivey.

Link: https://youtu.be/GnxFohpljqM

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = NoLimitTexasHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     500,
   ...     (1000, 2000),
   ...     2000,
   ...     (1125600, 2000000, 553500),
   ...     3,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Ac2d')  # Ivey  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(Ac, 2d), statuse...
   >>> state.deal_hole('????')  # Antonius  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(??, ??), statuse...
   >>> state.deal_hole('7h6h')  # Dwan  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=2, cards=(7h, 6h), statuse...

   >>> state.complete_bet_or_raise_to(7000)  # Dwan  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
   >>> state.complete_bet_or_raise_to(23000)  # Ivey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.fold()  # Antonius
   Folding(commentary=None, player_index=1)
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(commentary=None, player_index=2, amount=16000)

Below are the flop dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Jc3d5c')
   BoardDealing(commentary=None, cards=(Jc, 3d, 5c))

   >>> state.complete_bet_or_raise_to(35000)  # Ivey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(commentary=None, player_index=2, amount=35000)

Below are the turn dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('4h')
   BoardDealing(commentary=None, cards=(4h,))

   >>> state.complete_bet_or_raise_to(90000)  # Ivey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.complete_bet_or_raise_to(
   ...     232600,
   ... )  # Dwan  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
   >>> state.complete_bet_or_raise_to(
   ...     1067100,
   ... )  # Ivey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Dwan
   CheckingOrCalling(commentary=None, player_index=2, amount=262400)

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Jh')
   BoardDealing(commentary=None, cards=(Jh,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [572100, 1997500, 1109500]

A Sample Short-Deck Hold'em Hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows an all-in hand between Xuan and Phua.

Link: https://youtu.be/QlgCcphLjaQ

.. code-block:: pycon

   >>> state = NoLimitShortDeckHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     3000,
   ...     {-1: 3000},
   ...     3000,
   ...     (495000, 232000, 362000, 403000, 301000, 204000),
   ...     6,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Th8h')  # Badziakouski  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(Th, 8h), statuse...
   >>> state.deal_hole('QsJd')  # Zhong  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(Qs, Jd), statuse...
   >>> state.deal_hole('QhQd')  # Xuan  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=2, cards=(Qh, Qd), statuse...
   >>> state.deal_hole('8d7c')  # Jun  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(8d, 7c), statuse...
   >>> state.deal_hole('KhKs')  # Phua  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=4, cards=(Kh, Ks), statuse...
   >>> state.deal_hole('8c7h')  # Koon  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=5, cards=(8c, 7h), statuse...

   >>> state.check_or_call()  # Badziakouski
   CheckingOrCalling(commentary=None, player_index=0, amount=3000)
   >>> state.check_or_call()  # Zhong
   CheckingOrCalling(commentary=None, player_index=1, amount=3000)
   >>> state.complete_bet_or_raise_to(35000)  # Xuan  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=2, amount...
   >>> state.fold()  # Jun
   Folding(commentary=None, player_index=3)
   >>> state.complete_bet_or_raise_to(
   ...     298000,
   ... )  # Phua  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=4, amount...
   >>> state.fold()  # Koon
   Folding(commentary=None, player_index=5)
   >>> state.fold()  # Badziakouski
   Folding(commentary=None, player_index=0)
   >>> state.fold()  # Zhong
   Folding(commentary=None, player_index=1)
   >>> state.check_or_call()  # Xuan
   CheckingOrCalling(commentary=None, player_index=2, amount=263000)

Below is the flop dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('9h6cKc')
   BoardDealing(commentary=None, cards=(9h, 6c, Kc))

Below is the turn dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Jh')
   BoardDealing(commentary=None, cards=(Jh,))

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('Ts')
   BoardDealing(commentary=None, cards=(Ts,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [489000, 226000, 684000, 400000, 0, 198000]

A Sample Pot-Limit Omaha Hold'em Hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows the largest online poker pot ever played between Patrik Antonius and Viktor Blom.

Link: https://youtu.be/UMBm66Id2AA

.. code-block:: pycon

   >>> state = PotLimitOmahaHoldem.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (500, 1000),
   ...     1000,
   ...     (1259450.25, 678473.5),
   ...     2,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('Ah3sKsKh')  # Antonius  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(Ah, 3s, Ks, Kh),...
   >>> state.deal_hole('6d9s7d8h')  # Blom  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(6d, 9s, 7d, 8h),...

   >>> state.complete_bet_or_raise_to(3000)  # Blom  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.complete_bet_or_raise_to(
   ...     9000,
   ... )  # Antonius  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.complete_bet_or_raise_to(27000)  # Blom  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.complete_bet_or_raise_to(
   ...     81000,
   ... )  # Antonius  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Blom
   CheckingOrCalling(commentary=None, player_index=1, amount=54000)

Below are the flop dealing and actions.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('4s5c2h')
   BoardDealing(commentary=None, cards=(4s, 5c, 2h))

   >>> state.complete_bet_or_raise_to(
   ...     91000,
   ... )  # Antonius  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.complete_bet_or_raise_to(
   ...     435000,
   ... )  # Blom  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount...
   >>> state.complete_bet_or_raise_to(
   ...     779000,
   ... )  # Antonius  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Blom
   CheckingOrCalling(commentary=None, player_index=1, amount=162473.5)

Below is the turn dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('5h')
   BoardDealing(commentary=None, cards=(5h,))

Below is the river dealing.

.. code-block:: pycon

   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_board('9c')
   BoardDealing(commentary=None, cards=(9c,))

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [1937923.75, 0.0]

A Sample Fixed-Limit Deuce-To-Seven Lowball Triple Draw Hand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below shows a bad beat between Yockey and Arieh.

Link: https://youtu.be/pChCqb2FNxY

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (75000, 150000),
   ...     150000,
   ...     300000,
   ...     (1180000, 4340000, 5910000, 10765000),
   ...     4,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('7h6c4c3d2c')  # Yockey  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(7h, 6c, 4c, 3d, ...
   >>> state.deal_hole('??????????')  # Hui  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(??, ??, ??, ??, ...
   >>> state.deal_hole('??????????')  # Esposito  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=2, cards=(??, ??, ??, ??, ...
   >>> state.deal_hole('AsQs6s5c3c')  # Arieh  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(As, Qs, 6s, 5c, ...

   >>> state.fold()  # Esposito
   Folding(commentary=None, player_index=2)
   >>> state.complete_bet_or_raise_to()  # Arieh  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount...
   >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.fold()  # Hui
   Folding(commentary=None, player_index=1)
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(commentary=None, player_index=3, amount=150000)

Below are the first draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
   >>> state.stand_pat_or_discard('AsQs')  # Arieh  # doctest: +ELLIPSIS
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=(As, ...
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('2hQh')  # Arieh  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(2h, Qh), statuse...

   >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(commentary=None, player_index=3, amount=150000)

Below are the second draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
   >>> state.stand_pat_or_discard('Qh')  # Arieh
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=(Qh,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('4d')  # Arieh  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(4d,), statuses=(...

   >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(commentary=None, player_index=3, amount=300000)

Below are the third draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard()  # Yockey
   StandingPatOrDiscarding(commentary=None, player_index=0, cards=())
   >>> state.stand_pat_or_discard('6s')  # Arieh
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=(6s,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('7c')  # Arieh  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(7c,), statuses=(...

   >>> state.complete_bet_or_raise_to()  # Yockey  # doctest: +ELLIPSIS
   CompletionBettingOrRaisingTo(commentary=None, player_index=0, amount...
   >>> state.check_or_call()  # Arieh
   CheckingOrCalling(commentary=None, player_index=3, amount=280000)

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [0, 4190000, 5910000, 12095000]

A Sample Badugi Hand
^^^^^^^^^^^^^^^^^^^^

Below shows an example badugi hand from Wikipedia.

Link: https://en.wikipedia.org/wiki/Badugi

.. code-block:: pycon

   >>> from pokerkit import *
   >>> state = FixedLimitBadugi.create_state(
   ...     (
   ...         Automation.ANTE_POSTING,
   ...         Automation.BET_COLLECTION,
   ...         Automation.BLIND_OR_STRADDLE_POSTING,
   ...         Automation.HAND_KILLING,
   ...         Automation.CHIPS_PUSHING,
   ...         Automation.CHIPS_PULLING,
   ...     ),
   ...     True,
   ...     0,
   ...     (1, 2),
   ...     2,
   ...     4,
   ...     200,
   ...     4,
   ... )

Below are the pre-flop dealings and actions.

.. code-block:: pycon

   >>> state.deal_hole('????????')  # Bob  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(??, ??, ??, ??),...
   >>> state.deal_hole('????????')  # Carol  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(??, ??, ??, ??),...
   >>> state.deal_hole('????????')  # Ted  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=2, cards=(??, ??, ??, ??),...
   >>> state.deal_hole('????????')  # Alice  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(??, ??, ??, ??),...

   >>> state.fold()  # Ted
   Folding(commentary=None, player_index=2)
   >>> state.check_or_call()  # Alice
   CheckingOrCalling(commentary=None, player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   CheckingOrCalling(commentary=None, player_index=0, amount=1)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(commentary=None, player_index=1, amount=0)

Below are the first draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('????')  # Bob  # doctest: +ELLIPSIS
   StandingPatOrDiscarding(commentary=None, player_index=0, cards=(??, ...
   >>> state.stand_pat_or_discard('????')  # Carol  # doctest: +ELLIPSIS
   StandingPatOrDiscarding(commentary=None, player_index=1, cards=(??, ...
   >>> state.stand_pat_or_discard('??')  # Alice
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=(??,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('????')  # Bob  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(??, ??), statuse...
   >>> state.deal_hole('????')  # Carol  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(??, ??), statuse...
   >>> state.deal_hole('??')  # Alice  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(??,), statuses=(...

   >>> state.check_or_call()  # Bob
   CheckingOrCalling(commentary=None, player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=2)
   >>> state.check_or_call()  # Alice
   CheckingOrCalling(commentary=None, player_index=3, amount=2)
   >>> state.check_or_call()  # Bob
   CheckingOrCalling(commentary=None, player_index=0, amount=2)

Below are the second draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('??')  # Bob
   StandingPatOrDiscarding(commentary=None, player_index=0, cards=(??,))
   >>> state.stand_pat_or_discard()  # Carol
   StandingPatOrDiscarding(commentary=None, player_index=1, cards=())
   >>> state.stand_pat_or_discard('??')  # Alice
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=(??,))
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('??')  # Bob  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=0, cards=(??,), statuses=(...
   >>> state.deal_hole('??')  # Alice  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=3, cards=(??,), statuses=(...

   >>> state.check_or_call()  # Bob
   CheckingOrCalling(commentary=None, player_index=0, amount=0)
   >>> state.complete_bet_or_raise_to()  # Carol
   CompletionBettingOrRaisingTo(commentary=None, player_index=1, amount=4)
   >>> state.complete_bet_or_raise_to()  # Alice
   CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount=8)
   >>> state.fold()  # Bob
   Folding(commentary=None, player_index=0)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(commentary=None, player_index=1, amount=4)

Below are the third draw and actions.

.. code-block:: pycon

   >>> state.stand_pat_or_discard('??')  # Carol
   StandingPatOrDiscarding(commentary=None, player_index=1, cards=(??,))
   >>> state.stand_pat_or_discard()  # Alice
   StandingPatOrDiscarding(commentary=None, player_index=3, cards=())
   >>> state.burn_card('??')
   CardBurning(commentary=None, card=??)
   >>> state.deal_hole('??')  # Carol  # doctest: +ELLIPSIS
   HoleDealing(commentary=None, player_index=1, cards=(??,), statuses=(...

   >>> state.check_or_call()  # Carol
   CheckingOrCalling(commentary=None, player_index=1, amount=0)
   >>> state.complete_bet_or_raise_to()  # Alice
   CompletionBettingOrRaisingTo(commentary=None, player_index=3, amount=4)
   >>> state.check_or_call()  # Carol
   CheckingOrCalling(commentary=None, player_index=1, amount=4)

Below is the showdown.

.. code-block:: pycon

   >>> state.show_or_muck_hole_cards(
   ...     '2s4c6d9h',
   ... )  # Alice  # doctest: +ELLIPSIS
   HoleCardsShowingOrMucking(commentary=None, player_index=3, hole_card...
   >>> state.show_or_muck_hole_cards(
   ...     '3s5d7c8h',
   ... )  # Carol  # doctest: +ELLIPSIS
   HoleCardsShowingOrMucking(commentary=None, player_index=1, hole_card...

Below are the final stacks.

.. code-block:: pycon

   >>> state.stacks
   [196, 220, 200, 184]

Hand Evaluation
---------------

Below are example short-deck hold'em hand evaluations.

Note that hands are compared through the comparison operators.

.. code-block:: pycon

   >>> from pokerkit import *
   >>> h0 = ShortDeckHoldemHand('6s7s8s9sTs')
   >>> h1 = ShortDeckHoldemHand('7c8c9cTcJc')
   >>> h2 = ShortDeckHoldemHand('2c2d2h2s3h')  # doctest: +ELLIPSIS
   Traceback (most recent call last):
       ...
   ValueError: The cards '2c2d2h2s3h' form an invalid ShortDeckHoldemHand h...
   >>> h0
   6s7s8s9sTs
   >>> h1
   7c8c9cTcJc
   >>> print(h0)
   Straight flush (6s7s8s9sTs)
   >>> h0 < h1
   True

Statistical Analysis
--------------------

Various tools in PokerKit exists to facilitate poker analysis.

Monte-Carlo Evaluations
^^^^^^^^^^^^^^^^^^^^^^^

Below are example player equity/hand strength calculations.

.. code-block:: pycon

   >>> from concurrent.futures import ProcessPoolExecutor
   >>> from pokerkit import *
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_equities(
   ...         (
   ...             parse_range('AK'),
   ...             parse_range('22'),
   ...         ),
   ...         (),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=10000,
   ...         executor=executor,
   ...     )
   ... 
   [0.4807, 0.5193]
   >>> with ProcessPoolExecutor() as executor:
   ...     calculate_hand_strength(
   ...         2,
   ...         parse_range('AsKs'),
   ...         Card.parse('Kc8h8d'),
   ...         2,
   ...         5,
   ...         Deck.STANDARD,
   ...         (StandardHighHand,),
   ...         sample_count=1000,
   ...         executor=executor,
   ...     )
   ... 
   0.885

Hand Histories
^^^^^^^^^^^^^^

One can also save/load hand histories and analyze them.

.. code-block:: python

   from pokerkit import *

   hh0 = ...
   hh1 = ...
   hh2 = ...
   ...

   ss = Statistics.from_hand_history(hh0, hh1, hh2, ...)

   print(ss['John Doe'].payoff_mean)  # in chips/hand
   print(ss['John Doe'].payoff_stdev)  # in chips/hand
