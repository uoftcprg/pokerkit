""":mod:`pokerkit.analysis` implements classes related to poker
analysis.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from collections import Counter, defaultdict
from concurrent.futures import Executor
from dataclasses import dataclass
from functools import partial
from itertools import (
    chain,
    combinations,
    permutations,
    product,
    repeat,
    starmap,
)
from operator import eq
from random import choices, sample
from statistics import mean, stdev
from typing import Any

from pokerkit.hands import Hand
from pokerkit.notation import HandHistory
from pokerkit.utilities import Card, Deck, max_or_none, RankOrder, Suit

__SUITS = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE


def __parse_range(
        raw_range: str,
        rank_order: RankOrder,
) -> Iterator[frozenset[Card]]:

    def index(r: str) -> int:
        return rank_order.index(r)

    def iterate(ss: Any) -> Iterator[frozenset[Card]]:
        for s0, s1 in ss:
            yield frozenset(Card.parse(f'{r0}{s0}{r1}{s1}'))

    def iterate_plus(s: str) -> Iterator[frozenset[Card]]:
        if r0 == r1:
            r = rank_order[-1]

            yield from __parse_range(f'{r0}{r1}{s}-{r}{r}{s}', rank_order)
        else:
            i0 = index(r0)
            i1 = index(r1)

            if i0 > i1:
                i0, i1 = i1, i0

            for r in rank_order[i0:i1]:
                yield from __parse_range(f'{rank_order[i1]}{r}{s}', rank_order)

    def iterate_interval(s: str) -> Iterator[frozenset[Card]]:
        i0 = index(r0)
        i1 = index(r1)
        i2 = index(r2)
        i3 = index(r3)

        if i1 - i0 != i3 - i2:
            raise ValueError(
                (
                    f'Pattern {repr(raw_range)} is invalid because the two'
                    ' pairs of ranks that bounds the dash-separated notation'
                    ' must be a shifted version of the other.'
                ),
            )

        if i0 > i2:
            i0, i1, i2, i3 = i2, i3, i0, i1

        for ra, rb in zip(
                rank_order[i0:i2 + 1],
                rank_order[i1:i3 + 1],
        ):
            yield from __parse_range(f'{ra}{rb}{s}', rank_order)

    match tuple(raw_range):
        case r0, r1:
            if r0 == r1:
                yield from iterate(combinations(__SUITS, 2))
            else:
                yield from iterate(product(__SUITS, repeat=2))
        case r0, r1, 's':
            if r0 != r1:
                yield from iterate(zip(__SUITS, __SUITS))
        case r0, r1, 'o':
            if r0 == r1:
                yield from __parse_range(f'{r0}{r1}', rank_order)
            else:
                yield from iterate(permutations(__SUITS, 2))
        case r0, r1, '+':
            yield from iterate_plus('')
        case r0, r1, 's', '+':
            yield from iterate_plus('s')
        case r0, r1, 'o', '+':
            yield from iterate_plus('o')
        case r0, r1, '-', r2, r3:
            yield from iterate_interval('')
        case r0, r1, 's', '-', r2, r3, 's':
            yield from iterate_interval('s')
        case r0, r1, 'o', '-', r2, r3, 'o':
            yield from iterate_interval('o')
        case _:
            yield frozenset(Card.parse(raw_range))


def parse_range(
        *raw_ranges: str,
        rank_order: RankOrder = RankOrder.STANDARD,
) -> set[frozenset[Card]]:
    """Parse the range.

    The notations can be separated by a whitespace, comma, or a
    semicolon. The returned range is a set of frozensets of cards.

    >>> rng = parse_range('AKs')
    >>> len(rng)
    4
    >>> frozenset(Card.parse('AsKs')) in rng
    True
    >>> frozenset(Card.parse('AcKd')) in rng
    False

    :param raw_ranges: The raw ranges to be parsed.
    :param rank_order: The rank ordering to be used, defaults to
                       :attr:`pokerkit.utilities.RankOrder`.
    :return: The range.
    """
    raw_ranges = tuple(
        ' '.join(raw_ranges).replace(',', ' ').replace(';', ' ').split(),
    )
    range_ = set[frozenset[Card]]()

    for raw_range in raw_ranges:
        range_.update(__parse_range(raw_range, rank_order))

    return range_


def __calculate_equities_0(
        hole_cards: tuple[list[Card], ...],
        board_cards: list[Card],
        hole_dealing_count: int,
        board_dealing_count: int,
        deck_cards: list[Card],
        hand_types: tuple[type[Hand], ...],
) -> list[float]:
    hole_cards = tuple(map(list.copy, hole_cards))
    board_cards = board_cards.copy()
    sample_count = (
        (hole_dealing_count * len(hole_cards))
        - sum(map(len, hole_cards))
        + board_dealing_count
        - len(board_cards)
    )
    sampled_cards = sample(deck_cards, k=sample_count)
    begin = 0

    for i in range(len(hole_cards)):
        end = begin + hole_dealing_count - len(hole_cards[i])

        hole_cards[i].extend(sampled_cards[begin:end])

        assert len(hole_cards[i]) == hole_dealing_count

        begin = end

    board_cards.extend(sampled_cards[begin:])

    assert len(board_cards) == board_dealing_count

    equities = [0.0] * len(hole_cards)

    for hand_type in hand_types:
        hands = list(
            map(
                partial(hand_type.from_game, board_cards=board_cards),
                hole_cards,
            ),
        )
        max_hand = max_or_none(hands)
        statuses = list(map(partial(eq, max_hand), hands))
        increment = 1 / (len(hand_types) * sum(statuses))

        for i, status in enumerate(statuses):
            if status:
                equities[i] += increment

    return equities


def __calculate_equities_1(
        hole_cards: list[tuple[list[Card], ...]],
        board_cards: list[Card],
        hole_dealing_count: int,
        board_dealing_count: int,
        deck_cards: list[list[Card]],
        hand_types: tuple[type[Hand], ...],
        index: int,
) -> list[float]:
    return __calculate_equities_0(
        hole_cards[index],
        board_cards,
        hole_dealing_count,
        board_dealing_count,
        deck_cards[index],
        hand_types,
    )


def calculate_equities(
        hole_ranges: Iterable[Iterable[Iterable[Card]]],
        board_cards: Iterable[Card],
        hole_dealing_count: int,
        board_dealing_count: int,
        deck: Deck,
        hand_types: Iterable[type[Hand]],
        *,
        sample_count: int,
        executor: Executor | None = None,
) -> list[float]:
    """Calculate the equities.

    The user may supply an executor to use parallelization. If not
    given, a single-threaded evaluation is performed.

    >>> from concurrent.futures import ProcessPoolExecutor
    >>> from pokerkit import *
    >>> calculate_equities(
    ...     (
    ...         parse_range('33'),
    ...         parse_range('33'),
    ...     ),
    ...     Card.parse('Tc8d6h4s'),
    ...     2,
    ...     5,
    ...     Deck.STANDARD,
    ...     (StandardHighHand,),
    ...     sample_count=1000,
    ... )
    [0.5, 0.5]
    >>> calculate_equities(
    ...     (
    ...         parse_range('2h2c'),
    ...         parse_range('3h3c'),
    ...         parse_range('AhKh'),
    ...     ),
    ...     Card.parse('3s3d4c'),
    ...     2,
    ...     5,
    ...     Deck.STANDARD,
    ...     (StandardHighHand,),
    ...     sample_count=1000,
    ... )
    [0.0, 1.0, 0.0]
    >>> with ProcessPoolExecutor() as executor:
    ...     calculate_equities(
    ...         (
    ...             parse_range('2h2c'),
    ...             parse_range('3h3c'),
    ...             parse_range('AsKs'),
    ...         ),
    ...         Card.parse('QsJsTs'),
    ...         2,
    ...         5,
    ...         Deck.STANDARD,
    ...         (StandardHighHand,),
    ...         sample_count=1000,
    ...         executor=executor,
    ...     )
    ...
    [0.0, 0.0, 1.0]

    :param hole_ranges: The ranges of each player in the pot.
    :param board_cards: The board cards, may be empty.
    :param hole_dealing_count: The final number of hole cards; for
                               hold'em, it is ``2``.
    :param board_dealing_count: The final number of board cards; for
                                hold'em, it is ``5``.
    :param deck: The deck; most games typically use
                 :attr:`pokerkit.utilities.Deck.STANDARD`.
    :param hand_types: The hand types; most games typically just use
                       :class:`pokerkit.hands.StandardHighHand`.
    :param sample_count: The number of samples to simulate, higher value
                         gives greater accuracy and fidelity.
    :param executor: The optional executor, defaults to ``None`` which
                     is just using 1 thread/process. The user can supply
                     a ``ProcessPoolExecutor`` to use processes.
    :return: The equity values.
    """
    hole_ranges = tuple(map(list, map(partial(map, list), hole_ranges)))
    board_cards = list(board_cards)
    hand_types = tuple(hand_types)
    hole_cards = []
    deck_cards = []

    for selection in product(*hole_ranges):
        counter = Counter(chain(chain.from_iterable(selection), board_cards))

        if all(count == 1 for count in counter.values()):
            hole_cards.append(selection)
            deck_cards.append(list(set(deck) - counter.keys()))

    fn = partial(
        __calculate_equities_1,
        hole_cards,
        board_cards,
        hole_dealing_count,
        board_dealing_count,
        deck_cards,
        hand_types,
    )
    mapper: Any = map if executor is None else executor.map
    indices = choices(range(len(hole_cards)), k=sample_count)
    equities = [0.0] * len(hole_ranges)

    for i, equity in chain.from_iterable(map(enumerate, mapper(fn, indices))):
        equities[i] += equity

    for i, equity in enumerate(equities):
        equities[i] = equity / sample_count

    return equities


def calculate_hand_strength(
        player_count: int,
        hole_range: Iterable[Iterable[Card]],
        board_cards: Iterable[Card],
        hole_dealing_count: int,
        board_dealing_count: int,
        deck: Deck,
        hand_types: Iterable[type[Hand]],
        *,
        sample_count: int,
        executor: Executor | None = None,
) -> float:
    """Calculate the hand strength: odds of beating a single other hand
    chosen uniformly at random.

    The user may supply an executor to use parallelization. If not
    given, a single-threaded evaluation is performed.

    >>> from concurrent.futures import ProcessPoolExecutor
    >>> from pokerkit import *
    >>> calculate_hand_strength(
    ...     3,
    ...     parse_range('3h3c'),
    ...     Card.parse('3s3d2c2h'),
    ...     2,
    ...     5,
    ...     Deck.STANDARD,
    ...     (StandardHighHand,),
    ...     sample_count=1000,
    ... )
    1.0
    >>> with ProcessPoolExecutor() as executor:
    ...     calculate_hand_strength(
    ...         3,
    ...         parse_range('AsKs'),
    ...         Card.parse('QsJsTs'),
    ...         2,
    ...         5,
    ...         Deck.STANDARD,
    ...         (StandardHighHand,),
    ...         sample_count=1000,
    ...         executor=executor,
    ...     )
    ...
    1.0

    :param player_count: Number of players in the pot.
    :param hole_range: The range of the player.
    :param board_cards: The board cards, may be empty.
    :param hole_dealing_count: The final number of hole cards; for
                               hold'em, it is ``2``.
    :param board_dealing_count: The final number of board cards; for
                                hold'em, it is ``5``.
    :param deck: The deck; most games typically use
                 :attr:`pokerkit.utilities.Deck.STANDARD`.
    :param hand_types: The hand types; most games typically just use
                       :class:`pokerkit.hands.StandardHighHand`.
    :param sample_count: The number of samples to simulate, higher value
                         gives greater accuracy and fidelity.
    :param executor: The optional executor, defaults to ``None`` which
                     is just using 1 thread/process. The user can supply
                     a ``ProcessPoolExecutor`` to use processes.
    :return: The equity values.
    """
    hole_ranges: list[Iterable[Iterable[Card]]] = [
        [[]] for _ in range(player_count - 1)
    ]

    hole_ranges.append(hole_range)

    equities = calculate_equities(
        hole_ranges,
        board_cards,
        hole_dealing_count,
        board_dealing_count,
        deck,
        hand_types,
        sample_count=sample_count,
        executor=executor,
    )

    return equities[-1]


@dataclass
class Statistics:
    """The class for player statistics."""

    payoffs: list[int]
    """The payoffs."""

    @classmethod
    def merge(cls, *statistics: Statistics) -> Statistics:
        """Merge the statistics.

        :param statistics: The statistics to merge.
        :return: The merged stats.
        """
        payoffs = []

        for sub_statistics in statistics:
            payoffs.extend(sub_statistics.payoffs)

        return Statistics(payoffs=payoffs)

    @classmethod
    def from_hand_history(cls, *hhs: HandHistory) -> dict[str, Statistics]:
        """Obtain statistics for each position and players (if any) for a
        hand history or hand histories.

        :param hh: The hand history/histories to analyze.
        :return: The hand history statistics.
        """
        statistics = defaultdict[str, list[Statistics]](list)

        for hh in hhs:
            end_state = tuple(hh)[-1]

            if hh.finishing_stacks is None:
                finishing_stacks = end_state.stacks
            else:
                finishing_stacks = hh.finishing_stacks

            players: Any

            if hh.players is None:
                players = repeat(None)
            else:
                players = hh.players

            for i, (starting_stack, stack, player) in enumerate(
                    zip(hh.starting_stacks, finishing_stacks, players),
            ):
                if player is not None:
                    statistics[player].append(
                        Statistics(payoffs=[stack - starting_stack]),
                    )

        return dict(
            zip(statistics.keys(), starmap(cls.merge, statistics.values())),
        )

    @property
    def sample_count(self) -> int:
        """Return the sample size.

        :return: The sample size.
        """
        return len(self.payoffs)

    @property
    def payoff_sum(self) -> float:
        """Return the total payoff.

        :return: The total payoff.
        """
        return sum(self.payoffs)

    @property
    def payoff_mean(self) -> float:
        """Return the payoff rate (per hand).

        :return: The payoff rate.
        """
        return mean(self.payoffs)

    @property
    def payoff_stdev(self) -> float:
        """Return the payoff standard deviation.

        :return: The payoff stdev.
        """
        return stdev(self.payoffs)
