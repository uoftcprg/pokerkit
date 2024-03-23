Code Snippets
=============

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
