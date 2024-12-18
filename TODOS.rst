=====
Todos
=====

Here are some of the features that are planned to be implemented in the future.

- Fully pre-define all variants in the 2023 World Series of Poker Tournament Rules.

  - URL: https://www.wsop.com/2022/2023-WSOP-Tournament-Rules.pdf
  - Add mock games to the unit test for each variant.

- Improved type annotations.

  - The code supports both ``int`` and ``float`` but type annotations for static type checking only support ``int``.

- Sandbox mode

  - Do not care about errors

- If both hole and board dealings are pending, card burning can be deferred so that one of the dealings is carried out before (for Courchevel).
- In non-uniform ante situations (e.g. button ante, BB ante), the paid ante(s) does not impact the pot bet during pre-flop (after flop, ante contributions are also considered to calculate the pot value).
- Faster hand evaluation for 6/7 card combinations.
- Faster hand strength and equity calculations.
- Allow callbacks with sampled hands in equity and hand strength calculations. This can be used for getting winning hand's distributions.
