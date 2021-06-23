import re
from itertools import islice

from pokertools.cards import Card, Rank, Suit


def rainbow(cards):
    """Checks if all cards have a rainbow texture.

    Cards have a rainbow texture when their suits are all unique to each other.

    :param cards: The cards to check.
    :return: True if the cards have a rainbow texture, else False.
    """
    return _unique(map(Card.suit.fget, cards))


def suited(cards):
    """Checks if all cards are of the same suit.

    :param cards: The cards to check.
    :return: True if the cards are suited, else False.
    """
    return len(set(card.suit for card in cards)) <= 1


def parse_card(card):
    """Parses the string of the card representation.

    :param card: The string of the card representation.
    :return: The parsed card.
    :raises ValueError: If the card-representation is invalid.
    """
    if len(card) == 2:
        rank, suit = card

        return Card(None if rank == '?' else Rank(rank), None if suit == '?' else Suit(suit))
    else:
        raise ValueError('Invalid card representation')


def parse_cards(cards):
    """Parses the string of card representations.

    :param cards: The string of card representations.
    :return: The parsed cards.
    :raises ValueError: If any card-representation is invalid.
    """
    return map(parse_card, (cards[i:i + 2] for i in range(0, len(cards), 2)))


def parse_range(pattern):
    """Parses the supplied pattern.

    >>> from pokertools import parse_range
    >>> parse_range('AKo')
    frozenset({frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), ..., frozenset({Ks, Ac})})
    >>> parse_range('AKs')
    frozenset({frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})})
    >>> parse_range('AK')
    frozenset({frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), ..., frozenset({Kh, Ac})})
    >>> parse_range('AA')
    frozenset({frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), ..., frozenset({As, Ac})})
    >>> parse_range('QQ+')
    frozenset({frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), ..., frozenset({Qd, Qc})})
    >>> parse_range('QT+')
    frozenset({frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), ..., frozenset({Jh, Qc})})
    >>> parse_range('QsTs')
    frozenset({frozenset({Qs, Ts})})

    :param pattern: The supplied pattern to be parsed.
    :return: The parsed card sets.
    :raises ValueError: If the pattern cannot be parsed.
    """
    card_sets = set()

    if match := re.fullmatch(r'(\w)(\w)(\w?)', pattern):
        ranks = tuple(map(Rank, match.groups()[:2]))
        flag = match.groups()[2]
        cards = set()

        for suit in Suit:
            cards.add(Card(ranks[0], suit))
            cards.add(Card(ranks[1], suit))

        for card_1 in cards:
            for card_2 in cards:
                if card_1.rank == ranks[0] and card_2.rank == ranks[1] and card_1 != card_2:
                    if (flag == 's' and card_1.suit == card_2.suit) or (flag == 'o' and card_1.suit != card_2.suit) \
                            or not flag:
                        card_sets.add(frozenset({card_1, card_2}))
    elif match := re.fullmatch(r'(\w)(\w)(\w?)\+', pattern):
        ranks = tuple(map(Rank, match.groups()[:2]))
        flag = match.groups()[2]

        if ranks[0] == ranks[1]:
            for rank in islice(Rank, ranks[0]._index, None):
                card_sets |= parse_range(rank.value + rank.value + flag)
        else:
            for rank in islice(Rank, ranks[1]._index, ranks[0]._index):
                card_sets |= parse_range(ranks[0].value + rank.value + flag)
    else:
        card_sets.add(frozenset(parse_cards(pattern)))

    return frozenset(card_sets)


# TODO: IMPLEMENT TESTS FOR BELOW


def parse_poker(game, tokens):
    """Parses the tokens as actions and applies them the supplied poker game.

    :param game: The poker game to be applied on.
    :param tokens: The tokens to parse as actions.
    :return: None.
    """
    for token in tokens:
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
        elif match := re.fullmatch(r'dh (?P<index>\d+)( (?P<cards>\w+))?', token):
            game.actor.deal_hole(
                game.players[int(match.group('index'))],
                None if (cards := match.group('cards')) is None else parse_cards(cards),
            )
        elif match := re.fullmatch(r'db( (?P<cards>\w+))?', token):
            game.actor.deal_board(None if (cards := match.group('cards')) is None else parse_cards(cards))
        else:
            raise ValueError('Invalid command')

    return game


def _unique(values):
    values = tuple(values)

    return len(values) == len(set(values))


def _collect(game):
    effective_bet = sorted(player.bet for player in game.players)[-2]

    for player in game.players:
        bet = min(effective_bet, player.bet)
        game._pot += bet
        player._stack += player.bet - bet
        player._bet = 0


def _update(game):
    if game.stage._done(game):
        game.stage._close(game)

        try:
            game._stage_index += 1

            while game.stage._done(game):
                game._stage_index += 1

            game.stage._open(game)
        except IndexError:
            _distribute(game)
            game._actor = None
    else:
        game._actor = game._queue.pop(0) if game._queue else game.nature


def _distribute(game):
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
