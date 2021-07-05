from enum import Enum, unique


@unique
class Rank(Enum):
    """Rank is the enum class for ranks."""
    TWO = '2'
    '''The rank of 2.'''
    THREE = '3'
    '''The rank of 3.'''
    FOUR = '4'
    '''The rank of 4.'''
    FIVE = '5'
    '''The rank of 5.'''
    SIX = '6'
    '''The rank of 6.'''
    SEVEN = '7'
    '''The rank of 7.'''
    EIGHT = '8'
    '''The rank of 8.'''
    NINE = '9'
    '''The rank of 9.'''
    TEN = 'T'
    '''The rank of 10.'''
    JACK = 'J'
    '''The rank of Jacks.'''
    QUEEN = 'Q'
    '''The rank of Queens.'''
    KING = 'K'
    '''The rank of Kings.'''
    ACE = 'A'
    '''The rank of Aces.'''

    @property
    def _index(self):
        return tuple(Rank).index(self)


@unique
class Ranks(Enum):
    """Suit is the enum class for tuples of ranks."""
    STANDARD_RANKS = tuple(Rank)
    '''The standard ranks (from deuce to ace).'''
    SHORT_DECK_RANKS = tuple(Rank)[Rank.SIX._index:]
    '''The short-deck ranks (from six to ace).'''
    ACE_LOW_RANKS = (Rank.ACE,) + tuple(Rank)[:Rank.ACE._index]
    '''The ace-low ranks (from ace to king).'''


@unique
class Suit(Enum):
    """Suit is the enum class for suits."""
    CLUB = 'c'
    '''The suit of clubs.'''
    DIAMOND = 'd'
    '''The suit of diamonds.'''
    HEART = 'h'
    '''The suit of hearts.'''
    SPADE = 's'
    '''The suit of spades.'''


class Card:
    """Card is the class for cards.

    :param rank: The optional rank of this card.
    :param suit: The optional suit of this card.
    """

    def __init__(self, rank, suit):
        self.__rank = rank
        self.__suit = suit

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.rank) ^ hash(self.suit)

    def __repr__(self):
        return self.rank.value + self.suit.value

    @property
    def rank(self):
        """Returns the rank of this card.

        :return: The rank of this card.
        """
        return self.__rank

    @property
    def suit(self):
        """Returns the suit of this card.

        :return: The suit of this card.
        """
        return self.__suit


class HoleCard(Card):
    """HoleCard is the class for hole cards.

    :param status: The status of this card. True if exposed, False otherwise.
    :param card: The card value.
    """

    def __init__(self, status, card):
        super().__init__(card.rank, card.suit)

        self.__status = status

    def __str__(self):
        return repr(self) if self.status else '??'

    @property
    def status(self):
        """Returns the status of this hole card.

        :return: True if this hole card is exposed, False otherwise.
        """
        return self.__status
