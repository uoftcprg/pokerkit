========
PokerKit
========

PokerKit is an open-source Python library for simulating poker games and evaluating poker hands, developed by the University of Toronto Computer Poker Research Group. PokerKit supports an extensive array of poker variants and it provides a flexible architecture for users to define their custom games. These facilities are exposed via an intuitive unified high-level programmatic API. The library can be used in a variety of use cases, from poker AI development, and tool creation, to online poker casino implementation. PokerKit's reliability has been established through static type checking, extensive doctests, and unit tests, achieving 99% code coverage.

Features
--------

* Extensive poker game logic for major and minor poker variants.
* High-speed hand evaluations.
* Customizable game states and parameters.
* Robust implementation with static type checking and extensive unit tests and doctests.
* Dataset of over 10,000 hand histories.

Installation
------------

The PokerKit library can be installed using pip:

.. code-block:: bash

   pip install pokerkit

Usages
------

**The first televised million-dollar pot between Tom Dwan and Phil Ivey.**

Link: https://youtu.be/GnxFohpljqM

Set up the game.

.. code-block:: python

   from pokerkit import Automation, NoLimitTexasHoldem

   state = NoLimitTexasHoldem.create_state(
       # Automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,  # Uniform antes?
       500,  # Antes
       (1000, 2000),  # Blinds or straddles
       2000,  # Min-bet
       (1125600, 2000000, 553500),  # Starting stacks
       3,  # Number of players
   )

Below are the pre-flop dealings and actions.

.. code-block:: python

   state.deal_hole('Ac2d')  # Ivey
   state.deal_hole('????')  # Antonius
   state.deal_hole('7h6h')  # Dwan

   state.complete_bet_or_raise_to(7000)  # Dwan
   state.complete_bet_or_raise_to(23000)  # Ivey
   state.fold()  # Antonius
   state.check_or_call()  # Dwan

Below are the flop dealing and actions.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('Jc3d5c')

   state.complete_bet_or_raise_to(35000)  # Ivey
   state.check_or_call()  # Dwan

Below are the turn dealing and actions.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('4h')

   state.complete_bet_or_raise_to(90000)  # Ivey
   state.complete_bet_or_raise_to(232600)  # Dwan
   state.complete_bet_or_raise_to(1067100)  # Ivey
   state.check_or_call()  # Dwan

Below is the river dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('Jh')

Below are the final stacks.

.. code-block:: python

   print(state.stacks)  # [572100, 1997500, 1109500]

**An all-in hand between Xuan and Phua.**

Link: https://youtu.be/QlgCcphLjaQ

.. code-block:: python

   from pokerkit import Automation, NoLimitShortDeckHoldem

   state = NoLimitShortDeckHoldem.create_state(
       # Automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,  # Uniform antes?
       3000,  # Antes
       {-1: 3000},  # Blinds or straddles
       3000,  # Min-bet
       (495000, 232000, 362000, 403000, 301000, 204000),  # Starting stacks
       6,  # Number of players
   )

Below are the pre-flop dealings and actions.

.. code-block:: python

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

Below is the flop dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('9h6cKc')

Below is the turn dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('Jh')

Below is the river dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('Ts')

Below are the final stacks.

.. code-block:: python

   print(state.stacks)  # [489000, 226000, 684000, 400000, 0, 198000]

**The largest online poker pot ever played between Patrik Antonius and Viktor
Blom.**

Link: https://youtu.be/UMBm66Id2AA

.. code-block:: python

   from pokerkit import Automation, PotLimitOmahaHoldem

   state = PotLimitOmahaHoldem.create_state(
       # Automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,  # Uniform antes?
       0,  # Antes
       (500, 1000),  # Blinds or straddles
       1000,  # Min-bet
       (1259450.25, 678473.5),  # Starting stacks
       2,  # Number of players
   )

Below are the pre-flop dealings and actions.

.. code-block:: python

   state.deal_hole('Ah3sKsKh')  # Antonius
   state.deal_hole('6d9s7d8h')  # Blom

   state.complete_bet_or_raise_to(3000)  # Blom
   state.complete_bet_or_raise_to(9000)  # Antonius
   state.complete_bet_or_raise_to(27000)  # Blom
   state.complete_bet_or_raise_to(81000)  # Antonius
   state.check_or_call()  # Blom

Below are the flop dealing and actions.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('4s5c2h')

   state.complete_bet_or_raise_to(91000)  # Antonius
   state.complete_bet_or_raise_to(435000)  # Blom
   state.complete_bet_or_raise_to(779000)  # Antonius
   state.check_or_call()  # Blom

Below is the turn dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('5h')

Below is the river dealing.

.. code-block:: python

   state.burn_card('??')
   state.deal_board('9c')

Below are the final stacks.

.. code-block:: python

   print(state.stacks)  # [1937923.75, 0.0]

**A bad beat between Yockey and Arieh.**

Link: https://youtu.be/pChCqb2FNxY

.. code-block:: python

   from pokerkit import Automation, FixedLimitDeuceToSevenLowballTripleDraw

   state = FixedLimitDeuceToSevenLowballTripleDraw.create_state(
       # Automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,  # Uniform antes?
       0,  # Antes
       (75000, 150000),  # Blinds or straddles
       150000,  # Small-bet
       300000,  # Big-bet
       (1180000, 4340000, 5910000, 10765000),  # Starting stacks
       4,  # Number of players
   )

Below are the pre-flop dealings and actions.

.. code-block:: python

   state.deal_hole('7h6c4c3d2c')  # Yockey
   state.deal_hole('??????????')  # Hui
   state.deal_hole('??????????')  # Esposito
   state.deal_hole('AsQs6s5c3c')  # Arieh

   state.fold()  # Esposito
   state.complete_bet_or_raise_to()  # Arieh
   state.complete_bet_or_raise_to()  # Yockey
   state.fold()  # Hui
   state.check_or_call()  # Arieh

Below are the first draw and actions.

.. code-block:: python

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('AsQs')  # Arieh
   state.burn_card('??')
   state.deal_hole('2hQh')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

Below are the second draw and actions.

.. code-block:: python

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('Qh')  # Arieh
   state.burn_card('??')
   state.deal_hole('4d')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

Below are the third draw and actions.

.. code-block:: python

   state.stand_pat_or_discard()  # Yockey
   state.stand_pat_or_discard('6s')  # Arieh
   state.burn_card('??')
   state.deal_hole('7c')  # Arieh

   state.complete_bet_or_raise_to()  # Yockey
   state.check_or_call()  # Arieh

Below are the final stacks.

.. code-block:: python

   print(state.stacks)  # [0, 4190000, 5910000, 12095000]

**An example badugi hand from Wikipedia.**

Link: https://en.wikipedia.org/wiki/Badugi

.. code-block:: python

   from pokerkit import Automation, FixedLimitBadugi

   state = FixedLimitBadugi.create_state(
       # Automations
       (
           Automation.ANTE_POSTING,
           Automation.BET_COLLECTION,
           Automation.BLIND_OR_STRADDLE_POSTING,
           Automation.HAND_KILLING,
           Automation.CHIPS_PUSHING,
           Automation.CHIPS_PULLING,
       ),
       True,  # Uniform antes?
       0,  # Antes
       (1, 2),  # Blinds or straddles
       2,  # Small-bet
       4,  # Big-bet
       200,  # Starting stacks
       4,  # Number of players
   )

Below are the pre-flop dealings and actions.

.. code-block:: python

   state.deal_hole('????????')  # Bob
   state.deal_hole('????????')  # Carol
   state.deal_hole('????????')  # Ted
   state.deal_hole('????????')  # Alice

   state.fold()  # Ted
   state.check_or_call()  # Alice
   state.check_or_call()  # Bob
   state.check_or_call()  # Carol

Below are the first draw and actions.

.. code-block:: python

   state.stand_pat_or_discard('????')  # Bob
   state.stand_pat_or_discard('????')  # Carol
   state.stand_pat_or_discard('??')  # Alice
   state.burn_card('??')
   state.deal_hole('????')  # Bob
   state.deal_hole('????')  # Carol
   state.deal_hole('??')  # Alice

   state.check_or_call()  # Bob
   state.complete_bet_or_raise_to()  # Carol
   state.check_or_call()  # Alice
   state.check_or_call()  # Bob

Below are the second draw and actions.

.. code-block:: python

   state.stand_pat_or_discard('??')  # Bob
   state.stand_pat_or_discard()  # Carol
   state.stand_pat_or_discard('??')  # Alice
   state.burn_card('??')
   state.deal_hole('??')  # Bob
   state.deal_hole('??')  # Alice

   state.check_or_call()  # Bob
   state.complete_bet_or_raise_to()  # Carol
   state.complete_bet_or_raise_to()  # Alice
   state.fold()  # Bob
   state.check_or_call()  # Carol

Below are the third draw and actions.

.. code-block:: python

   state.stand_pat_or_discard('??')  # Carol
   state.stand_pat_or_discard()  # Alice
   state.burn_card('??')
   state.deal_hole('??')  # Carol

   state.check_or_call()  # Carol
   state.complete_bet_or_raise_to()  # Alice
   state.check_or_call()  # Carol

Below is the showdown.

.. code-block:: python

   state.show_or_muck_hole_cards('2s4c6d9h')  # Alice
   state.show_or_muck_hole_cards('3s5d7c8h')  # Carol

Below are the final stacks.

.. code-block:: python

   print(state.stacks)  # [196, 220, 200, 184]

Testing and Validation
----------------------

PokerKit has extensive test coverage, passes mypy static type checking with strict parameter, and has been validated through extensive use in real-life scenarios.

Contributing
------------

Contributions are welcome! Please read our Contributing Guide for more information.

License
-------

PokerKit is distributed under the MIT license.

Citing
------

If you use PokerKit in your research, please cite our library:

.. code-block:: bibtex

   @ARTICLE{10287546,
     author={Kim, Juho},
     journal={IEEE Transactions on Games}, 
     title={PokerKit: A Comprehensive Python Library for Fine-Grained Multi-Variant Poker Game Simulations}, 
     year={2023},
     volume={},
     number={},
     pages={1-8},
     doi={10.1109/TG.2023.3325637}}
