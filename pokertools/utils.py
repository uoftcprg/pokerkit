import re
from collections import Iterable, Iterator, Set
from itertools import islice

from auxiliary import chunk, const

from pokertools.cards import Card, Rank, Suit


def suited(cards: Iterable[Card]) -> bool:
    """Checks if all cards are of the same suit.

    :param cards: The cards to check.
    :return: True if the cards are suited, else False.
    """
    return const(card.suit for card in cards)


def parse_card(card: str) -> Card:
    """Parses the string of the card representation.

    :param card: The string of the card representation.
    :return: The parsed card.
    """
    if isinstance(card, str) and len(card) == 2:
        return Card(Rank(card[0]), Suit(card[1]))
    elif isinstance(card, str):
        raise ValueError('Invalid card representation')
    else:
        raise TypeError('Invalid card type')


def parse_cards(cards: str) -> Iterator[Card]:
    """Parses the string of card representations.

    :param cards: The string of card representations.
    :return: The parsed cards.
    """
    if isinstance(cards, str):
        return map(parse_card, (''.join(card) for card in chunk(cards, 2)))
    else:
        raise TypeError('Invalid cards type')


def parse_range(pattern: str) -> Set[Set[Card]]:
    """Parses the supplied pattern.

       >>> from pokertools import parse_range
       >>> parse_range('AKo')
       {frozenset({Kc, Ah}), frozenset({Kc, As}), frozenset({Kh, Ac}), ..., frozenset({Ks, Ac})}
       >>> parse_range('AKs')
       {frozenset({Ks, As}), frozenset({Kc, Ac}), frozenset({Ad, Kd}), frozenset({Kh, Ah})}
       >>> parse_range('AK')
       {frozenset({Ad, Kd}), frozenset({Kh, Ah}), frozenset({Kc, Ad}), ..., frozenset({Kh, Ac})}
       >>> parse_range('AA')
       {frozenset({Ah, Ac}), frozenset({Ad, Ah}), frozenset({Ad, As}), ..., frozenset({As, Ac})}
       >>> parse_range('QQ+')
       {frozenset({Qc, Qh}), frozenset({Kc, Kd}), frozenset({Ad, As}), ..., frozenset({Qd, Qc})}
       >>> parse_range('QT+')
       {frozenset({Qd, Ts}), frozenset({Qd, Th}), frozenset({Jd, Qc}), ..., frozenset({Jh, Qc})}

    :param pattern: The supplied pattern to be parsed.
    :return: The parsed card sets.
    """
    card_sets: set[Set[Card]] = set()

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
            for rank in islice(Rank, ranks[0].index, None):
                card_sets |= parse_range(rank.value + rank.value + flag)
        else:
            for rank in islice(Rank, ranks[1].index, ranks[0].index):
                card_sets |= parse_range(ranks[0].value + rank.value + flag)
    else:
        card_sets.add(frozenset(parse_cards(pattern)))

    return frozenset(card_sets)
