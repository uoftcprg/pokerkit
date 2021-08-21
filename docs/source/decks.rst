Using Decks
===========

Decks, in PokerFace, can be thought of as a list of card instances. All
deck subclasses inherit from the base class
:class:`pokerface.decks.Deck`. They are all shuffled upon creation.
Allowing you to use them right after creation without shuffling them
first.

Currently, there are two types of decks:

- Standard Deck: :class:`pokerface.decks.StandardDeck`
- Short Deck: :class:`pokerface.decks.ShortDeck`

Standard decks are 52 card decks that are most commonly used. Short
decks are 36 card decks that do not have cards with ranks below 6.

Creating Decks
--------------

The following code demonstrates creating decks.

.. code-block:: python

   from pokerface import *

   # Create a standard deck
   standard_deck = StandardDeck()
   # Create a short deck
   short_deck = ShortDeck()
   # Create an empty deck
   empty_deck = Deck()
   # Create a custom deck of 4 cards
   custom_deck = Deck(parse_cards('4h4s4cAs'))

Remember that all decks are shuffled upon creation.

Deck operations
---------------

The method :meth:`pokerface.decks.Deck.draw` allow you to draw cards
from decks.

.. code-block:: python

   from pokerface import *

   # Create a shuffled standard deck (52 cards).
   deck = StandardDeck()

   print(len(deck))  # 52
   print(parse_card('4h') in deck)  # True

   # Draw the following cards from the deck.
   print(deck.draw(parse_cards('4h4s4cAs')))  # [4h, 4s, 4c, As]

   print(len(deck))  # 48
   print(parse_card('4h') in deck)  # False

   # Draw 5 cards from the deck (from the beginning of the deck).
   print(deck.draw(5))  # [5h, Jh, 7h, 2s, Tc]

   print(len(deck))  # 43
   print(deck)  # [7d, 3s, Ac, Qh, ..., 7c, Td]

As :class:`pokerface.decks.Deck` is a subclass of ``list``, it also has
all the methods defined in lists.

.. code-block:: python

   from pokerface import *

   # Create a shuffled standard deck (52 cards)
   deck = StandardDeck()

   deck.pop()
   deck.append(parse_card('Ks'))
   ...

For example, if you want to order the cards in the deck nicely, you can
do what's done below:

.. code-block:: python

   from pokerface import *

   deck = StandardDeck()

   # Print a shuffled deck.
   print(deck)  # [Ad, 7s, 7d, 3c, ..., Ac, Qh]

   # Sort the deck in place.
   deck.sort()

   # Print an ordered deck.
   print(deck)  # [2c, 3c, 4c, 5c, ..., Ks, As]

Custom Decks
------------

Creating and using customized decks are explained in the later section.
