from functools import partial
from itertools import starmap
from numbers import Integral
from operator import gt

from auxiliary import maxima, reverse_args
from gameframe.sequential import SequentialActor, SequentialGame

from pokertools.cards import HoleCard, parse_cards
from pokertools.decks import Deck


class PokerGame(SequentialGame):
    """PokerGame is the class for poker games.

    When a PokerGame instance is created, its deck, evaluator, limit, and streets are also created through the
    invocations of corresponding create methods, which should be overridden by the subclasses. Also, every subclass
    should override the ante, blinds, and starting_stacks properties accordingly.

    The number of players, denoted by the length of the starting_stacks property, must be greater than or equal to 2.

    :param limit_type: The limit type of this poker game.
    :param definition_type: The definition type this poker game.
    :param stakes: The stakes of this poker game.
    :param starting_stacks: The starting stacks of this poker game.
    """

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

    @classmethod
    def _allocate(cls, amount, count):
        if isinstance(amount, Integral):
            amounts = [amount // count] * count
            amounts[0] += amount % count
        else:
            amounts = [amount / count] * count
            amounts[0] += amount - sum(amounts)

        return amounts

    def __init__(self, limit_type, definition_type, stakes, starting_stacks):
        super().__init__(None, PokerNature(self), (PokerPlayer(self) for _ in range(len(starting_stacks))))

        self.__limit = limit_type(self)
        self.__definition = definition_type(self)
        self.__stakes = stakes
        self.__starting_stacks = tuple(starting_stacks)
        self.__stages = self.definition.create_stages()
        self.__evaluators = self.definition.create_evaluators()

        self._deck = self.definition.create_deck()
        self._muck = Deck()
        self._pot = 0
        self._board = []

        self._stage = None
        self._queue = []
        self._aggressor = None
        self._bet_raise_count = None
        self._max_delta = None

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
    def stakes(self):
        """Returns the stakes of this poker game.

        :return: The stakes of this poker game.
        """
        return self.__stakes

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
    def ante(self):
        """Returns the ante of this poker game.

        :return: The ante of this poker game.
        """
        return self.stakes.ante

    @property
    def blinds(self):
        """Returns the blinds of this poker game.

        This tuple includes straddles and forced bets.

        :return: The blinds of this poker game.
        """
        return self.stakes.blinds

    @property
    def small_bet(self):
        """Returns the small bet of this poker game.

        :return: The small bet of this poker game.
        """
        return self.stakes.small_bet

    @property
    def big_bet(self):
        """Returns the big bet of this poker game.

        :return: The big bet of this poker game.
        """
        return self.stakes.big_bet

    @property
    def muck(self):
        """Returns the muck of this poker game.

        :return: The muck of this poker game.
        """
        return tuple(self._muck)

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
        players = sorted(self.players, key=PokerPlayer._put.fget, reverse=True)
        side_pots = []
        pot = 0
        prev = 0

        while pot < self.pot:
            cur = players[-1]._put
            amount = len(players) * (cur - prev)

            side_pots.append(self._SidePot(filter(PokerPlayer.is_active, players), amount))

            pot += amount
            prev = players.pop()._put

        return side_pots

    @property
    def _hole_card_statuses(self):
        from pokertools.stages import HoleDealingStage

        statuses = []

        for stage in self.stages:
            if isinstance(stage, HoleDealingStage):
                statuses.extend((stage.status,) * stage.deal_count)

        return statuses

    def parse(self, *tokens):
        """Parses the tokens as actions and applies them this poker game.

        :param tokens: The tokens to parse as actions.
        :return: This game.
        """
        for token in tokens:
            if token == 'dh':
                self.actor.deal_hole()
            elif token.startswith('dh '):
                self.actor.deal_hole(parse_cards(token[3:]))
            elif token == 'db':
                self.actor.deal_board()
            elif token.startswith('db '):
                self.actor.deal_board(parse_cards(token[3:]))
            elif token == 'f':
                self.actor.fold()
            elif token == 'cc':
                self.actor.check_call()
            elif token == 'br':
                self.actor.bet_raise()
            elif token.startswith('br '):
                self.actor.bet_raise(int(token[3:]))
            elif token == 'dd':
                self.actor.discard_draw()
            elif token.startswith('dd ') and len(token.split()) == 2:
                _, discarded_cards = token.split()
                self.actor.discard_draw(parse_cards(discarded_cards))
            elif token.startswith('dd ') and len(token.split()) == 3:
                _, discarded_cards, drawn_cards = token.split()
                self.actor.discard_draw(parse_cards(discarded_cards), parse_cards(drawn_cards))
            elif token == 's':
                self.actor.showdown()
            elif token == 's 0':
                self.actor.showdown(False)
            elif token == 's 1':
                self.actor.showdown(True)
            else:
                raise ValueError(f'Invalid command \'{token}\'')

        return self

    def _is_all_in(self):
        return not self._is_folded() and not any(map(PokerPlayer._is_relevant, self.players))

    def _is_folded(self):
        return sum(map(PokerPlayer.is_active, self.players)) == 1

    def _verify(self):
        if len(self.starting_stacks) < 2:
            raise ValueError('Poker needs at least 2 players')
        elif len(self.blinds) > len(self.starting_stacks):
            raise ValueError('Number of blinds must be less than or equal to the number of players')
        elif any(map(partial(gt, 0), self.starting_stacks)):
            raise ValueError('All starting stack values must be positive')

    def _setup(self):
        for player in self.players:
            ante = min(self.ante, player.starting_stack)
            blind = max(min(player.blind, player.starting_stack - ante), 0)
            stack = player.starting_stack

            self._pot += ante
            player._bet = blind
            player._stack = stack - ante - blind

        if self._is_all_in():
            for player in self.players:
                player._status = True

        self._update()

    def _collect(self):
        effective_bet = sorted(map(PokerPlayer.bet.fget, self.players))[-2]

        for player in self.players:
            bet = min(effective_bet, player.bet)
            self._pot += bet
            player._stack += player.bet - bet
            player._bet = 0

    def _update(self):
        if self.stage is None or self.stage._is_done():
            if self.stage is None:
                index = 0
            else:
                index = self.stages.index(self.stage) + 1
                self.stage._close()

            try:
                while self.stages[index]._is_done():
                    index += 1

                self.stages[index]._open()
            except IndexError:
                self._distribute()
                self._actor = None
        else:
            self._actor = self._queue.pop(0) if self._queue else self.nature

    def _distribute(self):
        self._collect()

        for side_pot in self._side_pots:
            for amount, evaluator in zip(self._allocate(side_pot.amount, len(self.evaluators)), self.evaluators):
                if len(side_pot.players) == 1:
                    players = side_pot.players
                else:
                    players = tuple(
                        maxima(side_pot.players, key=partial(reverse_args(PokerPlayer._get_hand), evaluator))
                    )

                for player, share in zip(players, self._allocate(amount, len(players))):
                    player._stack += share

        self._pot = 0


class PokerNature(SequentialActor):
    """PokerNature is the class for poker natures."""

    def __repr__(self):
        return 'PokerNature'

    @property
    def deal_hole_player(self):
        """Returns the next player that can be dealt hole cards.

        :return: The player that can be dealt hole cards.
        """
        if self.can_deal_hole():
            return self._get_hole_deal_action().deal_player
        else:
            raise ValueError('The nature cannot deal hole cards')

    @property
    def deal_hole_count(self):
        """Returns the number of hole cards that can be dealt.

        :return: The number of cards to deal to the player hole.
        """
        if self.can_deal_hole():
            return self._get_hole_deal_action().deal_count
        else:
            raise ValueError('The nature cannot deal hole cards')

    @property
    def deal_board_count(self):
        """Returns the number of board cards that can be dealt.

        :return: The number of cards to deal to the board.
        """
        if self.can_deal_board():
            return self._get_board_deal_action().deal_count
        else:
            raise ValueError('The nature cannot deal board cards')

    def deal_hole(self, cards=None):
        """Deals the optionally supplied hole cards to the next player to be dealt hole cards.

        If the cards are not supplied, they are randomly drawn from the deck.

        :param cards: The optional hole cards to be dealt.
        :return: None.
        """
        self._get_hole_deal_action(cards).act()

    def can_deal_hole(self, cards=None):
        """Determines if the optionally specified hole cards can be dealt to the next player to be dealt hole cards.

        If the cards are not supplied, they are randomly drawn from the deck.

        :param cards: The optional hole cards to be dealt.
        :return: True if the hole can be dealt, else False.
        """
        return self._get_hole_deal_action(cards).can_act()

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

    def _get_hole_deal_action(self, cards=None):
        from pokertools._actions import HoleDealingAction

        return HoleDealingAction(cards, self)

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
        self._seen = []
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
        if self.is_mucked():
            return ()
        elif self.is_shown():
            return tuple(map(partial(HoleCard, True), self._hole))
        else:
            return tuple(starmap(HoleCard, zip(self.game._hole_card_statuses, self._hole)))

    @property
    def seen(self):
        """Returns the cards that this poker player have had before in his/her hole.

        :return: The seen cards of this poker player.
        """
        return tuple(self._seen)

    @property
    def starting_stack(self):
        """Returns the starting stack of this poker player.

        :return: The starting stack of this poker player.
        """
        return self.game.starting_stacks[self.index]

    @property
    def blind(self):
        """Returns the blind of this poker player.

        :return: The blind of this poker player.
        """
        index = not self.index if len(self.game.players) == 2 else self.index

        return self.game.blinds[index] if index < len(self.game.blinds) else 0

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
    def payoff(self):
        """Returns the payoff of this poker player.

        Payoff is the amount this poker player has made/lost. If this poker player made money, this quantity is
        positive, and vice versa.

        :return: The payoff of this poker player.
        """
        return self.stack - self.starting_stack

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
            raise ValueError('The player cannot check/call')

    @property
    def bet_raise_min_amount(self):
        """Returns the minimum bet/raise amount.

        The minimum bet/raise amount is set by the limit of the poker game.

        :return: The minimum bet/raise amount.
        """
        if self.can_bet_raise():
            return self._get_bet_raise_action().min_amount
        else:
            raise ValueError('The player cannot bet/raise')

    @property
    def bet_raise_max_amount(self):
        """Returns the maximum bet/raise amount.

        The maximum bet/raise amount is set by the limit of the poker game.

        :return: The maximum bet/raise amount.
        """
        if self.can_bet_raise():
            return self._get_bet_raise_action().max_amount
        else:
            raise ValueError('The player cannot bet/raise')

    @property
    def bet_raise_pot_amount(self):
        """Returns the pot bet/raise amount.

        The pot bet/raise amount is calculated using the outstanding bets and the pot amount. It can be obtained with
        the following equation: 3 * (last wager) + (trail) + (starting pot) + (maximum bet)

        Source: https://en.wikipedia.org/wiki/Betting_in_poker#Pot_limit

        :return: The pot bet/raise amount.
        """
        if self.can_bet_raise():
            return self._get_bet_raise_action().pot_amount
        else:
            raise ValueError('The player cannot bet/raise')

    @property
    def _put(self):
        return self.starting_stack - self.total

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
            raise ValueError('The player cannot showdown')

    def fold(self):
        """Folds the poker player's hand.

        :return: None.
        """
        self._get_fold_action().act()

    def can_fold(self):
        """Returns whether or not the player can fold his/her hand.

        :return: True if this poker player can fold, else False.
        """
        return self._get_fold_action().can_act()

    def check_call(self):
        """Checks or calls the opponent's bet.

        :return: None.
        """
        self._get_check_call_action().act()

    def can_check_call(self):
        """Returns whether or not the player can check/call.

        :return: True if this poker player can check/call, else False.
        """
        return self._get_check_call_action().can_act()

    def bet_raise(self, amount=None):
        """Bets or raises to the optional amount.

        If no amount is specified, this poker player will min-raise.

        :param amount: The optional amount to bet/raise.
        :return: None.
        """
        self._get_bet_raise_action(amount).act()

    def can_bet_raise(self, amount=None):
        """Returns whether or not the player can bet/raise to the optionally given bet amount.

        If no amount is specified, this poker player is assumed to min-raise.

        :param amount: The optional amount to bet/raise.
        :return: True if this poker player can bet/raise, else False.
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
        :return: None.
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

    def showdown(self, forced=None):
        """Showdowns this poker player's hand if necessary to win the pot or forced.

        if forced is not supplied, the showdown is forced if necessary to win the pot. This is the case when there is no
        face-up hand on the board that beats your hand.

        :param forced: True to force showdown, False to force muck. Defaults to None.
        :return: None.
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
