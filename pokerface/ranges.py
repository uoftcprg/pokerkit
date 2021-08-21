from itertools import chain, islice, product, starmap

from auxiliary import chunked

from pokerface.cards import Card, Rank, Suit


class Range(set):
    """The class for poker ranges."""

    @classmethod
    def parse(cls, pattern):
        """Parses the supplied two-card pattern.

        :param pattern: The supplied pattern to be parsed.
        :return: The parsed card sets.
        :raises ValueError: If the pattern cannot be parsed.
        """
        if not isinstance(pattern, str):
            return {frozenset(pattern)}

        card_sets = set()

        if 2 <= len(pattern) <= 3 and pattern[-1] != '+':
            ranks, flag = tuple(map(Rank, pattern[:2])), pattern[2:]
            cards = set()

            for suit in Suit:
                cards.add(Card(ranks[0], suit))
                cards.add(Card(ranks[1], suit))

            for card_1, card_2 in product(cards, repeat=2):
                if card_1.rank == ranks[0] and card_2.rank == ranks[1] \
                        and card_1 != card_2:
                    if not flag \
                            or (flag == 's' and card_1.suit == card_2.suit) \
                            or (flag == 'o' and card_1.suit != card_2.suit):
                        card_sets.add(frozenset({card_1, card_2}))
        elif 3 <= len(pattern) <= 4 and pattern[-1] == '+':
            ranks, flag = tuple(map(Rank, pattern[:2])), pattern[2:-1]

            if ranks[0] == ranks[1]:
                for rank in islice(Rank, ranks[0].index, None):
                    card_sets |= cls.parse(rank.value + rank.value + flag)
            else:
                for rank in islice(Rank, ranks[1].index, ranks[0].index):
                    card_sets |= cls.parse(ranks[0].value + rank.value + flag)
        elif len(pattern) % 2 == 0:
            previous = [frozenset()]

            for card_str in chunked(pattern, 2):
                rank_str, suit_str = card_str
                ranks = Rank if rank_str == '?' else (Rank(rank_str),)
                suits = Suit if suit_str == '?' else (Suit(suit_str),)
                next_ = []

                for card_set in previous:
                    for card in starmap(Card, product(ranks, suits)):
                        if card not in card_set:
                            next_.append(card_set | {card})

                previous = next_

            card_sets |= set(previous)
        else:
            raise ValueError('invalid pattern')

        return frozenset(card_sets)

    def __init__(self, *args):
        super().__init__(chain.from_iterable(map(self.parse, args)))
