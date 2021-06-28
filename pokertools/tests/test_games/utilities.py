from abc import ABC, abstractmethod
from itertools import zip_longest
from random import choice, randint, sample

from gameframe.tests import GameFrameTestCaseMixin

from pokertools import PokerNature, PokerPlayer


class PokerTestCaseMixin(GameFrameTestCaseMixin, ABC):
    GAME_TYPE = None

    @classmethod
    def assert_terminal_poker_game(cls, game, statuses, stacks):
        assert game.is_terminal(), 'Game is not terminal'

        for player, status, stack in zip_longest(game.players, statuses, stacks):
            assert player._status == status, f'Status of player {player.index}: {player._status} does not equal {status}'
            assert player.stack == stack, f'Stack of player {player.index}: {player.stack} does not equal {stack}'

    @classmethod
    def verify_nature(cls, game):
        if game.nature.can_deal_hole():
            for player in game.players:
                if game.nature.can_deal_hole(player):
                    assert game.nature.can_deal_hole(player, sample(game.deck, game.nature.hole_deal_count))
                    assert not game.nature.can_deal_hole(player, sample(game.deck, game.nature.hole_deal_count + 1))

        if game.nature.can_deal_board():
            assert game.nature.can_deal_board(sample(game.deck, game.nature.board_deal_count))
            assert not game.nature.can_deal_board(sample(game.deck, game.nature.board_deal_count + 1))

    @classmethod
    def verify_player(cls, player, game):
        if player.can_fold():
            assert player.bet < max(player.bet for player in game.players)

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

    def test_monte_carlo(self):
        ...

    def test_speed(self):
        ...

    def create_game(self):
        return self.GAME_TYPE(1, (1, 2), tuple(randint(0, 50) for _ in range(randint(2, 4))))

    def act(self, game):
        if isinstance(game.actor, PokerNature):
            if game.actor.can_deal_hole():
                for player in game.players:
                    game.nature.deal_hole(player, sample(game.deck, game.actor.hole_deal_count))
            elif game.actor.can_deal_board():
                game.nature.deal_board(sample(game.deck, game.actor.board_deal_count))
            else:
                raise AssertionError('Poker Nature cannot act')
        elif isinstance(game.actor, PokerPlayer):
            actions = []

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
        else:
            raise AssertionError('Unknown player type')

    def verify(self, game):
        self.verify_nature(game)

        for player in game.players:
            self.verify_player(player, game)

        assert sum(player.bet + player.stack for player in game.players) + game.pot \
               == sum(player.starting_stack for player in game.players)
        assert sum(game.side_pots) == game.pot, str(list(game.side_pots)) + ' ' + str(game.pot)

        if game.is_terminal():
            assert game.pot == 0

    @abstractmethod
    def test_hands(self): ...
