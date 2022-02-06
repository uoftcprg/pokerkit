from collections.abc import Sized
from functools import partial
from itertools import starmap
from numbers import Integral
from operator import gt

from auxiliary import SequenceView, maxima, reverse_args
from krieg.sequential import SequentialActor, SequentialGame

from pokerface.cards import HoleCard, parse_cards
from pokerface.decks import Deck


class PokerGame(SequentialGame):
    """The class for poker games.

    When a PokerGame instance is created, its deck, evaluator, limit,
    and streets are also created through the invocations of
    corresponding create methods, which should be overridden by the
    subclasses. Also, every subclass should override the ante, blinds,
    and starting stacks properties accordingly.

    The number of players, denoted by the length of the starting stacks
    property, must be greater than or equal to 2.

    :param limit_type: The limit type of this poker game.
    :param variant_type: The variant type of this poker game.
    :param stakes: The stakes of this poker game.
    :param starting_stacks: The starting stacks of this poker game.
    """

    class _SidePot:
        def __init__(self, players, amount):
            self.players = tuple(players)
            self.amount = amount

    @classmethod
    def _allocate(cls, amount, count):
        if isinstance(amount, Integral):
            amounts = [amount // count] * count
            amounts[0] += amount % count
        else:
            amounts = [amount / count] * count
            amounts[0] += amount - sum(amounts)

        return amounts

    def __init__(self, limit_type, variant_type, stakes, starting_stacks):
        if not isinstance(starting_stacks, Sized):
            starting_stacks = tuple(starting_stacks)

        nature = PokerNature(self)
        players = (PokerPlayer(self) for _ in range(len(starting_stacks)))

        super().__init__(nature, players, nature)

        self._limit = limit_type(self)
        self._variant = variant_type(self)
        self._stakes = stakes
        self._starting_stacks = tuple(starting_stacks)

        self._stages = self.variant.create_stages()
        self._evaluators = self.variant.create_evaluators()

        self._deck = self.variant.create_deck()
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
        """Return the limit of this poker game.

        :return: The limit of this poker game.
        """
        return self._limit

    @property
    def variant(self):
        """Return the variant of this poker game.

        :return: The variant of this poker game.
        """
        return self._variant

    @property
    def stakes(self):
        """Return the stakes of this poker game.

        :return: The stakes of this poker game.
        """
        return self._stakes

    @property
    def starting_stacks(self):
        """Return the starting stacks of this poker game.

        :return: The starting stacks of this poker game.
        """
        return self._starting_stacks

    @property
    def stages(self):
        """Return the stages of this poker game.

        :return: The stages of this poker game.
        """
        return self._stages

    @property
    def evaluators(self):
        """Return the evaluators of this poker game.

        :return: The evaluators of this poker game.
        """
        return self._evaluators

    @property
    def deck(self):
        """Return the deck of this poker game.

        :return: The deck of this poker game.
        """
        return SequenceView(self._deck)

    @property
    def muck(self):
        """Return the muck of this poker game.

        :return: The muck of this poker game.
        """
        return SequenceView(self._muck)

    @property
    def pot(self):
        """Return the pot of this poker game.

        :return: The pot of this poker game.
        """
        return self._pot

    @property
    def board(self):
        """Return the board of this poker game.

        The board contains the public cards in a poker game. They can be
        combined with individual player's hole cards to create a hand.

        :return: The board of this poker game.
        """
        return SequenceView(self._board)

    @property
    def stage(self):
        """Return the stage of this poker game.

        :return: The stage of this poker game.
        """
        return self._stage

    @property
    def side_pots(self):
        """Return the side pots of this poker game.

        :return: The side pots of this poker game.
        """
        for side_pot in self._side_pots:
            yield side_pot.amount

    @property
    def _side_pots(self):
        players = sorted(self.players, key=PokerPlayer._put.fget, reverse=True)
        side_pots = []
        pot = 0
        prev = 0

        while pot < self.pot:
            cur = players[-1]._put
            amount = len(players) * (cur - prev)

            side_pots.append(self._SidePot(
                filter(PokerPlayer.is_active, players), amount,
            ))

            pot += amount
            prev = players.pop()._put

        return side_pots

    @property
    def _hole_card_statuses(self):
        statuses = []

        for stage in self.stages:
            if stage.is_hole_dealing_stage():
                statuses.extend((stage.status,) * stage.deal_count)

        return statuses

    def act(self, *commands):
        """Parse the commands as actions and applies them to this poker
        game.

        :param commands: The commands to parse as actions.
        :return: This game.
        """
        for command in commands:
            self._parse(command).act()

        return self

    def can_act(self, command):
        """Parse the command as an action and verify if it is valid.

        :param command: The command to parse as an action.
        :return: True if the parsed command is valid, else False.
        """
        return self._parse(command).can_act()

    def _is_all_in(self):
        return not self._is_folded() and not any(map(
            PokerPlayer._is_relevant, self.players,
        ))

    def _is_folded(self):
        return sum(map(PokerPlayer.is_active, self.players)) == 1

    def _verify(self):
        if len(self.starting_stacks) < 2:
            raise ValueError('less than 2 players')
        elif len(self.stakes.blinds) > len(self.starting_stacks):
            raise ValueError('more blinds than players')
        elif any(map(partial(gt, 0), self.starting_stacks)):
            raise ValueError('negative starting stack values')

    def _setup(self):
        for player in self.players:
            ante = min(self.stakes.ante, player.starting_stack)
            blind = max(min(player.blind, player.starting_stack - ante), 0)
            stack = player.starting_stack

            self._pot += ante
            player._bet = blind
            player._stack = stack - ante - blind

        if self._is_all_in():
            for player in self.players:
                player._status = True

        self._update()

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
            for amount, evaluator in zip(self._allocate(
                    side_pot.amount, len(self.evaluators),
            ), self.evaluators):
                if len(side_pot.players) == 1:
                    players = side_pot.players
                else:
                    players = tuple(maxima(side_pot.players, key=partial(
                        reverse_args(PokerPlayer._get_hand), evaluator,
                    )))

                for player, share in zip(players, self._allocate(
                        amount, len(players),
                )):
                    player._stack += share

        self._pot = 0

    def _collect(self):
        effective_bet = sorted(map(PokerPlayer.bet.fget, self.players))[-2]

        for player in self.players:
            bet = min(effective_bet, player.bet)
            self._pot += bet
            player._stack += player.bet - bet
            player._bet = 0

    def _parse(self, *commands):
        for command in commands:
            if command == 'dh':
                return self.actor._get_hole_deal_action()
            elif command.startswith('dh '):
                _, cards = command.split()
                return self.actor._get_hole_deal_action(parse_cards(cards))
            elif command == 'db':
                return self.actor._get_board_deal_action()
            elif command.startswith('db '):
                _, cards = command.split()
                return self.actor._get_board_deal_action(parse_cards(cards))
            elif command == 'f':
                return self.actor._get_fold_action()
            elif command == 'cc':
                return self.actor._get_check_call_action()
            elif command == 'br':
                return self.actor._get_bet_raise_action()
            elif command.startswith('br '):
                _, amount = command.split()
                return self.actor._get_bet_raise_action(int(amount))
            elif command == 'dd':
                return self.actor._get_discard_draw_action()
            elif command.startswith('dd ') and len(command.split()) == 2:
                _, discarded_cards = command.split()
                return self.actor._get_discard_draw_action(
                    parse_cards(discarded_cards),
                )
            elif command.startswith('dd ') and len(command.split()) == 3:
                _, discarded_cards, drawn_cards = command.split()
                return self.actor._get_discard_draw_action(
                    parse_cards(discarded_cards), parse_cards(drawn_cards),
                )
            elif command == 's':
                return self.actor._get_showdown_action()
            elif command == 's 0':
                return self.actor._get_showdown_action(False)
            elif command == 's 1':
                return self.actor._get_showdown_action(True)

            raise ValueError(f'invalid command \'{command}\'')


class PokerNature(SequentialActor):
    """The class for poker natures."""

    def __repr__(self):
        return 'PokerNature'

    @property
    def deal_hole_player(self):
        """Return the next player that can be dealt hole cards.

        :return: The player that can be dealt hole cards.
        """
        if not self.can_deal_hole():
            raise ValueError('cannot deal hole cards')

        return self._get_hole_deal_action().deal_player

    @property
    def deal_hole_count(self):
        """Return the number of hole cards that can be dealt.

        :return: The number of cards to deal to the player hole.
        """
        if not self.can_deal_hole():
            raise ValueError('cannot deal hole cards')

        return self._get_hole_deal_action().deal_count

    @property
    def deal_board_count(self):
        """Return the number of board cards that can be dealt.

        :return: The number of cards to deal to the board.
        """
        if not self.can_deal_board():
            raise ValueError('cannot deal board cards')

        return self._get_board_deal_action().deal_count

    def deal_hole(self, cards=None):
        """Deal the optionally supplied hole cards to the next player.

        If the cards are not supplied, they are randomly drawn from the
        deck.

        :param cards: The optional hole cards to be dealt.
        :return: ``None``.
        """
        self._get_hole_deal_action(cards).act()

    def can_deal_hole(self, cards=None):
        """Determine if the optionally specified hole cards can be dealt
        to the next player.

        If the cards are not supplied, they are randomly drawn from the
        deck.

        :param cards: The optional hole cards to be dealt.
        :return: ``True`` if the hole can be dealt, else ``False``.
        """
        return self._get_hole_deal_action(cards).can_act()

    def deal_board(self, cards=None):
        """Deal the optionally specified cards to the board.

        If ``None`` is given as cards, sample cards are randomly
        selected from the deck.

        :param cards: The optional cards to be dealt.
        :return: ``None``.
        """
        self._get_board_deal_action(cards).act()

    def can_deal_board(self, cards=None):
        """Determine if the optionally specified cards can be dealt to
        the board.

        If ``None`` is given as cards, sample cards are assumed to be
        randomly selected from the deck.

        :param cards: The optional cards to be dealt.
        :return: ``True`` if the board can be dealt, else ``False``.
        """
        return self._get_board_deal_action(cards).can_act()

    def _get_hole_deal_action(self, cards=None):
        from pokerface._actions import HoleDealingAction

        return HoleDealingAction(self, cards)

    def _get_board_deal_action(self, cards=None):
        from pokerface._actions import BoardDealingAction

        return BoardDealingAction(self, cards)


class PokerPlayer(SequentialActor):
    """The class for poker players.

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

        return f'PokerPlayer({self.bet}, {self.stack}, ' \
               + ''.join(map(str, self.hole)) + ')'

    @property
    def blind(self):
        """Return the blind of this poker player.

        :return: The blind of this poker player.
        """
        index = not self.index if len(self.game.players) == 2 else self.index
        values = []

        for key, value in self.game.stakes.blinds.items():
            if key % len(self.game.players) == index:
                values.append(value)

        if not values:
            return 0
        elif len(values) == 1:
            return values[0]

        raise ValueError('multiple possible blind values')

    @property
    def total(self):
        """Return the sum of the bet and the stack of this poker
        player.

        :return: The sum of the bet and the stack of this poker player.
        """
        return self.bet + self.stack

    @property
    def effective_stack(self):
        """Return the effective stack of this poker player.

        The effective stacks are maximum amount that the poker player
        can lose in a current poker game state.

        :return: The effective stack of this poker player.
        """
        active_players = tuple(
            filter(PokerPlayer.is_active, self.game.players)
        )

        if self.is_mucked() or len(active_players) < 2:
            return 0

        return min(
            self.starting_stack,
            sorted(map(PokerPlayer.starting_stack.fget, active_players))[-2],
        )

    @property
    def payoff(self):
        """Return the payoff of this poker player.

        Payoff is the amount this poker player has made/lost. If this
        poker player made money, this quantity is positive, and vice
        versa.

        :return: The payoff of this poker player.
        """
        return self.stack - self.starting_stack

    @property
    def hands(self):
        """Return the hands of this poker player.

        The hands are arranged in the order of evaluators of the
        associated poker game. Usually, poker games only have one
        evaluator type, in which case this property will be a singleton
        iterator. However, sometimes, a poker game may have hi and lo
        evaluator. Then, this property will be an iterator of hi and lo
        hands.

        :return: The hands of this poker player.
        """
        return map(self._get_hand, self.game.evaluators)

    @property
    def check_call_amount(self):
        """Return the check/call amount.

        If the player checks, 0 is returned.

        :return: The check/call amount.
        """
        if not self.can_check_call():
            raise ValueError('cannot check/call')

        return self._get_check_call_action().amount

    @property
    def bet_raise_min_amount(self):
        """Return the minimum bet/raise amount.

        The minimum bet/raise amount is set by the limit of the poker
        game.

        :return: The minimum bet/raise amount.
        """
        if not self.can_bet_raise():
            raise ValueError('cannot bet/raise')

        return self._get_bet_raise_action().min_amount

    @property
    def bet_raise_max_amount(self):
        """Return the maximum bet/raise amount.

        The maximum bet/raise amount is set by the limit of the poker
        game.

        :return: The maximum bet/raise amount.
        """
        if not self.can_bet_raise():
            raise ValueError('cannot bet/raise')

        return self._get_bet_raise_action().max_amount

    @property
    def bet_raise_pot_amount(self):
        """Return the pot bet/raise amount.

        The pot bet/raise amount is calculated using the outstanding
        bets and the pot amount. It can be obtained with the following
        equation:

        ``3 * (last wager) + (trail) + (starting pot) + (maximum bet)``

        Source: https://en.wikipedia.org/wiki/Betting_in_poker#Pot_limit

        :return: The pot bet/raise amount.
        """
        if not self.can_bet_raise():
            raise ValueError('cannot bet/raise')

        return self._get_bet_raise_action().pot_amount

    @property
    def starting_stack(self):
        """Return the starting stack of this poker player.

        :return: The starting stack of this poker player.
        """
        return self.game.starting_stacks[self.index]

    @property
    def bet(self):
        """Return the bet of this poker player.

        :return: The bet of this poker player.
        """
        return self._bet

    @property
    def stack(self):
        """Return the stack of this poker player.

        :return: The stack of this poker player.
        """
        return self._stack

    @property
    def hole(self):
        """Return the hole cards of this poker player.

        :return: The hole cards of this poker player.
        """
        if self.is_mucked():
            return ()
        elif self.is_shown():
            return tuple(map(HoleCard.show, self._hole))

        return tuple(starmap(HoleCard, zip(
            self.game._hole_card_statuses, self._hole,
        )))

    @property
    def seen(self):
        """Return the cards that this poker player have had before in
        his/her hole.

        :return: The seen cards of this poker player.
        """
        return SequenceView(self._seen)

    @property
    def _put(self):
        return self.starting_stack - self.total

    @property
    def _lost(self):
        return self.starting_stack - self.stack

    def is_active(self):
        """Return whether or not the player is active.

        The player is active if he/she is in a hand.

        :return: ``True`` if this poker player is active, else
                 ``False``.
        """
        return not self.is_mucked()

    def is_mucked(self):
        """Return whether or not the player has mucked his/her hand.

        :return: ``True`` if this poker player has mucked his/her hand,
                 else ``False``.
        """
        return self._status is False

    def is_shown(self):
        """Return whether or not the player has shown his/her hand.

        :return: ``True`` if this poker player has shown his/her hand,
                 else ``False``.
        """
        return self._status is True

    def is_showdown_necessary(self):
        """Return whether or not showdown is necessary to win the pot.

        If any hand that beats this poker player's hand is already
        revealed, then the showdown would not be necessary.

        :return: ``True`` if the showdown is necessary, else ``False``.
        """
        if not self.can_showdown():
            raise ValueError('cannot showdown')

        return self._get_showdown_action().is_necessary()

    def fold(self):
        """Fold the poker player's hand.

        :return: ``None``.
        """
        self._get_fold_action().act()

    def can_fold(self):
        """Return whether or not the player can fold his/her hand.

        :return: ``True`` if this poker player can fold, else ``False``.
        """
        return self._get_fold_action().can_act()

    def check_call(self):
        """Check or call the opponent's bet.

        :return: ``None``.
        """
        self._get_check_call_action().act()

    def can_check_call(self):
        """Return whether or not the player can check/call.

        :return: ``True`` if this poker player can check/call, else
                 ``False``.
        """
        return self._get_check_call_action().can_act()

    def bet_raise(self, amount=None):
        """Bet or raise to the optional amount.

        If no amount is specified, this poker player will min-raise.

        :param amount: The optional amount to bet/raise.
        :return: ``None``.
        """
        self._get_bet_raise_action(amount).act()

    def can_bet_raise(self, amount=None):
        """Return whether or not the player can bet/raise to the
        optionally given bet amount.

        If no amount is specified, this poker player is assumed to
        min-raise.

        :param amount: The optional amount to bet/raise.
        :return: ``True`` if this poker player can bet/raise, else
                 ``False``.
        """
        return self._get_bet_raise_action(amount).can_act()

    def discard_draw(self, discarded_cards=(), drawn_cards=None):
        """Discard this poker player's optionally specified hole cards
        and draw the corresponding optionally given cards.

        If discarded cards are not specified, the poker player performs
        a stand pat. If the drawn cards are not specified, random cards
        will be drawn.

        If drawn cards is specified, so must the discarded cards.

        :param discarded_cards: The optional cards to discard. Defaults
                                to an empty ``tuple`` (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: ``None``.
        """
        self._get_discard_draw_action(discarded_cards, drawn_cards).act()

    def can_discard_draw(self, discarded_cards=(), drawn_cards=None):
        """Return whether or not this poker player can discard and
        draw.

        If discarded cards are not specified, the poker player is
        assumed to perform a stand pat. If the drawn cards are not
        specified, random cards are assumed be drawn.

        If drawn cards is specified, so must the discarded cards.

        :param discarded_cards: The cards to discard. Defaults to empty
                                tuple (stand pat).
        :param drawn_cards: The optional cards to draw.
        :return: ``True`` if this poker player can discard and draw,
                 else ``False``.
        """
        return self._get_discard_draw_action(
            discarded_cards, drawn_cards,
        ).can_act()

    def showdown(self, forced=None):
        """Showdown this poker player's hand if necessary to win the
        pot or forced.

        if forced is not supplied, the showdown is forced if necessary
        to win the pot. This is the case when there is no face-up hand
        on the board that beats your hand.

        :param forced: ``True`` to force showdown, ``False`` to force
                       muck. Defaults to ``None``.
        :return: ``None``.
        """
        self._get_showdown_action(forced).act()

    def can_showdown(self, forced=None):
        """Return whether or not this poker player can showdown.

        if forced is not supplied, the showdown is assumed to be forced
        if necessary to win the pot. This is the case when there is no
        face-up hand on the board that beats your hand.

        :param forced: ``True`` to force showdown, ``False`` to force
                       muck. Defaults to ``None``.
        :return: ``True`` if this poker player can showdown, else
                 ``False``.
        """
        return self._get_showdown_action(forced).can_act()

    def _is_relevant(self):
        return self.is_active() and self._lost < self.effective_stack

    def _get_hand(self, evaluator):
        return evaluator.evaluate_hand(self.hole, self.game.board)

    def _get_fold_action(self):
        from pokerface._actions import FoldAction

        return FoldAction(self)

    def _get_check_call_action(self):
        from pokerface._actions import CheckCallAction

        return CheckCallAction(self)

    def _get_bet_raise_action(self, amount=None):
        from pokerface._actions import BetRaiseAction

        return BetRaiseAction(self, amount)

    def _get_discard_draw_action(self, discarded_cards=(), drawn_cards=None):
        from pokerface._actions import DiscardDrawAction

        return DiscardDrawAction(self, discarded_cards, drawn_cards)

    def _get_showdown_action(self, forced=None):
        from pokerface._actions import ShowdownAction

        return ShowdownAction(self, forced)
