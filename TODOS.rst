=====
Todos
=====

Here are some of the features that are planned to be implemented in the future.

- Fully pre-define all variants listed in the 2023 World Series of Poker Tournament Rules.

  - URL: https://www.wsop.com/2022/2023-WSOP-Tournament-Rules.pdf
  - Add mock games to the unit test for each variant.

- Add unit tests for all WSOP poker tournament rules in ``pokerkit/tests/test_rules.py``.
- Improve type annotations.

  - Currently, the code supports both ``int`` and ``float``, but type annotations for static type checking shows that only ``int`` is supported.

- Sandbox mode

  - Do not care about errors.

- In non-uniform ante situations (e.g. button ante, BB ante), make it so the paid ante(s) does not impact the pot bet during pre-flop (right now, after flop, ante contributions are also considered to calculate the pot value).
- Faster hand evaluation for 6/7 card combinations.
- Faster hand strength and equity calculations.
- Allow callbacks with sampled hands in equity and hand strength calculations. This can be used for getting winning hand's distributions.
- Keep track of more things in ``pokerkit.analysis.Statistics`` while avoiding requiring new dependencies to PokerKit like ``numpy``.
- More robust implementation of poker hand history parsers (it seems quite fragile as it stands right now).
