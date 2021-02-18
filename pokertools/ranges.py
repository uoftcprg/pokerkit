import re

from pokertools.cards import Card, Rank, Suit, parse_cards


def parse_range(pattern: str) -> frozenset[frozenset[Card]]:
    """Parses the supplied pattern.

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

    :param pattern: the supplied pattern to be parsed.
    :return: the parsed card sets
    """
    card_sets = set()

    if match := re.fullmatch(r'(\w)(\w)(\w?)', pattern):
        ranks = list(map(Rank, match.groups()[:2]))
        flag = match.groups()[2]
        cards = set()

        for suit in Suit:
            cards.add(Card(ranks[0], suit))
            cards.add(Card(ranks[1], suit))

        for card_1 in cards:
            for card_2 in cards:
                if card_1.rank == ranks[0] and card_2.rank == ranks[1] and card_1 != card_2:
                    if not flag \
                            or (flag == 's' and card_1.suit == card_2.suit) \
                            or (flag == 'o' and card_1.suit != card_2.suit):
                        card_sets.add(frozenset({card_1, card_2}))
    elif match := re.fullmatch(r'(\w)(\w)(\w?)\+', pattern):
        ranks = list(map(Rank, match.groups()[:2]))
        flag = match.groups()[2]

        if ranks[0] == ranks[1]:
            for rank in list(Rank)[ranks[0].index:]:
                card_sets |= parse_range(rank.value + rank.value + flag)
        else:
            for rank in list(Rank)[ranks[1].index:ranks[0].index]:
                card_sets |= parse_range(ranks[0].value + rank.value + flag)
    else:
        card_sets.add(parse_cards(pattern))

    return frozenset(card_sets)
