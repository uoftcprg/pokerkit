Interacting with PokerTools
===========================

In order to use the pokertools package in your project, you must first import it.

.. code-block:: python

   from pokertools import *

Creating cards are very simple.

.. code-block:: python

   from pokertools import Card, HoleCard, Rank, Suit, parse_card, parse_cards, parse_range, rainbow, suited

   # Create a card instance
   print(Card(Rank.FOUR, Suit.HEART))  # 4h
   print(Card(Rank('4'), Suit('h')))  # 4h
   print(parse_card('4h'))  # 4h

   # Create multiple card instances
   print(list(parse_cards('4h4s4cAs')))  # [4h, 4s, 4c, As]
   print(tuple(parse_cards('4h4s4cAs')))  # (4h, 4s, 4c, As)
   print(parse_range('AKo'))  # {frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), frozenset({Ks, Ac}), ...}
   print(parse_range('AKs'))  # {frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})}
   print(parse_range('AK'))  # {frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), frozenset({Kh, Ac}), ...}
   print(parse_range('AA'))  # {frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), frozenset({As, Ac}), ...}
   print(parse_range('QQ+'))  # {frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), frozenset({Qd, Qc}), ...}
   print(parse_range('QT+'))  # {frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), frozenset({Jh, Qc}), ...}
   print(parse_range('J5o+'))  # {frozenset({Jc, 5d}), frozenset({Jc, 5d}), frozenset({Jh, 7c}), frozenset({Js, 6d}), ...}
   print(parse_range('J5s+'))  # {frozenset({Jc, 5c}), frozenset({Jd, 5d}), frozenset({Jc, 6c}), frozenset({Jd, 6d}), ...}

   # Create hole cards
   print(HoleCard(True, parse_card('As')))  # As
   print(HoleCard(False, parse_card('As')))  # As
   print(str(HoleCard(False, parse_card('As'))))  # ??

   # Query cards
   print(suited(parse_cards('4h4s4cAs')))  # False
   print(suited(parse_cards('3s4sAs')))  # True
   print(rainbow(parse_cards('4h4s4cAs')))  # False
   print(rainbow(parse_cards('4c4d4hAs')))  # True

The following code demonstrates interacting with decks.

.. code-block:: python

   from pokertools import StandardDeck, parse_card, parse_cards

   deck = StandardDeck()  # Create a shuffled standard deck (52 cards)

   print(len(deck))  # 52
   print(parse_card('4h') in deck)  # True

   deck.draw(parse_cards('4h4s4cAs'))  # Draw the following cards from the deck

   print(len(deck))  # 48
   print(parse_card('4h') in deck)  # False

   deck.draw(5)  # Draw 5 cards from the deck (from the beginning of the deck)

   print(len(deck))  # 43
   print(deck)  # [Kd, 3c, Js, 2s, ...]

The following code demonstrates interacting with evaluators. The evaluated hands are ordered so that stronger are
treated as being greater, and vice versa.

.. code-block:: python

   from pokertools import StandardEvaluator, parse_cards

   print(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKdKh'))
         < StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJsTs')))  # True
   print(StandardEvaluator.evaluate(parse_cards('AcAd'), parse_cards('AhAsKcKd'))
         < StandardEvaluator.evaluate(parse_cards('AcKs'), parse_cards('AhAsQsJs')))  # False

For more information, you can look at the PokerTools API documentations.
