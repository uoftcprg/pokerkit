from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence
from itertools import zip_longest
from typing import Final, Optional, cast, final, overload

from auxiliary import iter_equal
from pokertools import Card, Deck, Evaluator, Hand, HoleCard

from gameframe.exceptions import GameFrameError
from gameframe.game import Actor
from gameframe.sequential import SequentialGame


class Poker(SequentialGame['PokerNature', 'PokerPlayer'], ABC):
    """Poker is the abstract base class for all poker games.

    When a PokerGame instance is created, its deck, evaluator, limit, and streets are also created through the
    invocations of corresponding create methods, which should be overridden by the subclasses. Also, every subclass
    should override the ante, blinds, and starting_stacks properties accordingly.

    The number of players, denoted by the length of the starting_stacks property, must be greater than or equal to 2.

    :param stages: The stages of this poker game.
    :param evaluators: The evaluators of this poker game.
    :param deck: The deck of this poker game.
    :param limit: The limit of this poker game.
    :param ante: The ante of this poker game.
    :param blinds: The blinds of this poker game.
    :param starting_stacks: The starting stacks of this poker game.
    """

    def __init__(
            self,
            stages: Sequence[Stage],
            evaluators: Sequence[Evaluator],
            deck: Deck,
            limit: Limit,
            ante: int,
            blinds: Sequence[int],
            starting_stacks: Sequence[int],
    ):
        from gameframe.poker import ShowdownStage

        super().__init__(None, PokerNature(self), (PokerPlayer(self) for _ in range(len(starting_stacks))))

        self.stages: Final = tuple(stages)
        '''The stages of this poker game.'''
        self.evaluators: Final = tuple(evaluators)
        '''The evaluators of this poker game.'''
        self.limit: Final = limit
        '''The limit of this poker game.'''
        self.ante: Final = ante
        '''The ante of this poker game.'''
        self.blinds: Final = tuple(blinds)
        '''The blinds of this poker game.'''
        self.starting_stacks: Final = tuple(starting_stacks)
        '''The starting stacks of this poker game.'''

        self._deck = deck
        self._stage = self.stages[0]

        if len(self.starting_stacks) < 2:
            raise GameFrameError('Poker needs at least 2 players')
        elif not iter_equal(self.blinds, sorted(self.blinds)):
            raise GameFrameError('Blinds must be sorted')
        elif len(self.blinds) > len(self.starting_stacks):
            raise GameFrameError('Number of blinds must be less than or equal to the number of players')
        elif not self.stages:
            raise GameFrameError('Number of stages must be at least 1')
        elif not isinstance(self.stages[-1], ShowdownStage):
            raise GameFrameError('The final stage must be a showdown stage')
        elif any(value < 0 for value in (self.ante,) + self.blinds + self.starting_stacks):
            raise GameFrameError('All numerical values must be positive')
        elif not self.evaluators:
            raise GameFrameError('Number of evaluators must be at least 1')

        self._pot = 0
        self._board = list[Card]()
        self._queue = list[PokerPlayer]()
        self._aggressor: Optional[PokerPlayer] = None
        self._bet_raise_count = 0
        self._max_delta = 0

        self._setup()

    @property
    @final
    def deck(self) -> Sequence[Card]:
        """Returns the deck of this poker game.

        :return: The deck of this poker game.
        """
        return self._deck

    @property
    @final
    def stage(self) -> Stage:
        """Returns the stage of this poker game.

        :return: The stage of this poker game.
        """
        return self._stage

    @property
    @final
    def pot(self) -> int:
        """Returns the pot of this poker game.

        :return: The pot of this poker game.
        """
        return self._pot

    @property
    @final
    def board(self) -> Sequence[Card]:
        """Returns the board of this poker game.

        The board contains the public cards in a poker game. They can be combined with individual player's hole cards to
        create a hand.

        :return: The board of this poker game.
        """
        return self._board

    @property
    @final
    def side_pots(self) -> Iterator[int]:
        """Returns the side pots of this poker game.

        :return: The side pots of this poker game.
        """
        return (side_pot.amount for side_pot in self._side_pots)

    @property
    def _side_pots(self) -> Sequence[_SidePot]:
        players = sorted(self.players, key=lambda player: player.put)
        side_pots = []
        pot = 0
        prev = 0

        while pot < self.pot:
            cur = min(player.put for player in players)
            amount = len(players) * (cur - prev)

            side_pots.append(_SidePot((player for player in players if player.active), amount))

            players.pop(0)
            pot += amount
            prev = cur

        return side_pots

    def _setup(self) -> None:
        for i, (blind, stack, player) in enumerate(zip_longest(
                reversed(self.blinds) if len(self.players) == 2 else self.blinds,
                self.starting_stacks,
                self.players,
                fillvalue=0,
        )):
            ante = min(self.ante, stack)
            blind = max(min(blind, stack - ante), 0)

            self._pot += ante
            player._bet = blind
            player._stack = stack - ante - blind

        self._aggressor = max(self.players, key=lambda player_: player_.bet)

        self.stage._open(self)


@final
class PokerNature(Actor[Poker]):
    """PokerNature is the class for poker natures."""

    def __repr__(self) -> str:
        return 'PokerNature'

    @property
    def dealable_players(self) -> Iterator[PokerPlayer]:
        """Returns an iterator of poker players that can be dealt.

        :return: The players that can be dealt.
        """
        if self.can_deal_hole():
            return filter(self.can_deal_hole, self.game.players)
        else:
            raise GameFrameError('The nature cannot deal hole cards')

    @property
    def hole_deal_count(self) -> int:
        """Returns the number of hole cards that can be dealt to each player.

        :return: The number of hole cards to deal.
        """
        if self.can_deal_hole():
            return self.game.stage._deal_count
        else:
            raise GameFrameError('The nature cannot deal hole cards')

    @property
    def board_deal_count(self) -> int:
        """Returns the number of cards that can be dealt to the board.

        :return: The number of cards to deal.
        """
        if self.can_deal_board():
            return self.game.stage._deal_count
        else:
            raise GameFrameError('The nature cannot deal board cards')

    @overload
    def deal_hole(self) -> None:
        ...

    @overload
    def deal_hole(self, player: PokerPlayer) -> None:
        ...

    @overload
    def deal_hole(self, player: PokerPlayer, cards: Iterable[Card]) -> None:
        ...

    def deal_hole(self, player: Optional[PokerPlayer] = None, cards: Optional[Iterable[Card]] = None) -> None:
        """Deals the optionally supplied hole cards to the optionally specified player.

        If the cards are not supplied, they are randomly drawn from the deck. If the player is not known, the next
        player in order who is dealable will be dealt.

        :param player: The optional player to deal to.
        :param cards: The optional hole cards to be dealt.
        :return: None.
        """
        from gameframe.poker._actions import HoleDealingAction

        HoleDealingAction(player, cards, self).act()

    @overload
    def can_deal_hole(self) -> bool:
        ...

    @overload
    def can_deal_hole(self, player: PokerPlayer) -> bool:
        ...

    @overload
    def can_deal_hole(self, player: PokerPlayer, cards: Iterable[Card]) -> bool:
        ...

    def can_deal_hole(self, player: Optional[PokerPlayer] = None, cards: Optional[Iterable[Card]] = None) -> bool:
        """Determines if the optionally specified hole cards can be dealt to the optionally supplied player.

        :param player: The optional player to deal to.
        :param cards: The optional hole cards to be dealt.
        :return: True if the hole cards dealt, else False.
        """
        from gameframe.poker._actions import HoleDealingAction

        return HoleDealingAction(player, cards, self).can_act()

    def deal_board(self, cards: Optional[Iterable[Card]] = None) -> None:
        """Deals the optionally specified cards to the board.

        If none is given as cards, sample cards are randomly selected from the deck.

        :param cards: The optional cards to be dealt.
        :return: None.
        """
        from gameframe.poker._actions import BoardDealingAction

        BoardDealingAction(cards, self).act()

    def can_deal_board(self, cards: Optional[Iterable[Card]] = None) -> bool:
        """Determines if cards can be dealt to the board.

        :param cards: The optional cards to be dealt.
        :return: True if the board can be dealt, else False.
        """
        from gameframe.poker._actions import BoardDealingAction

        return BoardDealingAction(cards, self).can_act()


@final
class PokerPlayer(Actor[Poker]):
    """PokerPlayer is the class for poker players.

    :param game: The game of this poker player.
    """

    def __init__(self, game: Poker):
        super().__init__(game)

        self._bet = 0
        self._stack = 0
        self._hole = list[HoleCard]()
        self._status: Optional[bool] = None

    def __repr__(self) -> str:
        if self.mucked:
            return f'PokerPlayer({self.bet}, {self.stack})'
        else:
            return f'PokerPlayer({self.bet}, {self.stack}, ' + ''.join(map(str, self.hole)) + ')'

    @property
    def bet(self) -> int:
        """Returns the bet of this poker player.

        :return: The bet of this poker player.
        """
        return self._bet

    @property
    def stack(self) -> int:
        """Returns the stack of this poker player.

        :return: The stack of this poker player.
        """
        return self._stack

    @property
    def hole(self) -> Sequence[HoleCard]:
        """Returns the hole cards of this poker player.

        :return: The hole cards of this poker player.
        """
        if self._status is None:
            return self._hole
        else:
            return tuple(HoleCard(self._status, card) for card in self._hole)

    @property
    def starting_stack(self) -> int:
        """Returns the starting stack of this poker player.

        :return: The starting stack of this poker player.
        """
        return self.game.starting_stacks[self.game.players.index(self)]

    @property
    def total(self) -> int:
        """Returns the total of the bet and the stack of this poker player.

        In other words, returns the sum of this player's bet and stack.

        :return: The total of he bet and the stack of this poker player.
        """
        return self.bet + self.stack

    @property
    def effective_stack(self) -> int:
        """Returns the effective stack of this poker player.

        The effective stacks are maximum amount that the poker player can lose in a current poker game state.

        :return: The effective stack of this poker player.
        """
        active_players = tuple(player for player in self.game.players if player.active)

        if self.mucked or len(active_players) < 2:
            return 0
        else:
            return min(self.starting_stack, sorted(player.starting_stack for player in active_players)[-2])

    @property
    def put(self) -> int:
        """Returns the amount put into the pot by this poker player.

        :return: The amount put by this poker player.
        """
        return max(self.starting_stack - self.total, 0)

    @property
    def hands(self) -> Iterator[Hand]:
        """Returns the hands of this poker player.

        The hands are arranged in the order of evaluators of the associated poker game. Usually, poker games only have
        one evaluator type, in which case this property will be a singleton iterator. However, sometimes, a poker game
        may have hi and lo evaluator. Then, this property will be a pair of hi and lo hands.

        :return: The hands of this poker player.
        """
        return (self._hand(evaluator) for evaluator in self.game.evaluators)

    @property
    def mucked(self) -> bool:
        """Returns whether or not the player has mucked his/her hand.

        :return: True if this poker player has mucked his/her hand, else False.
        """
        return self._status is False

    @property
    def shown(self) -> bool:
        """Returns whether or not the player has shown his/her hand.

        :return: True if this poker player has shown his/her hand, else False.
        """
        return self._status is True

    @property
    def active(self) -> bool:
        """Returns whether or not the player is active.

        The player is active if he/she is in a hand.

        :return: True if this poker player is active, else False.
        """
        return not self.mucked

    @property
    def check_call_amount(self) -> int:
        """Returns the check/call amount.

        If the player checks, 0 is returned.

        :return: The check/call amount.
        """
        if self.can_check_call():
            return min(self.stack, max(player.bet for player in self.game.players) - self.bet)
        else:
            raise GameFrameError('The player cannot check/call')

    @property
    def min_bet_raise_amount(self) -> int:
        """Returns the minimum bet/raise amount.

        The minimum bet/raise amount is set by the limit of the poker game.

        :return: The minimum bet/raise amount.
        """
        if self.can_bet_raise():
            return self.game.limit._min_amount(self.game)
        else:
            raise GameFrameError('The player cannot bet/raise')

    @property
    def max_bet_raise_amount(self) -> int:
        """Returns the maximum bet/raise amount.

        The maximum bet/raise amount is set by the limit of the poker game.

        :return: The maximum bet/raise amount.
        """
        if self.can_bet_raise():
            return self.game.limit._max_amount(self.game)
        else:
            raise GameFrameError('The player cannot bet/raise')

    @property
    def showdown_necessary(self) -> bool:
        """Returns whether or not showdown is necessary to win the pot.

        If any hand that beats this poker player's hand is already revealed, then the showdown would not be necessary.

        :return: True if the showdown is necessary, else False.
        """
        if self.can_showdown():
            staked = [True] * len(self.game.evaluators)

            for player in self.game.players:
                if player.shown:
                    for i, (actor_hand, player_hand) in enumerate(zip(self.hands, player.hands)):
                        if player_hand > actor_hand and player.put >= self.put:
                            staked[i] = False

            return any(staked)
        else:
            raise GameFrameError('The player cannot showdown')

    @property
    def _relevant(self) -> bool:
        return self.active and self._lost < self.effective_stack

    @property
    def _lost(self) -> int:
        return self.starting_stack - self.stack

    def fold(self) -> None:
        """Folds the poker player's hand.

        :return: None
        """
        from gameframe.poker._actions import FoldAction

        FoldAction(self).act()

    def can_fold(self) -> bool:
        """Returns whether or not the player can fold his/her hand.

        :return: True if this poker player can fold, else False
        """
        from gameframe.poker._actions import FoldAction

        return FoldAction(self).can_act()

    def check_call(self) -> None:
        """Checks or calls the opponent's bet.

        :return: None
        """
        from gameframe.poker._actions import CheckCallAction

        CheckCallAction(self).act()

    def can_check_call(self) -> bool:
        """Returns whether or not the player can check/call.

        :return: True if this poker player can check/call, else False
        """
        from gameframe.poker._actions import CheckCallAction

        return CheckCallAction(self).can_act()

    @overload
    def bet_raise(self) -> None:
        ...

    @overload
    def bet_raise(self, amount: int) -> None:
        ...

    def bet_raise(self, amount: Optional[int] = None) -> None:
        """Bets or raises to the optional amount.

        If no amount is specified, this poker player will min-raise.

        :param amount: The optional amount to bet/raise.
        :return: None
        """
        from gameframe.poker._actions import BetRaiseAction

        BetRaiseAction(amount, self).act()

    @overload
    def can_bet_raise(self) -> bool:
        ...

    @overload
    def can_bet_raise(self, amount: int) -> bool:
        ...

    def can_bet_raise(self, amount: Optional[int] = None) -> bool:
        """Returns whether or not the player can bet/raise to the optionally given bet amount.

        :param amount: The optional amount to bet/raise.
        :return: True if this poker player can bet/raise, else False
        """
        from gameframe.poker._actions import BetRaiseAction

        return BetRaiseAction(amount, self).can_act()

    @overload
    def discard_draw(self) -> None:
        ...

    @overload
    def discard_draw(self, discarded_cards: Iterable[Card]) -> None:
        ...

    @overload
    def discard_draw(self, discarded_cards: Iterable[Card], drawn_cards: Iterable[Card]) -> None:
        ...

    def discard_draw(self, discarded_cards: Iterable[Card] = (), drawn_cards: Optional[Iterable[Card]] = None) -> None:
        """Discards this poker player's optionally specified hole cards and draws the corresponding optionally given
        cards.

        If discarded cards are not specified, the poker player performs a stand pat. If the drawn cards are not
        specified, random cards will be drawn.

        :param discarded_cards: The optional cards to discard. Defaults to empty tuple (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: None
        """
        from gameframe.poker._actions import DiscardDrawAction

        DiscardDrawAction(discarded_cards, drawn_cards, self).act()

    @overload
    def can_discard_draw(self) -> bool:
        ...

    @overload
    def can_discard_draw(self, discarded_cards: Iterable[Card]) -> bool:
        ...

    @overload
    def can_discard_draw(self, discarded_cards: Iterable[Card], drawn_cards: Iterable[Card]) -> bool:
        ...

    def can_discard_draw(
            self,
            discarded_cards: Iterable[Card] = (),
            drawn_cards: Optional[Iterable[Card]] = None,
    ) -> bool:
        """Returns whether or not this poker player can discard and draw.

        :param discarded_cards: The cards to discard. Defaults to empty tuple (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: True if this poker player can discard and draw, else False.
        """
        from gameframe.poker._actions import DiscardDrawAction

        return DiscardDrawAction(discarded_cards, drawn_cards, self).can_act()

    def showdown(self, forced_status: Optional[bool] = None) -> None:
        """Showdowns this poker player's hand if necessary to win the pot or forced.

        :param forced_status: True to force showdown, False to force muck. Defaults to None.
        :return: None
        """
        from gameframe.poker._actions import ShowdownAction

        ShowdownAction(forced_status, self).act()

    def can_showdown(self, forced_status: Optional[bool] = None) -> bool:
        """Returns whether or not this poker player can showdown.

        :param forced_status: True to force showdown, False to force muck. Defaults to None.
        :return: True if this poker player can showdown, else False.
        """
        from gameframe.poker._actions import ShowdownAction

        return ShowdownAction(forced_status, self).can_act()

    def _hand(self, evaluator: Evaluator) -> Hand:
        return evaluator.hand(self.hole, self.game.board)


class _SidePot:
    def __init__(self, players: Iterable[PokerPlayer], amount: int):
        self.players: Final = tuple(players)
        self.amount: Final = amount


class Stage(ABC):
    """Stage is the abstract base class for all stages."""

    _deal_count: int

    def _deal_target(self, game: Poker) -> int:
        count = 0

        for stage in game.stages[:game.stages.index(self) + 1]:
            if isinstance(stage, type(self)):
                count += stage._deal_count

        return count

    def _done(self, game: Poker) -> bool:
        return sum(player.active for player in game.players) == 1

    def _open(self, game: Poker) -> None:
        ...

    def _close(self, game: Poker) -> None:
        ...


class Limit(ABC):
    """Limit is the abstract base class for all limits."""

    _max_count: Optional[int]

    @staticmethod
    def _min_amount(game: Poker) -> int:
        return min(max(player.bet for player in game.players) + game._max_delta, cast(PokerPlayer, game.actor).total)

    @abstractmethod
    def _max_amount(self, game: Poker) -> int: ...
