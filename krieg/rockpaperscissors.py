"""This module defines various components of rock paper scissors games."""

from random import choice

from auxiliary import IndexedEnum, maxima, minima

from krieg.game import Action, Actor, Game


class RockPaperScissorsGame(Game):
    """The class for rock paper scissors games."""

    def __init__(self, player_count=2):
        super().__init__(None, (
            RockPaperScissorsPlayer(self) for _ in range(player_count)
        ))

        if player_count < 2:
            raise ValueError('less than 2 players')

    @property
    def winners(self):
        """Determine the winner of this rock paper scissors game.

        >>> game = RockPaperScissorsGame(3)
        >>> game.throw(
        ...     RockPaperScissorsHand.PAPER,
        ...     RockPaperScissorsHand.ROCK,
        ...     RockPaperScissorsHand.PAPER,
        ... )
        <RockPaperScissorsGame>
        >>> tuple(game.winners)
        (<RockPaperScissorsPlayer 0>, <RockPaperScissorsPlayer 2>)

        :return: The winning players if this game is terminal, else
                 ``None``.
        """
        if not self.is_terminal():
            return None

        hands = map(RockPaperScissorsPlayer.hand.fget, self.players)

        if len(set(hands)) != 2:
            return iter(())

        return maxima(self.players, key=RockPaperScissorsPlayer.hand.fget)

    @property
    def losers(self):
        """Determine the losers of this rock paper scissors game.

        >>> game = RockPaperScissorsGame(3)
        >>> game.throw(
        ...     RockPaperScissorsHand.PAPER,
        ...     RockPaperScissorsHand.ROCK,
        ...     RockPaperScissorsHand.PAPER,
        ... )
        <RockPaperScissorsGame>
        >>> tuple(game.losers)
        (<RockPaperScissorsPlayer 1>,)

        :return: The losing players if this game is terminal, else
                 ``None``.
        """
        if not self.is_terminal():
            return None

        hands = map(RockPaperScissorsPlayer.hand.fget, self.players)

        if len(set(hands)) != 2:
            return iter(())

        return minima(self.players, key=RockPaperScissorsPlayer.hand.fget)

    def throw(self, *hands):
        """Throw the given hands.

        >>> game = RockPaperScissorsGame()
        >>> game.throw(RockPaperScissorsHand.PAPER, RockPaperScissorsHand.ROCK)
        <RockPaperScissorsGame>
        >>> game.players[0].hand.value
        'Paper'
        >>> game.players[1].hand.value
        'Rock'

        :param hands: The hands to throw.
        :return: This game.
        """
        for player, hand in zip(self.players, hands):
            if player.can_throw(hand):
                player.throw(hand)

        return self

    def is_terminal(self):
        return all(map(RockPaperScissorsPlayer.hand.fget, self.players))


class RockPaperScissorsHand(IndexedEnum):
    """The enum class for rock paper scissors hands.

    The rock paper scissors hand can be compared to each other according
    to the rock paper scissors rules.
    """

    ROCK = 'Rock'
    """The rock hand."""
    PAPER = 'Paper'
    """The paper hand."""
    SCISSORS = 'Scissors'
    """The scissors hand."""

    def __lt__(self, other):
        if isinstance(other, RockPaperScissorsHand):
            return (self.index + 1) % 3 == other.index
        else:
            return NotImplemented


class ThrowingAction(Action):
    """ThrowingAction is a class for throwing actions in rock paper
    scissors games.

    If the hand to be thrown is not specified, a random one is chosen.

    :param hand: The optional hand to be thrown.
    """

    def __init__(self, actor, hand=None):
        super().__init__(actor)

        self.hand = hand

    def _verify(self):
        super()._verify()

        if self.actor.hand is not None:
            raise ValueError('player already threw')

    def _apply(self):
        super()._apply()

        if self.hand is None:
            self.hand = choice(tuple(RockPaperScissorsHand))

        self.actor._hand = self.hand


class RockPaperScissorsPlayer(Actor):
    """The class for rock paper scissors players.

    :param game: The game of this rock paper scissors actor.
    """

    throw, can_throw = ThrowingAction.create_methods()

    def __init__(self, game):
        super().__init__(game)

        self._hand = None

    @property
    def hand(self):
        """Return ``None`` if this rock paper scissors did not throw a
        hand, else the hand that this rock paper scissors player threw.

        >>> game = RockPaperScissorsGame()
        >>> print(game.players[1].hand)
        None
        >>> game.players[1].throw(RockPaperScissorsHand.SCISSORS)
        >>> print(game.players[1].hand)
        RockPaperScissorsHand.SCISSORS

        :return: The hand of this rock paper scissors player.
        """
        return self._hand
