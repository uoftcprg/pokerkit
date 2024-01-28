=====
Todos
=====

Here are some of the features that are planned to be implemented in the future.

- Post bets support.

  - Post bets are posted when a player wants to play a game immediately after joining without waiting for the button to pass him or her.
  - This is demonstrably different from blinds or straddles
  - As an optional parameter

- Unknown stacks support.

  - One can pass ``math.inf`` as the unknown starting stack.

- Fully comply with the Poker Hand History file format specs.

  - URL: https://arxiv.org/abs/2312.11753

- Parser for the PokerStars hand history file format.
- Fully pre-define all variants in the 2023 World Series of Poker Tournament Rules.

  - URL: https://www.wsop.com/2022/2023-WSOP-Tournament-Rules.pdf
  - Add mock games to the unit test for each variant.

- Improved type annotations.

  - The code supports both ``int`` and ``float`` but type annotations for static type checking only support ``int``.

- Sandbox mode

  - Do not care about errors
