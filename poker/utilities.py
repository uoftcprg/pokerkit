import re
from collections.abc import Iterable

from auxiliary import after
from pokertools import parse_cards

from gameframe.poker.bases import Poker, PokerPlayer


def parse_poker(game: Poker, tokens: Iterable[str]) -> Poker:
    """Parses the tokens as actions and applies them the supplied poker game.

    :param game: The poker game to be applied on.
    :param tokens: The tokens to parse as actions.
    :return: None.
    """
    for token in tokens:
        if isinstance(game.actor, PokerPlayer):
            if match := re.fullmatch(r'br( (?P<amount>\d+))?', token):
                game.actor.bet_raise(None if (amount := match.group('amount')) is None else int(amount))
            elif token == 'cc':
                game.actor.check_call()
            elif token == 'f':
                game.actor.fold()
            elif match := re.fullmatch(r'dd( (?P<discarded_cards>\w*))?( (?P<drawn_cards>\w*))?', token):
                game.actor.discard_draw(
                    () if (cards := match.group('discarded_cards')) is None else parse_cards(cards),
                    None if (cards := match.group('drawn_cards')) is None else parse_cards(cards),
                )
            elif match := re.fullmatch(r's( (?P<forced_status>[0|1]))?', token):
                game.actor.showdown(
                    None if (forced_status := match.group('forced_status')) is None else bool(forced_status),
                )
            else:
                raise ValueError('Invalid command')
        else:
            if match := re.fullmatch(r'dh (?P<index>\d+)( (?P<cards>\w+))?', token):
                game.nature.deal_hole(
                    game.players[int(match.group('index'))],
                    None if (cards := match.group('cards')) is None else parse_cards(cards),
                )
            elif match := re.fullmatch(r'db( (?P<cards>\w+))?', token):
                game.nature.deal_board(None if (cards := match.group('cards')) is None else parse_cards(cards))
            else:
                raise ValueError('Invalid command')

    return game


def _collect(game: Poker) -> None:
    effective_bet = sorted(player.bet for player in game.players)[-2]

    for player in game.players:
        bet = min(effective_bet, player.bet)
        game._pot += bet
        player._stack += player.bet - bet
        player._bet = 0


def _update(game: Poker) -> None:
    if game.stage._done(game):
        game.stage._close(game)

        try:
            stage = after(game.stages, game.stage)

            while stage._done(game):
                stage = after(game.stages, stage)

            game._stage = stage
            stage._open(game)
        except ValueError:
            _distribute(game)
            game._actor = None
    else:
        game._actor = game._queue.pop(0) if game._queue else game.nature


def _distribute(game: Poker) -> None:
    _collect(game)

    for side_pot in game._side_pots:
        amounts = [side_pot.amount // len(game.evaluators)] * len(game.evaluators)
        amounts[0] += side_pot.amount % len(game.evaluators)

        for amount, evaluator in zip(amounts, game.evaluators):
            if len(side_pot.players) == 1:
                players = side_pot.players
            else:
                hand = max(player._hand(evaluator) for player in side_pot.players)
                players = tuple(player for player in side_pot.players if player._hand(evaluator) == hand)

            rewards = [amount // len(players)] * len(players)
            rewards[0] += amount % len(players)

            for player, reward in zip(players, rewards):
                player._stack += reward

    game._pot = 0
