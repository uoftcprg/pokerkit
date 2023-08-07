=========
Changelog
=========

All notable changes to this project will be documented in this file.

Version 0.0.1 (August 7, 2023)
------------------------------

- Modify the methods that only accepted an iterable of ``Card`` so they can
  accept any card-like object.
- Make the protected attributes in the ``Hand`` type and its descendants public.
- Move ``pokerkit.state.State._clean_cards`` and
  ``pokerkit.games.Game._clean_values`` to ``pokerkit.utilities``.
