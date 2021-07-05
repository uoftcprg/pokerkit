import re
from collections.abc import Mapping, Sized
from functools import partial
from operator import gt

from gameframe.exceptions import GameFrameError
from gameframe.sequential import SequentialActor, SequentialGame

from pokertools.cards import HoleCard
from pokertools.utilities import parse_cards


class PokerGame(SequentialGame):
    """PokerGame is the class for poker games.

    When a PokerGame instance is created, its deck, evaluator, limit, and streets are also created through the
    invocations of corresponding create methods, which should be overridden by the subclasses. Also, every subclass
    should override the ante, blinds, and starting_stacks properties accordingly.

    The number of players, denoted by the length of the starting_stacks property, must be greater than or equal to 2.

    :param limit: The limit of this poker game.
    :param definition: The definition this poker game.
    :param ante: The ante of this poker game.
    :param forced_bets: The forced bets of this poker game.
    :param starting_stacks: The starting stacks of this poker game.
    """

    def __init__(self, limit, definition, ante, forced_bets, starting_stacks):
        super().__init__(None, PokerNature(self), (PokerPlayer(self) for _ in range(len(starting_stacks))))

        self.__limit = limit
        self.__definition = definition
        self.__ante = ante

        if isinstance(forced_bets, Mapping):
            forced_bets = tuple(forced_bets[i] if i in forced_bets else 0 for i in range(len(self.players)))
        elif not isinstance(forced_bets, Sized):
            forced_bets = tuple(forced_bets)

        self.__forced_bets = tuple(forced_bets) + (0,) * (len(self.players) - len(forced_bets))
        self.__starting_stacks = tuple(starting_stacks)
        self.__stages = definition.create_stages(self)
        self.__evaluators = definition.create_evaluators()

        self._deck = definition.create_deck()
        self._pot = 0
        self._board = []

        self._stage = None
        self._queue = []
        self._aggressor = None
        self._bet_raise_count = 0
        self._max_delta = 0

        self._verify()
        self._setup()

    @property
    def limit(self):
        """Returns the limit of this poker game.

        :return: The limit of this poker game.
        """
        return self.__limit

    @property
    def definition(self):
        """Returns the definition of this poker game.

        :return: The definition of this poker game.
        """
        return self.__definition

    @property
    def ante(self):
        """Returns the ante of this poker game.

        :return: The ante of this poker game.
        """
        return self.__ante

    @property
    def forced_bets(self):
        """Returns the forced bets of this poker game.

        The forced bets include the blinds and straddles.

        :return: The forced bets of this poker game.
        """
        return self.__forced_bets

    @property
    def starting_stacks(self):
        """Returns the starting stacks of this poker game.

        :return: The starting stacks of this poker game.
        """
        return self.__starting_stacks

    @property
    def stages(self):
        """Returns the stages of this poker game.

        :return: The stages of this poker game.
        """
        return self.__stages

    @property
    def evaluators(self):
        """Returns the evaluators of this poker game.

        :return: The evaluators of this poker game.
        """
        return self.__evaluators

    @property
    def deck(self):
        """Returns the deck of this poker game.

        :return: The deck of this poker game.
        """
        return tuple(self._deck)

    @property
    def pot(self):
        """Returns the pot of this poker game.

        :return: The pot of this poker game.
        """
        return self._pot

    @property
    def board(self):
        """Returns the board of this poker game.

        The board contains the public cards in a poker game. They can be combined with individual player's hole cards to
        create a hand.

        :return: The board of this poker game.
        """
        return tuple(self._board)

    @property
    def stage(self):
        """Returns the stage of this poker game.

        :return: The stage of this poker game.
        """
        return self._stage

    @property
    def side_pots(self):
        """Returns the side pots of this poker game.

        :return: The side pots of this poker game.
        """
        return map(self._SidePot.amount.fget, self._side_pots)

    @property
    def _side_pots(self):
        players = sorted(self.players, key=PokerPlayer.put.fget)
        side_pots = []
        pot = 0
        prev = 0

        while pot < self.pot:
            cur = players[0].put
            amount = len(players) * (cur - prev)

            side_pots.append(self._SidePot(filter(PokerPlayer.is_active, players), amount))

            pot += amount
            prev = players.pop(0).put

        return side_pots

    def parse(self, *tokens):
        """Parses the tokens as actions and applies them this poker game.

        :param tokens: The tokens to parse as actions.
        :return: This game.
        """
        for token in tokens:
            if match := re.fullmatch(r'dh( (?P<index>\d+))?( (?P<cards>\w+))?', token):
                self.actor.deal_hole(
                    None if (index := match.group('index')) is None else self.players[int(index)],
                    None if (cards := match.group('cards')) is None else parse_cards(cards),
                )
            elif match := re.fullmatch(r'db( (?P<cards>\w+))?', token):
                self.actor.deal_board(None if (cards := match.group('cards')) is None else parse_cards(cards))
            elif match := re.fullmatch(r'br( (?P<amount>\d+))?', token):
                self.actor.bet_raise(None if (amount := match.group('amount')) is None else int(amount))
            elif token == 'cc':
                self.actor.check_call()
            elif token == 'f':
                self.actor.fold()
            elif match := re.fullmatch(r'dd( (?P<discarded_cards>\w*))?( (?P<drawn_cards>\w*))?', token):
                self.actor.discard_draw(
                    () if (cards := match.group('discarded_cards')) is None else parse_cards(cards),
                    None if (cards := match.group('drawn_cards')) is None else parse_cards(cards),
                )
            elif match := re.fullmatch(r's( (?P<forced_status>[0|1]))?', token):
                self.actor.showdown(
                    None if (forced_status := match.group('forced_status')) is None else bool(int(forced_status)),
                )
            else:
                raise ValueError('Invalid command')

        return self

    def _verify(self):
        filtered_bets = list(filter(bool, self.forced_bets))

        if filtered_bets != sorted(filtered_bets):
            raise GameFrameError('Forced bets must be sorted (except zero values)')
        elif len(self.starting_stacks) < 2:
            raise GameFrameError('Poker needs at least 2 players')
        elif self.ante < 0:
            raise GameFrameError('The ante must be a positive value')
        elif len(self.forced_bets) > len(self.starting_stacks):
            raise GameFrameError('Number of blinds must be less than or equal to the number of players')
        elif any(map(partial(gt, 0), (self.ante,) + self.forced_bets + self.starting_stacks)):
            raise GameFrameError('All numerical values must be positive')

    def _setup(self):
        for player in self.players:
            stack = player.starting_stack
            ante = min(self.ante, stack)
            forced_bet = max(min(player.forced_bet, player.starting_stack - ante), 0)

            self._pot += ante
            player._bet = forced_bet
            player._stack = stack - ante - forced_bet

        self.stages[0]._open()

    class _SidePot:
        def __init__(self, players, amount):
            self.__players = tuple(players)
            self.__amount = amount

        @property
        def players(self):
            return self.__players

        @property
        def amount(self):
            return self.__amount


class PokerNature(SequentialActor):
    """PokerNature is the class for poker natures."""

    def __repr__(self):
        return 'PokerNature'

    @property
    def dealable_players(self):
        """Returns an iterator of poker players that can be dealt.

        :return: The players that can be dealt.
        """
        if self.can_deal_hole():
            return self._get_hole_deal_action().dealable_players
        else:
            raise GameFrameError('The nature cannot deal hole cards')

    @property
    def hole_deal_count(self):
        """Returns the number of hole cards that can be dealt to each player.

        :return: The number of hole cards to deal.
        """
        if self.can_deal_hole():
            return self._get_hole_deal_action().deal_count
        else:
            raise GameFrameError('The nature cannot deal hole cards')

    @property
    def board_deal_count(self):
        """Returns the number of cards that can be dealt to the board.

        :return: The number of cards to deal.
        """
        if self.can_deal_board():
            return self._get_board_deal_action().deal_count
        else:
            raise GameFrameError('The nature cannot deal board cards')

    def deal_hole(self, player=None, cards=None):
        """Deals the optionally supplied hole cards to the optionally specified player.

        If the cards are not supplied, they are randomly drawn from the deck. If the player is not known, the next
        player in order who is dealable will be dealt.

        If the cards are specified, the player must be specified as well.

        :param player: The optional player to deal to.
        :param cards: The optional hole cards to be dealt.
        :return: None.
        """
        self._get_hole_deal_action(player, cards).act()

    def can_deal_hole(self, player=None, cards=None):
        """Determines if the optionally specified hole cards can be dealt to the optionally supplied player.

        If the cards are not supplied, they are assumed to be randomly drawn from the deck. If the player is not known,
        the next player in order who is dealable will be assumed to be dealt.

        If the cards are specified, the player must be specified as well.

        :param player: The optional player to deal to.
        :param cards: The optional hole cards to be dealt.
        :return: True if the hole can be dealt, else False.
        """
        return self._get_hole_deal_action(player, cards).can_act()

    def deal_board(self, cards=None):
        """Deals the optionally specified cards to the board.

        If none is given as cards, sample cards are randomly selected from the deck.

        :param cards: The optional cards to be dealt.
        :return: None.
        """
        self._get_board_deal_action(cards).act()

    def can_deal_board(self, cards=None):
        """Determines if cards can be dealt to the board.

        If none is given as cards, sample cards are assumed to be randomly selected from the deck.

        :param cards: The optional cards to be dealt.
        :return: True if the board can be dealt, else False.
        """
        return self._get_board_deal_action(cards).can_act()

    def _get_hole_deal_action(self, player=None, cards=None):
        from pokertools._actions import HoleDealingAction

        return HoleDealingAction(player, cards, self)

    def _get_board_deal_action(self, cards=None):
        from pokertools._actions import BoardDealingAction

        return BoardDealingAction(cards, self)


class PokerPlayer(SequentialActor):
    """PokerPlayer is the class for poker players.

    :param game: The game of this poker player.
    """

    def __init__(self, game):
        super().__init__(game)

        self._bet = 0
        self._stack = 0
        self._hole = []
        self._status = None

    def __repr__(self):
        if self.is_mucked():
            return f'PokerPlayer({self.bet}, {self.stack})'
        else:
            return f'PokerPlayer({self.bet}, {self.stack}, ' + ''.join(map(str, self.hole)) + ')'

    @property
    def bet(self):
        """Returns the bet of this poker player.

        :return: The bet of this poker player.
        """
        return self._bet

    @property
    def stack(self):
        """Returns the stack of this poker player.

        :return: The stack of this poker player.
        """
        return self._stack

    @property
    def hole(self):
        """Returns the hole cards of this poker player.

        :return: The hole cards of this poker player.
        """
        if self._status is None:
            return self._hole
        else:
            return tuple(map(partial(HoleCard, self._status), self._hole))

    @property
    def starting_stack(self):
        """Returns the starting stack of this poker player.

        :return: The starting stack of this poker player.
        """
        return self.game.starting_stacks[self.index]

    @property
    def forced_bet(self):
        """Returns the forced-bet of this poker player.

        :return: The forced-bet of this poker player.
        """
        if len(self.game.players) == 2:
            return self.game.forced_bets[not self.index]
        else:
            return self.game.forced_bets[self.index]

    @property
    def total(self):
        """Returns the sum of the bet and the stack of this poker player.

        :return: The sum of the bet and the stack of this poker player.
        """
        return self.bet + self.stack

    @property
    def effective_stack(self):
        """Returns the effective stack of this poker player.

        The effective stacks are maximum amount that the poker player can lose in a current poker game state.

        :return: The effective stack of this poker player.
        """
        active_players = tuple(filter(PokerPlayer.is_active, self.game.players))

        if self.is_mucked() or len(active_players) < 2:
            return 0
        else:
            return min(self.starting_stack, sorted(map(PokerPlayer.starting_stack.fget, active_players))[-2])

    @property
    def put(self):
        """Returns the amount put into the pot by this poker player.

        :return: The amount put by this poker player.
        """
        return max(self.starting_stack - self.total, 0)

    @property
    def hands(self):
        """Returns the hands of this poker player.

        The hands are arranged in the order of evaluators of the associated poker game. Usually, poker games only have
        one evaluator type, in which case this property will be a singleton iterator. However, sometimes, a poker game
        may have hi and lo evaluator. Then, this property will be an iterator of hi and lo hands.

        :return: The hands of this poker player.
        """
        return map(self._get_hand, self.game.evaluators)

    @property
    def check_call_amount(self):
        """Returns the check/call amount.

        If the player checks, 0 is returned.

        :return: The check/call amount.
        """
        if self.can_check_call():
            return self._get_check_call_action().amount
        else:
            raise GameFrameError('The player cannot check/call')

    @property
    def min_bet_raise_amount(self):
        """Returns the minimum bet/raise amount.

        The minimum bet/raise amount is set by the limit of the poker game.

        :return: The minimum bet/raise amount.
        """
        if self.can_bet_raise():
            return self._get_bet_raise_action().min_amount
        else:
            raise GameFrameError('The player cannot bet/raise')

    @property
    def max_bet_raise_amount(self):
        """Returns the maximum bet/raise amount.

        The maximum bet/raise amount is set by the limit of the poker game.

        :return: The maximum bet/raise amount.
        """
        if self.can_bet_raise():
            return self._get_bet_raise_action().max_amount
        else:
            raise GameFrameError('The player cannot bet/raise')

    @property
    def _lost(self):
        return self.starting_stack - self.stack

    def is_mucked(self):
        """Returns whether or not the player has mucked his/her hand.

        :return: True if this poker player has mucked his/her hand, else False.
        """
        return self._status is False

    def is_shown(self):
        """Returns whether or not the player has shown his/her hand.

        :return: True if this poker player has shown his/her hand, else False.
        """
        return self._status is True

    def is_active(self):
        """Returns whether or not the player is active.

        The player is active if he/she is in a hand.

        :return: True if this poker player is active, else False.
        """
        return not self.is_mucked()

    def is_showdown_necessary(self):
        """Returns whether or not showdown is necessary to win the pot.

        If any hand that beats this poker player's hand is already revealed, then the showdown would not be necessary.

        :return: True if the showdown is necessary, else False.
        """
        if self.can_showdown():
            return self._get_showdown_action().is_necessary()
        else:
            raise GameFrameError('The player cannot showdown')

    def fold(self):
        """Folds the poker player's hand.

        :return: None
        """
        self._get_fold_action().act()

    def can_fold(self):
        """Returns whether or not the player can fold his/her hand.

        :return: True if this poker player can fold, else False
        """
        return self._get_fold_action().can_act()

    def check_call(self):
        """Checks or calls the opponent's bet.

        :return: None
        """
        self._get_check_call_action().act()

    def can_check_call(self):
        """Returns whether or not the player can check/call.

        :return: True if this poker player can check/call, else False
        """
        return self._get_check_call_action().can_act()

    def bet_raise(self, amount=None):
        """Bets or raises to the optional amount.

        If no amount is specified, this poker player will min-raise.

        :param amount: The optional amount to bet/raise.
        :return: None
        """
        self._get_bet_raise_action(amount).act()

    def can_bet_raise(self, amount=None):
        """Returns whether or not the player can bet/raise to the optionally given bet amount.

        If no amount is specified, this poker player is assumed to min-raise.

        :param amount: The optional amount to bet/raise.
        :return: True if this poker player can bet/raise, else False
        """
        return self._get_bet_raise_action(amount).can_act()

    def discard_draw(self, discarded_cards=(), drawn_cards=None):
        """Discards this poker player's optionally specified hole cards and draws the corresponding optionally given
        cards.

        If discarded cards are not specified, the poker player performs a stand pat. If the drawn cards are not
        specified, random cards will be drawn.

        If drawn cards is specified, so must the discarded cards.

        :param discarded_cards: The optional cards to discard. Defaults to empty tuple (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: None
        """
        self._get_discard_draw_action(discarded_cards, drawn_cards).act()

    def can_discard_draw(self, discarded_cards=(), drawn_cards=None):
        """Returns whether or not this poker player can discard and draw.

        If discarded cards are not specified, the poker player is assumed to perform a stand pat. If the drawn cards are
        not specified, random cards are assumed be drawn.

        If drawn cards is specified, so must the discarded cards.

        :param discarded_cards: The cards to discard. Defaults to empty tuple (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: True if this poker player can discard and draw, else False.
        """
        return self._get_discard_draw_action(discarded_cards, drawn_cards).can_act()

    def showdown(self, forced):
        """Showdowns this poker player's hand if necessary to win the pot or forced.

        if forced is not supplied, the showdown is forced if necessary to win the pot. This is the case when there is no
        face-up hand on the board that beats your hand.

        :param forced: True to force showdown, False to force muck. Defaults to None.
        :return: None
        """
        self._get_showdown_action(forced).act()

    def can_showdown(self, forced=None):
        """Returns whether or not this poker player can showdown.

        if forced is not supplied, the showdown is assumed to be forced if necessary to win the pot. This is the case
        when there is no face-up hand on the board that beats your hand.

        :param forced: True to force showdown, False to force muck. Defaults to None.
        :return: True if this poker player can showdown, else False.
        """
        return self._get_showdown_action(forced).can_act()

    def _is_relevant(self):
        return self.is_active() and self._lost < self.effective_stack

    def _get_hand(self, evaluator):
        return evaluator.evaluate(self.hole, self.game.board)

    def _get_fold_action(self):
        from pokertools._actions import FoldAction

        return FoldAction(self)

    def _get_check_call_action(self):
        from pokertools._actions import CheckCallAction

        return CheckCallAction(self)

    def _get_bet_raise_action(self, amount=None):
        from pokertools._actions import BetRaiseAction

        return BetRaiseAction(amount, self)

    def _get_discard_draw_action(self, discarded_cards=(), drawn_cards=None):
        from pokertools._actions import DiscardDrawAction

        return DiscardDrawAction(discarded_cards, drawn_cards, self)

    def _get_showdown_action(self, forced=None):
        from pokertools._actions import ShowdownAction

        return ShowdownAction(forced, self)
