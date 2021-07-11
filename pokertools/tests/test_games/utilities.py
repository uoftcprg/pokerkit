from abc import ABC, abstractmethod
from itertools import zip_longest
from random import choice, randint, sample

from gameframe.tests import GameFrameTestCaseMixin

from pokertools import PokerNature, PokerPlayer, Stakes


class PokerTestCaseMixin(GameFrameTestCaseMixin, ABC):
    GAME_TYPE = None

    @property
    def game_name(self):
        game = self.create_game()

        return type(game.limit).__name__ + type(game.definition).__name__.replace('Definition', '')

    def assert_terminal_poker_game(self, game, statuses, stacks):
        assert game.is_terminal(), 'Game is not terminal'

        for player, status, stack in zip_longest(game.players, statuses, stacks):
            assert player._status == status, f'Status of player {player.index}: {player._status} is not {status}'
            assert player.stack == stack, f'Stack of player {player.index}: {player.stack} is not {stack}'

    def create_game(self):
        return self.GAME_TYPE(Stakes(1, (1, 2)), tuple(randint(0, 50) for _ in range(randint(2, 6))))

    def act(self, game):
        actions = []

        if isinstance(game.actor, PokerNature):
            if game.actor.can_deal_hole():
                cards = ''.join(map(repr, sample(game.deck, game.actor.deal_count)))
                actions.append(f'dh {cards}')
            if game.actor.can_deal_board():
                cards = ''.join(map(repr, sample(game.deck, game.actor.deal_count)))
                actions.append(f'db {cards}')
        elif isinstance(game.actor, PokerPlayer):
            if game.actor.can_fold():
                actions.append('f')
            if game.actor.can_check_call():
                actions.append('cc')
            if game.actor.can_bet_raise():
                actions.extend((f'br {game.actor.min_bet_raise_amount}', f'br {game.actor.max_bet_raise_amount}'))
            if game.actor.can_discard_draw():
                cards = ''.join(map(repr, sample(game.actor.hole, randint(0, len(game.actor.hole)))))
                actions.append(f'dd {cards}')
            if game.actor.can_showdown():
                actions.append('s')

        game.parse(choice(actions))

    def verify(self, game):
        if game.nature.can_deal_hole():
            assert game.nature.can_deal_hole(sample(game.deck, game.nature.deal_count))
            assert not game.nature.can_deal_hole(sample(game.deck, game.nature.deal_count + 1))

        if game.nature.can_deal_board():
            assert game.nature.can_deal_board(sample(game.deck, game.nature.deal_count))
            assert not game.nature.can_deal_board(sample(game.deck, game.nature.deal_count + 1))

        for player in game.players:
            if player.can_fold():
                assert player.bet < max(map(PokerPlayer.bet.fget, game.players))

            if player.can_bet_raise():
                assert player.can_bet_raise(player.min_bet_raise_amount)
                assert player.can_bet_raise(player.max_bet_raise_amount)
                assert not player.can_bet_raise(player.min_bet_raise_amount - 1)
                assert not player.can_bet_raise(player.max_bet_raise_amount + 1)

            if player.can_discard_draw():
                assert player.can_discard_draw(player.hole)
                assert not game.deck or not player.can_discard_draw(game.deck)
                assert player.can_discard_draw(player.hole, sample(game.deck, len(player.hole)))
                assert not player.hole or not player.can_discard_draw(player.hole, player.hole)
            else:
                assert not player.can_discard_draw(player.hole)
                assert not player.can_discard_draw(player.hole, sample(game.deck, len(player.hole)))

            if player.can_showdown():
                assert player.can_showdown(False)
                assert player.can_showdown(True)
            else:
                assert not player.can_showdown(False)
                assert not player.can_showdown(True)

        assert sum(map(PokerPlayer.total.fget, game.players)) + game.pot \
               == sum(map(PokerPlayer.starting_stack.fget, game.players))
        assert sum(game.side_pots) == game.pot, str(list(game.side_pots)) + ' ' + str(game.pot)

        if game.is_terminal():
            assert game.pot == 0

    @abstractmethod
    def test_hands(self):
        ...
