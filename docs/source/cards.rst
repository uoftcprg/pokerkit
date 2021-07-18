Creating Cards and Hole Cards
=============================

The :mod:`pokertools.cards` module contains various data types related to cards and their components, along with various
functions for bulk creations and queries.

Basic Data Types
----------------

Cards are of type :class:`pokertools.cards.Card` and they contain information about the card's
:attr:`pokertools.cards.Card.rank` and :attr:`pokertools.cards.Card.suit`. For hole cards, there is an extra attribute
called :class:`pokertools.cards.HoleCard.status`, denoting whether if the hole card is face down or up.

Ranks and Suits are enumerations with the following members:

- Rank: :class:`pokertools.cards.Rank`
   - Two: :attr:`pokertools.cards.Rank.TWO`
   - Three: :attr:`pokertools.cards.Rank.THREE`
   - ... (skipped)
   - Queen: :attr:`pokertools.cards.Rank.QUEEN`
   - King: :attr:`pokertools.cards.Rank.KING`
   - Ace: :attr:`pokertools.cards.Rank.ACE`
- Suit: :class:`pokertools.cards.Suit`
   - Club: :attr:`pokertools.cards.Suit.CLUB`
   - Diamond: :attr:`pokertools.cards.Suit.DIAMOND`
   - Heart: :attr:`pokertools.cards.Suit.HEART`
   - Spade: :attr:`pokertools.cards.Suit.SPADE`

Above member variables contain single character representations of themselves as their values.

Some games define different orders of ranks. So, there exists :class:`pokertools.cards.Ranks` enumeration class for
various rank order formats.

- Ranks: :class:`pokertools.cards.Ranks`
   - Standard Ranks (Ace high with all ranks from 2 to Ace): :attr:`pokertools.cards.Ranks.STANDARD`
   - Short Deck Ranks (Ace high with all ranks from 6 to Ace): :attr:`pokertools.cards.Ranks.SHORT_DECK`
   - Ace Low Ranks (Ace low with all ranks from 2 to Ace): :attr:`pokertools.cards.Ranks.ACE_LOW`

While the rank ordering is not so relevant when creating cards, they play a role in the creations of decks and lookup
tables for hand evaluations.

Creating Card Instances
-----------------------

Cards and hole cards are of type :class:`pokertools.cards.Card` and :class:`pokertools.cards.HoleCard`. Creating cards
are very simple, as demonstrated below.

.. code-block:: python

   from pokertools import *

   # Create cards
   print(Card(Rank.FOUR, Suit.HEART))  # 4h
   print(Card(Rank('4'), Suit('h')))  # 4h
   print(parse_card('4h'))  # 4h

   # Create hole cards
   print(HoleCard(True, parse_card('As')))  # As
   print(HoleCard(False, parse_card('As')))  # As
   print(HoleCard(False, parse_card('As')))  # As
   print(str(HoleCard(False, parse_card('As'))))  # ??

Cards accept a rank and a suit during its construction. In order to create hole cards, you must supply the status of the
card, which denotes whether or not the card is face down or up, and supply the card data by supplying the card from
which to copy the data.

The card data can be accessed as below.

.. code-block:: python

   from pokertools import *

   # Create a card
   card = parse_card('4h')

   print(card.rank)  # Four
   print(card.suit)  # Heart

   # Create a hole card
   hole_card = HoleCard(False, parse_card('As'))

   print(hole_card.rank)  # Ace
   print(hole_card.suit)  # Spades
   print(hole_card.status)  # False

Note that hole cards instances are also card instances. So, they can access rank and suit attributes just like cards do.

Bulk Card Creations
-------------------

Creating cards one by one can make code become very long. There are functions that help circumvent this.

.. code-block:: python

   from pokertools import *

   # Create an iterable of cards
   print(list(parse_cards('4h4s4cAs')))  # An iterator (unintelligible)
   print(list(parse_cards('4h4s4cAs')))  # [4h, 4s, 4c, As]
   print(tuple(parse_cards('4h4s4cAs')))  # (4h, 4s, 4c, As)

   # Parse a range
   print(parse_range('AKo'))  # {frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), frozenset({Ks, Ac}), ...}
   print(parse_range('AKs'))  # {frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})}
   print(parse_range('AK'))  # {frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), frozenset({Kh, Ac}), ...}
   print(parse_range('AA'))  # {frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), frozenset({As, Ac}), ...}
   print(parse_range('QQ+'))  # {frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), frozenset({Qd, Qc}), ...}
   print(parse_range('QT+'))  # {frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), frozenset({Jh, Qc}), ...}
   print(parse_range('J5o+'))  # {frozenset({Jc, 5d}), frozenset({Jc, 5d}), frozenset({Jh, 7c}), frozenset({Js, 6d}), ...}
   print(parse_range('J5s+'))  # {frozenset({Jc, 5c}), frozenset({Jd, 5d}), frozenset({Jc, 6c}), frozenset({Jd, 6d}), ...}

As shown above, you can pass a string of multiple of cards or a range of cards to parse them and create them in bulk. To
see how ranges are parsed, read up related poker articles from the internet.

Card Queries
------------

Sometimes a group of cards are denoted as being suited or having a rainbow texture. These functions are already
implemented for you. See below for demonstrations on how to use them.

.. code-block:: python

   from pokertools import *

   # Query cards
   print(suited(parse_cards('4h4s4cAs')))  # False
   print(suited(parse_cards('3s4sAs')))  # True
   print(rainbow(parse_cards('4h4s4cAs')))  # False
   print(rainbow(parse_cards('4c4d4hAs')))  # True
