========
PokerKit
========

``PokerKit`` is an open-source Python library for simulating poker games and
evaluating poker hands, developed by the University of Toronto Computer Poker
Research Group. It provides extensive support for all major and minor poker
variants, offers a high level of control over game states, and supports
high-speed hand evaluations.

**Installation**
----------------

The ``PokerKit`` library can be installed using pip:

.. code-block:: bash

   pip install pokerkit

**Features**
------------

* Extensive poker game logic for major and minor poker variants
* High-speed hand evaluations
* Customizable game states and parameters
* Robust implementation with extensive unit tests and doctests
* Ability to simulate famous hands from poker history

**Usage**
---------

Below shows the first televised million dollar pot between Tom Dwan and Phil
Ivey.

Link: https://youtu.be/GnxFohpljqM

.. code-block:: python

   from pokerkit import Automation, NoLimitTexasHoldem

   state = NoLimitTexasHoldem.create_state(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIP_PUSHING,
           Automation.CHIP_PULLING,
       ),
       True,
       500,
       (1000, 2000),
       2000,
       (1125600, 2000000, 553500),
       3,
   )

   # Below shows the pre-flop dealings and actions.

   state.deal_hole('Ac2d')  # Ivey
   state.deal_hole('5h7s')  # Antonius*
   state.deal_hole('7h6h')  # Dwan

   state.complete_bet_or_raise_to(7000)  # Dwan
   state.complete_bet_or_raise_to(23000)  # Ivey
   state.fold()  # Antonius
   state.check_or_call()  # Dwan

   # Below shows the flop dealing and actions.

   state.deal_board('Jc3d5c')

   state.complete_bet_or_raise_to(35000)  # Ivey
   state.check_or_call()  # Dwan

   # Below shows the turn dealing and actions.

   state.deal_board('4h')

   state.complete_bet_or_raise_to(90000)  # Ivey
   state.complete_bet_or_raise_to(232600)  # Dwan
   state.complete_bet_or_raise_to(1067100)  # Ivey
   state.check_or_call()  # Dwan

   # Below shows the river dealing.

   state.deal_board('Jh')

   # Below shows the final stacks.

   print(state.stacks)  # [572100, 1997500, 1109500]

Below shows an all-in hand between Xuan and Phua.

Link: https://youtu.be/QlgCcphLjaQ

.. code-block:: python

   from pokerkit import Automation, NoLimitShortDeckHoldem

   state = NoLimitShortDeckHoldem.create_state(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,
       3000,
       {-1: 3000},
       3000,
       (495000, 232000, 362000, 403000, 301000, 204000),
       6,
   )

   # Below shows the pre-flop dealings and actions.

   state.deal_hole('Th8h')  # Badziakouski
   state.deal_hole('QsJd')  # Zhong
   state.deal_hole('QhQd')  # Xuan
   state.deal_hole('8d7c')  # Jun
   state.deal_hole('KhKs')  # Phua
   state.deal_hole('8c7h')  # Koon

   state.check_or_call()  # Badziakouski
   state.check_or_call()  # Zhong
   state.complete_bet_or_raise_to(35000)  # Xuan
   state.fold()  # Jun
   state.complete_bet_or_raise_to(298000)  # Phua
   state.fold()  # Koon
   state.fold()  # Badziakouski
   state.fold()  # Zhong
   state.check_or_call()  # Xuan

   # Below shows the flop dealing.

   state.deal_board('9h6cKc')

   # Below shows the turn dealing.

   state.deal_board('Jh')

   # Below shows the river dealing.

   state.deal_board('Ts')

   # Below show the final stacks.

   print(state.stacks)  # [489000, 226000, 684000, 400000, 0, 198000]

Below shows the largest online poker pot every played between
Patrik Antonius and Viktor Blom.

Link: https://youtu.be/UMBm66Id2AA

.. code-block:: python

   from pokerkit import Automation, PotLimitOmahaHoldem

   state = PotLimitOmahaHoldem.create_state(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,
       None,
       (50000, 100000),
       2000,
       (125945025, 67847350),
       2,
   )

   # Below shows the pre-flop dealings and actions.

   state.deal_hole('Ah3sKsKh')  # Antonius
   state.deal_hole('6d9s7d8h')  # Blom

   state.complete_bet_or_raise_to(300000)  # Blom
   state.complete_bet_or_raise_to(900000)  # Antonius
   state.complete_bet_or_raise_to(2700000)  # Blom
   state.complete_bet_or_raise_to(8100000)  # Antonius
   state.check_or_call()  # Blom

   # Below shows the flop dealing and actions.

   state.deal_board('4s5c2h')

   state.complete_bet_or_raise_to(9100000)  # Antonius
   state.complete_bet_or_raise_to(43500000)  # Blom
   state.complete_bet_or_raise_to(77900000)  # Antonius
   state.check_or_call()  # Blom

   # Below shows the turn dealing.

   state.deal_board('5h')

   # Below shows the river dealing.

   state.deal_board('9c')

   # Below show the final stacks.

   print(state.stacks)  # [193792375, 0]

Below shows a bad beat between Yockey and Arieh.

Link: https://youtu.be/pChCqb2FNxY

.. code-block:: python

   from pokerkit import Automation, FixedLimitDeuceToSevenLowballTripleDraw

   state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIP_PUSHING,
           Automation.CHIP_PULLING,
       ),
       True,
       None,
       (75000, 150000),
       150000,
       300000,
       (1180000, 4340000, 5910000, 10765000),
       4,
   )

   # Below shows the pre-flop dealings and actions.

   state.deal_hole('7h6c4c3d2c')  # Yockey
   state.deal_hole('JsJcJdJhTs')  # Hui*
   state.deal_hole('KsKcKdKhTh')  # Esposito*
   state.deal_hole('AsQs6s5c3c')  # Arieh

   state.fold()  # Esposito
   state.complete_bet_or_raise_to()  # Arieh
   state.complete_bet_or_raise_to()  # Yockey
   state.fold()  # Hui
   state.check_or_call()  # Arieh

   # Below shows the first draw and actions.

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('AsQs')  # Arieh
   state.deal_hole('2hQh')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

   # Below shows the second draw and actions.

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('Qh')  # Arieh
   state.deal_hole('4d')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

   # Below shows the third draw and actions.

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('6s')  # Arieh
   state.deal_hole('7c')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

   # Below show the final stacks.

   print(state.stacks)  # [0, 4190000, 5910000, 12095000]

Below shows an example badugi hand from Wikipedia.

Link: https://en.wikipedia.org/wiki/Badugi

.. code-block:: python

   from pokerkit import Automation, FixedLimitBadugi

   state = FixedLimitBadugi.create_state(
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.CARD_BURNING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,
       None,
       (1, 2),
       2,
       4,
       200,
       4,
   )

   # Below shows the pre-flop dealings and actions.

   state.deal_hole('As4hJcKh')  # Bob*
   state.deal_hole('3s5d7s8s')  # Carol*
   state.deal_hole('KsKdQsQd')  # Ted*
   state.deal_hole('2s4c6dKc')  # Alice*

   state.fold()  # Ted
   state.check_or_call()  # Alice
   state.check_or_call()  # Bob
   state.check_or_call()  # Carol

   # Below shows the first draw and actions.

   state.stand_pat_or_discard('JcKh')  # Bob*
   state.stand_pat_or_discard('7s8s')  # Carol*
   state.stand_pat_or_discard('Kc')  # Alice*
   state.deal_hole('TcJs')  # Bob*
   state.deal_hole('7cTh')  # Carol*
   state.deal_hole('Qc')  # Alice*

   state.check_or_call()  # Bob
   state.complete_bet_or_raise_to()  # Carol
   state.check_or_call()  # Alice
   state.check_or_call()  # Bob

   # Below shows the second draw and actions.

   state.stand_pat_or_discard('Js')  # Bob*
   state.stand_pat_or_discard()  # Carol*
   state.stand_pat_or_discard('Qc')  # Alice*
   state.deal_hole('Ts')  # Bob*
   state.deal_hole('9h')  # Alice*

   state.check_or_call()  # Bob
   state.complete_bet_or_raise_to()  # Carol
   state.complete_bet_or_raise_to()  # Alice
   state.fold()  # Bob
   state.check_or_call()  # Carol

   # Below shows the third draw and actions.

   state.stand_pat_or_discard('Th')  # Carol*
   state.stand_pat_or_discard()  # Alice*
   state.deal_hole('8h')  # Carol*

   state.check_or_call()  # Carol
   state.complete_bet_or_raise_to()  # Alice
   state.check_or_call()  # Carol

   # Below show the final stacks.

   print(state.stacks)  # [196, 220, 200, 184]

**Testing and Validation**
--------------------------

``PokerKit`` has extensive test coverage, passes mypy static type checking with
strict parameter, and has been validated through extensive use in real-life
scenarios.

**Contributing**
----------------

Contributions are welcome! Please read our
`Contributing Guide <CONTRIBUTING.rst>`_ for more information.

**License**
-----------

``PokerKit`` is distributed under the MIT license. See `LICENSE <LICENSE>`_ for
more information.

**Citing**
----------

If you use ``PokerKit`` in your research, please cite our library:

.. code-block:: bibtex

   @misc{pokerkit,
     title={PokerKit: An Open-Source Python Library for Poker Simulations and Hand Evaluations},
     author={Your name here},
     year={2023},
     url={https://github.com/uoftcprg/pokerkit}
   }
