Interacting with PokerTools
===========================

In order to use the pokertools package in your project, you must first import it.

.. code-block:: python

   from pokertools import ...


The following code demonstrates interacting with cards.

.. code-block:: python

   >>> from pokertools import Card, HoleCard, Rank, Suit, parse_card, parse_cards, suited
   >>> Card(Rank.FOUR, Suit.HEART)
   4h
   >>> parse_card('4h')
   4h
   >>> tuple(parse_cards('4h4s4cAs'))
   (4h, 4s, 4c, As)
   >>> suited(parse_cards('4h4s4cAs'))
   False
   >>> HoleCard(True, parse_card('As'))
   As
   >>> HoleCard(False, parse_card('As'))
   As
   >>> str(HoleCard(False, parse_card('As')))
   ??


The following code demonstrates interacting with decks.

.. code-block:: python

   >>> from pokertools import StandardDeck, parse_card, parse_cards
   >>> deck = StandardDeck()
   >>> parse_card('4h') in deck
   True
   >>> deck.draw(parse_cards('4h4s4cAs'))
   >>> parse_card('4h') in deck
   False

The following code demonstrates interacting with evaluators.

.. code-block:: python

   >>> from pokertools import StandardEvaluator, parse_cards
   >>> StandardEvaluator.hand(parse_cards('AcAd'), parse_cards('AhAsKcKdKh')) \
   ...     < StandardEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsQsJsTs'))
   True
   >>> StandardEvaluator.hand(parse_cards('AcAd'), parse_cards('AhAsKcKd')) \
   ...     < StandardEvaluator.hand(parse_cards('AcKs'), parse_cards('AhAsQsJs'))
   False

The following code demonstrates interacting with ranges.

.. code-block:: python

   >>> from pokertools import parse_range
   >>> parse_range('AKo')
   {frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), ..., frozenset({Ks, Ac})}
   >>> parse_range('AKs')
   {frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})}
   >>> parse_range('AK')
   {frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), ..., frozenset({Kh, Ac})}
   >>> parse_range('AA')
   {frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), ..., frozenset({As, Ac})}
   >>> parse_range('QQ+')
   {frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), ..., frozenset({Qd, Qc})}
   >>> parse_range('QT+')
   {frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), ..., frozenset({Jh, Qc})}


For more information, you can look at the PokerTools API documentations.
