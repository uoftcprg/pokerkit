from abc import ABC, abstractmethod
from functools import partial
from itertools import chain, zip_longest
from random import choice, randint, sample

from auxiliary import distinct
from krieg.tests import KriegTestCaseMixin

from pokerface import PokerNature, PokerPlayer, Stakes


class PokerTestCaseMixin(KriegTestCaseMixin, ABC):
    GAME_TYPE = None

    @classmethod
    def assert_terminal_poker_game(cls, game, statuses, stacks):
        assert game.is_terminal()

        for player, status, stack in zip_longest(
                game.players, statuses, stacks,
        ):
            assert player._status == status
            assert player.stack == stack

    @property
    def game_name(self):
        game = self.create_game()

        return type(game.limit).__name__ + type(game.variant).__name__.replace(
            'Variant', '',
        )

    def create_game(self):
        return self.GAME_TYPE(Stakes(1, (1, 2)), tuple(
            randint(0, 50) for _ in range(randint(2, 6))
        ))

    def act(self, game):
        actions = []

        if isinstance(game.actor, PokerNature):
            if game.actor.can_deal_hole():
                actions.append(game.actor.deal_hole)
            if game.actor.can_deal_board():
                actions.append(game.actor.deal_board)
        elif isinstance(game.actor, PokerPlayer):
            if game.actor.can_fold():
                actions.append(game.actor.fold)
            if game.actor.can_check_call():
                actions.append(game.actor.check_call)
            if game.actor.can_bet_raise():
                actions.extend((partial(
                    game.actor.bet_raise, game.actor.bet_raise_min_amount,
                ), partial(
                    game.actor.bet_raise, game.actor.bet_raise_max_amount,
                )))
            if game.actor.can_discard_draw():
                actions.append(partial(game.actor.discard_draw, sample(
                    game.actor.hole, randint(0, len(game.actor.hole)),
                )))
            if game.actor.can_showdown():
                actions.append(game.actor.showdown)

        choice(actions)()

    def verify(self, game):
        if game.nature.can_deal_hole():
            assert game.nature.can_deal_hole(sample(
                game.deck, game.nature.deal_hole_count,
            ))
            assert not game.nature.can_deal_hole(sample(
                game.deck, game.nature.deal_hole_count + 1,
            ))

        if game.nature.can_deal_board():
            assert game.nature.can_deal_board(sample(
                game.deck, game.nature.deal_board_count,
            ))
            assert not game.nature.can_deal_board(sample(
                game.deck, game.nature.deal_board_count + 1,
            ))

        for player in game.players:
            if player.can_fold():
                assert player.bet < max(
                    map(PokerPlayer.bet.fget, game.players)
                )

            if player.can_bet_raise():
                assert player.can_bet_raise(player.bet_raise_min_amount)
                assert player.can_bet_raise(player.bet_raise_max_amount)
                assert not player.can_bet_raise(
                    player.bet_raise_min_amount - 1
                )
                assert not player.can_bet_raise(
                    player.bet_raise_max_amount + 1
                )

            if player.can_discard_draw():
                assert player.can_discard_draw(player.hole)
                assert not game.deck or not player.can_discard_draw(game.deck)

                if len(game.deck) < len(player.hole):
                    population = set(chain(game.deck, game.muck)) \
                                 - set(player.seen)
                    cards = set(player.seen) & set(game.muck)

                    if cards:
                        end = max(len(player.hole) - len(cards), 0)
                        assert not player.can_discard_draw(player.hole, chain(
                            cards, tuple(chain(game.deck, game.muck))[:end],
                        ))
                else:
                    population = game.deck

                    if game.muck:
                        end = max(len(player.hole) - len(game.muck), 0)
                        assert not player.can_discard_draw(
                            player.hole,
                            chain(game.muck, game.deck[:end]),
                        )

                assert player.can_discard_draw(player.hole, sample(
                    tuple(population), len(player.hole),
                ))
            else:
                assert not player.can_discard_draw(player.hole)

                if len(game.deck) < len(player.hole):
                    population = set(chain(game.deck, game.muck)) \
                                 - set(player.seen)
                else:
                    population = game.deck

                assert not player.can_discard_draw(player.hole, sample(
                    tuple(population), len(player.hole),
                ))

            if player.can_showdown():
                assert player.can_showdown(False)
                assert player.can_showdown(True)
            else:
                assert not player.can_showdown(False)
                assert not player.can_showdown(True)

            assert set(player.seen) >= set(player.hole)

        assert sum(map(PokerPlayer.total.fget, game.players)) + game.pot \
               == sum(map(PokerPlayer.starting_stack.fget, game.players))
        assert sum(game.side_pots) == game.pot
        assert distinct(chain(game.deck, game.muck, chain.from_iterable(map(
            PokerPlayer.hole.fget, game.players,
        ))))

        if game.is_terminal():
            assert game.pot == 0

    @abstractmethod
    def test_hands(self):
        ...
