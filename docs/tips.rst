Tips and Tricks
===============

Some tips and tricks are shown below. If you would like to see more, please create an issue.

Full Manual Usage
-----------------

In some use cases, it might be better not to use any automation and handle each operation step by step. For such a purpose, one might use the code below.

.. code-block:: python

   from pokerkit import *

   def create_state(): ...

   state = create_state()

   while state.status:
       if state.can_post_ante():
           state.post_ante()
       elif state.can_collect_bets():
           state.collect_bets()
       elif state.can_post_blind_or_straddle():
           state.post_blind_or_straddle()
       elif state.can_burn_card():
           state.burn_card('??')
       elif state.can_deal_hole():
           state.deal_hole()
       elif state.can_deal_board():
           state.deal_board()
       elif state.can_kill_hand():
           state.kill_hand()
       elif state.can_push_chips():
           state.push_chips()
       elif state.can_pull_chips():
           state.pull_chips()
       else:
           action = input('Action: ')

           parse_action(state, action)

Type Checking
-------------

All code in PokerKit passes ``--strict`` type checking with MyPy, with one caveat: all chip values are pretended to be integral (``int``). Technically, PokerKit also supports alternative numeric types like ``float``, etc. However, the type annotations for chip values do not reflect this as there is no simple way to express the acceptance of different numeric types (although I suspect it is possible).

Game Tree Construction
----------------------

PokerKit's game simulation mechanics are well-suited for monte-carlo simulations. But, to use this library for game state construction, a careful consideration of the implementation and Python's dataclasses are necessary. One can use Python's ``copy.deepcopy`` function and checking of the validity of operations to build a game tree.

Automations
-----------

PokerKit allows fine-grained control of very detailed aspect of poker games, but many people may not be familiar with the details of each operations. As such, it is recommended for new users to first automate as much as possible before removing automations and incorporating fine-grained control away from PokerKit's automation mechanics.

Read-only and Read-Write Values
-------------------------------

Some fields/attributes in PokerKit are designed to be readonly. Most of these accesses (but not all) are enforced at the Python's ``dataclasses.dataclass`` level. An exception is for the attributes of :class:`pokerkit.state.State`. They should never be modified but instead let PokerKit modify them through public method calls. In other words, the user must only read from the state's attributes or call public methods (which may modify them).

In general, one should never call protected (denoted with a preceding ``_`` character in their names) or private methods for anything in PokerKit.

Assertions
----------

Inside PokerKit, assertions are only used for sanity checks. It is **never** used for anything meaningful in PokerKit. As there are many assertions throughout the code, if speed is a concern, one can safely disable assertions in Python by turning on appropriate optimizations for the Python interpreter (e.g. ``-O`` flag or the ``PYTHONOPTIMIZE`` environmental variable).

Standpatters
------------

Unfortunately, when I was writing this library, I did not realize the word "standpatter" (or "stand-patter") exists (see `this Wikipedia entry <https://en.wikipedia.org/wiki/Standpatter_Republican>`_). This is why I used the term "stander-pat" instead (e.g. :attr:`stander_pat_or_discarder_index`). If I had known this earlier, I would have named the attribute differently.
