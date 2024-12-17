""":mod:`pokerkit.notation` implements classes related to poker
notations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterable, Iterator, Sequence
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import asdict, dataclass, field, fields, KW_ONLY
from decimal import Decimal
from functools import partial
from math import inf
from operator import add, itemgetter
from re import (
    compile,
    DOTALL,
    findall,
    finditer,
    Match,
    match,
    MULTILINE,
    Pattern,
    search,
)
from string import whitespace
from tomllib import loads as loads_toml
from typing import Any, cast, ClassVar, BinaryIO
from warnings import warn
import datetime

from pokerkit.state import (
    Automation,
    BoardDealing,
    BringInPosting,
    CheckingOrCalling,
    CompletionBettingOrRaisingTo,
    Folding,
    HoleCardsShowingOrMucking,
    HoleDealing,
    Mode,
    StandingPatOrDiscarding,
    State,
)
from pokerkit.games import (
    FixedLimitBadugi,
    FixedLimitDeuceToSevenLowballTripleDraw,
    FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
    FixedLimitRazz,
    FixedLimitSevenCardStud,
    FixedLimitSevenCardStudHighLowSplitEightOrBetter,
    FixedLimitTexasHoldem,
    NoLimitDeuceToSevenLowballSingleDraw,
    NoLimitShortDeckHoldem,
    NoLimitTexasHoldem,
    Poker,
    PotLimitOmahaHoldem,
)
from pokerkit.utilities import (
    Card,
    divmod,
    parse_month,
    parse_time,
    parse_value,
    rake,
    rotated,
    UNMATCHABLE_PATTERN,
)


@dataclass
class HandHistory(Iterable[State]):
    """The class for hand histories.

    :param variant: The variant name. For more information, please refer
                    to :attr:`pokerkit.notation.HandHistory.variant`.
    :param ante_trimming_status: The ante trimming status. For more
                                 information, please refer to
                                 :attr:`pokerkit.notation.HandHistory.ante_trimming_status`.
    :param antes: The antes. For more information, please refer to
                  :attr:`pokerkit.notation.HandHistory.antes`.
    :param blinds_or_straddles: The blinds or straddles. For more
                                information, please refer to
                                :attr:`pokerkit.notation.HandHistory.blinds_or_straddles`.
    :param bring_in: The bring-in. For more information, please refer to
                     :attr:`pokerkit.notation.HandHistory.bring_in`.
    :param small_bet: The small bet. For more information, please refer
                      to
                      :attr:`pokerkit.notation.HandHistory.small_bet`.
    :param big_bet: The big bet. For more information, please refer to
                    :attr:`pokerkit.notation.HandHistory.big_bet`.
    :param min_bet: The minimum bet. For more information, please refer
                    to :attr:`pokerkit.notation.HandHistory.min_bet`.
    :param starting_stacks: The starting stacks. For more information,
                            please refer to
                            :attr:`pokerkit.notation.HandHistory.starting_stacks`.
    :param actions: The actions. For more information, please refer to
                    :attr:`pokerkit.notation.HandHistory.actions`.
    :param author: The author. For more information, please refer to
                   :attr:`pokerkit.notation.HandHistory.author`.
    :param event: The event. For more information, please refer to
                  :attr:`pokerkit.notation.HandHistory.event`.
    :param url: The url. For more information, please refer to
                :attr:`pokerkit.notation.HandHistory.url`.
    :param venue: The venue. For more information, please refer to
                  :attr:`pokerkit.notation.HandHistory.venue`.
    :param address: The address. For more information, please refer to
                    :attr:`pokerkit.notation.HandHistory.address`.
    :param city: The city. For more information, please refer to
                 :attr:`pokerkit.notation.HandHistory.city`.
    :param region: The region. For more information, please refer to
                   :attr:`pokerkit.notation.HandHistory.region`.
    :param postal_code: The postal code. For more information, please
                        refer to
                        :attr:`pokerkit.notation.HandHistory.postal_code`.
    :param country: The country. For more information, please refer to
                    :attr:`pokerkit.notation.HandHistory.country`.
    :param time: The time. For more information, please refer to
                 :attr:`pokerkit.notation.HandHistory.time`.
    :param time_zone: The time zone. For more information, please refer
                      to
                      :attr:`pokerkit.notation.HandHistory.time_zone`.
    :param day: The day. For more information, please refer to
                :attr:`pokerkit.notation.HandHistory.day`.
    :param month: The month. For more information, please refer to
                  :attr:`pokerkit.notation.HandHistory.month`.
    :param year: The year. For more information, please refer to
                 :attr:`pokerkit.notation.HandHistory.year`.
    :param hand: The hand name or number. For more information, please
                 refer to :attr:`pokerkit.notation.HandHistory.hand`.
    :param level: The level. For more information, please refer to
                  :attr:`pokerkit.notation.HandHistory.level`.
    :param seats: The seat numbers. For more information, please refer
                  to :attr:`pokerkit.notation.HandHistory.seats`.
    :param seat_count: The number of seats. For more information, please
                       refer to
                       :attr:`pokerkit.notation.HandHistory.seat_count`.
    :param table: The table number. For more information, please refer
                  to :attr:`pokerkit.notation.HandHistory.table`.
    :param players: The player names. For more information, please refer
                    to :attr:`pokerkit.notation.HandHistory.players`.
    :param finishing_stacks: The finishing stacks. For more information,
                             please refer to
                             :attr:`pokerkit.notation.HandHistory.finishing_stacks`.
    :param winnings: The winnings. For more information, please refer to
                     :attr:`pokerkit.notation.HandHistory.winnings`.
    :param currency: The currency. For more information, please refer to
                     :attr:`pokerkit.notation.HandHistory.currency`.
    :param currency_symbol: The currency symbol. For more information,
                            please refer to
                            :attr:`pokerkit.notation.HandHistory.currency_symbol`.
    :param time_limit: The time limit. For more information, please
                       refer to
                       :attr:`pokerkit.notation.HandHistory.time_limit`.
    :param time_banks: The time banks. For more information, please
                       refer to
                       :attr:`pokerkit.notation.HandHistory.time_banks`.
    :param user_defined_fields: The user-defined fields. For more
                                information, please refer to
                                :attr:`pokerkit.notation.HandHistory.user_defined_fields`.
    :param automations: The automations. For more information, please
                        refer to
                        :attr:`pokerkit.notation.HandHistory.automations`.
    :param divmod: The divmod function. For more information, please
                   refer to :attr:`pokerkit.notation.HandHistory.divmod`.
    :param rake: The rake function. For more information, please refer
                 to :attr:`pokerkit.notation.HandHistory.rake`.
    :param parse_value: The value parsing function. For more
                        information, please refer to
                        :attr:`pokerkit.notation.HandHistory.parse_value`.
    """

    game_types: ClassVar[dict[str, type[Poker]]] = {
        'FT': FixedLimitTexasHoldem,
        'NT': NoLimitTexasHoldem,
        'NS': NoLimitShortDeckHoldem,
        'PO': PotLimitOmahaHoldem,
        'FO/8': FixedLimitOmahaHoldemHighLowSplitEightOrBetter,
        'F7S': FixedLimitSevenCardStud,
        'F7S/8': FixedLimitSevenCardStudHighLowSplitEightOrBetter,
        'FR': FixedLimitRazz,
        'N2L1D': NoLimitDeuceToSevenLowballSingleDraw,
        'F2L3D': FixedLimitDeuceToSevenLowballTripleDraw,
        'FB': FixedLimitBadugi,
    }
    """The game codes and the corresponding game types."""
    variants: ClassVar[dict[type[Poker], str]] = dict(
        zip(game_types.values(), game_types.keys()),
    )
    """The game types and the corresponding game codes."""
    required_field_names: ClassVar[dict[str, tuple[str, ...]]] = {
        'FT': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'NT': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'starting_stacks',
            'actions',
        ),
        'NS': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'starting_stacks',
            'actions',
        ),
        'PO': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'starting_stacks',
            'actions',
        ),
        'FO/8': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'F7S': (
            'variant',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'F7S/8': (
            'variant',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'FR': (
            'variant',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'N2L1D': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'starting_stacks',
            'actions',
        ),
        'F2L3D': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
        'FB': (
            'variant',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'starting_stacks',
            'actions',
        ),
    }
    """The required field names."""
    optional_field_names: ClassVar[tuple[str, ...]] = (
        'author',
        'event',
        'url',
        'venue',
        'address',
        'city',
        'region',
        'postal_code',
        'country',
        'time',
        'time_zone',
        'day',
        'month',
        'year',
        'hand',
        'level',
        'seats',
        'seat_count',
        'table',
        'players',
        'finishing_stacks',
        'winnings',
        'currency',
        'currency_symbol',
        'ante_trimming_status',
        'time_limit',
        'time_banks',
    )
    """The optional field names."""
    ACPC_PROTOCOL_VARIANTS: ClassVar[set[str]] = {'FT', 'NT'}
    """The variant codes supported by the ACPC protocol."""
    PLURIBUS_PROTOCOL_VARIANTS: ClassVar[set[str]] = {'NT'}
    """The variant codes supported by the Pluribus protocol."""
    _: KW_ONLY
    variant: str
    """The variant name."""
    ante_trimming_status: bool = False
    """The ante trimming status."""
    antes: list[int]
    """The antes."""
    blinds_or_straddles: list[int] | None = None
    """The blinds or straddles."""
    bring_in: int | None = None
    """The bring-in."""
    small_bet: int | None = None
    """The small bet."""
    big_bet: int | None = None
    """The big bet."""
    min_bet: int | None = None
    """The minimum bet."""
    starting_stacks: list[int]
    """The starting stacks."""
    actions: list[str]
    """The actions."""
    author: str | None = None
    """The author."""
    event: str | None = None
    """The event."""
    url: str | None = None
    """The url."""
    venue: str | None = None
    """The venue."""
    address: str | None = None
    """The address."""
    city: str | None = None
    """The city."""
    region: str | None = None
    """The region."""
    postal_code: str | None = None
    """The postal code."""
    country: str | None = None
    """The country."""
    time: datetime.time | None = None
    """The time."""
    time_zone: str | None = None
    """The time zone."""
    day: int | None = None
    """The day."""
    month: int | None = None
    """The month."""
    year: int | None = None
    """The year."""
    hand: str | int | None = None
    """The hand name or number."""
    level: int | None = None
    """The level."""
    seats: list[int] | None = None
    """The seat numbers."""
    seat_count: int | None = None
    """The number of seats."""
    table: str | int | None = None
    """The table name or number."""
    players: list[str] | None = None
    """The player names."""
    finishing_stacks: list[int] | None = None
    """The finishing stacks."""
    winnings: list[int] | None = None
    """The winnings."""
    currency: str | None = None
    """The currency."""
    currency_symbol: str | None = None
    """The currency symbol."""
    time_limit: int | None = None
    """The time limit."""
    time_banks: list[int] | None = None
    """The time banks."""
    user_defined_fields: dict[str, Any] = field(default_factory=dict)
    """The user-defined fields."""
    automations: tuple[Automation, ...] = (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.CARD_BURNING,
        Automation.RUNOUT_COUNT_SELECTION,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    )
    """The automations."""
    divmod: Callable[[int, int], tuple[int, int]] = divmod
    """The divmod function."""
    rake: Callable[[int], tuple[int, int]] = partial(rake, percentage=0)
    """The rake function."""
    parse_value: Callable[[str], int] = parse_value
    """The value parsing function."""

    @classmethod
    def _filter_non_fields(cls, **kwargs: Any) -> dict[str, Any]:
        field_names = {field.name for field in fields(cls)}
        filtered_fields = {}

        if 'user_defined_fields' in kwargs:
            filtered_fields['user_defined_fields'] = kwargs.pop(
                'user_defined_fields',
            )
        else:
            filtered_fields['user_defined_fields'] = {}

        for key, value in kwargs.items():
            if key in field_names:
                filtered_fields[key] = value
            else:
                if not key.startswith('_'):
                    warn(
                        (
                            f'The field {repr(key)} is an unexpected field and'
                            ' should probably be prefixed with an underscore'
                            ' character \'_\'.'
                        ),
                    )

                filtered_fields['user_defined_fields'][key] = value

        return filtered_fields

    @classmethod
    def loads(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            **kwargs: Any,
    ) -> HandHistory:
        """Load PHH from a ``str`` object.

        :param s: The ``str`` object.
        :param parse_value: The value parsing function.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        return cls(
            **cls._filter_non_fields(
                **loads_toml(s, parse_float=parse_value) | kwargs,
            ),
        )

    @classmethod
    def load(cls, fp: BinaryIO, **kwargs: Any) -> HandHistory:
        """Load PHH from a file pointer.

        :param fp: The file pointer.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        return cls.loads(fp.read().decode(), **kwargs)

    @classmethod
    def loads_all(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            **kwargs: Any,
    ) -> Iterator[HandHistory]:
        """Load PHHs from a ``str`` object.

        :param s: The ``str`` object.
        :param parse_value: The value parsing function.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        for raw_phh in loads_toml(s, parse_float=parse_value).values():
            yield cls(**cls._filter_non_fields(**raw_phh | kwargs))

    @classmethod
    def load_all(cls, fp: BinaryIO, **kwargs: Any) -> Iterator[HandHistory]:
        """Load PHHs from a file pointer.

        :param fp: The file pointer.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        yield from cls.loads_all(fp.read().decode(), **kwargs)

    @classmethod
    def dumps_all(cls, phhs: Iterable[HandHistory]) -> str:
        """Dump PHHs as a ``str`` object.

        :return: a ``str`` object.
        """
        raw_phhs = []

        for i, phh in enumerate(phhs):
            raw_phh = f'[{i + 1}]\n{phh.dumps()}'

            raw_phhs.append(raw_phh)

        return '\n\n'.join(raw_phhs)

    @classmethod
    def dump_all(cls, phhs: Iterable[HandHistory], fp: BinaryIO) -> None:
        """Dump PHH to a file pointer.

        :param fp: The file pointer.
        :return: ``None``.
        """
        fp.write(cls.dumps_all(phhs).encode())

    @classmethod
    def from_game_state(
            cls,
            game: Poker,
            state: State,
            compression_status: bool = True,
            **kwargs: Any,
    ) -> HandHistory:
        """Create a hand history from game state.

        :param game: The game.
        :param state: The state.
        :param compression_status: The compression status.
        :param kwargs: The metadata.
        :return: The hand history.
        """
        action: str | None

        def append_dealing_actions() -> None:
            nonlocal action

            for player_index in sorted(hole_cards):
                if hole_cards[player_index]:
                    action = (
                        f'd dh p{player_index + 1} '
                        + ''.join(map(repr, hole_cards[player_index]))
                    )

                    actions.append(action.strip())
                    hole_cards[player_index].clear()

            if board_cards:
                action = 'd db ' + ''.join(map(repr, board_cards))

                actions.append(action.strip())
                board_cards.clear()

        variant = cls.variants[type(game)]
        actions = []
        hole_cards = defaultdict[int, list[Card]](list)
        board_cards = list[Card]()

        for operation in state.operations:
            if (
                    not compression_status
                    or not isinstance(operation, HoleDealing | BoardDealing)
            ):
                append_dealing_actions()
            if isinstance(operation, BoardDealing):
                board_cards.extend(operation.cards)

                action = None
            elif isinstance(operation, HoleDealing):
                hole_cards[operation.player_index].extend(operation.cards)

                action = None
            elif isinstance(operation, StandingPatOrDiscarding):
                action = (
                    f'p{operation.player_index + 1} sd '
                    + ''.join(map(repr, operation.cards))
                )
            elif isinstance(operation, BringInPosting):
                action = f'p{operation.player_index + 1} pb'
            elif isinstance(operation, Folding):
                action = f'p{operation.player_index + 1} f'
            elif isinstance(operation, CheckingOrCalling):
                action = f'p{operation.player_index + 1} cc'
            elif isinstance(operation, CompletionBettingOrRaisingTo):
                action = (
                    f'p{operation.player_index + 1} cbr {operation.amount}'
                )
            elif isinstance(operation, HoleCardsShowingOrMucking):
                action = (
                    f'p{operation.player_index + 1} sm '
                    + ''.join(map(repr, operation.hole_cards))
                )
            else:
                action = None

            if operation.commentary is not None:
                if action is None:
                    action = f'# {operation.commentary}'
                else:
                    action = action.strip() + f' # {operation.commentary}'

            if action is not None:
                actions.append(action.strip())

        append_dealing_actions()
        kwargs.setdefault('variant', variant)
        kwargs.setdefault('actions', actions)
        kwargs.setdefault('starting_stacks', list(state.starting_stacks))

        field_names = {field.name for field in fields(cls)}

        for name in cls.required_field_names[variant]:
            if name not in field_names:
                continue

            if hasattr(game, name):
                attribute = getattr(game, name)
            elif hasattr(state, name):
                attribute = getattr(state, name)
            else:
                continue

            if isinstance(attribute, Iterable):
                attribute = list(attribute)

            kwargs.setdefault(name, attribute)

        return cls(**cls._filter_non_fields(**kwargs))

    @classmethod
    def from_absolute_poker(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from Absolute Poker.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return AbsolutePokerParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_full_tilt_poker(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from Full Tilt Poker.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return FullTiltPokerParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_ipoker_network(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from iPoker Network.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return IPokerNetworkParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_ongame_network(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from Ongame Network.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return OngameNetworkParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_partypoker(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from PartyPoker.

        If an error is encountered, an error is raised. The error can be
        disabled by setting ``error_status`` to be ``True``. Then,
        errors will be warned.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to skip errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return PartyPokerParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_pokerstars(
            cls,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs from PokerStars.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return PokerStarsParser()(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    @classmethod
    def from_acpc_protocol(
            cls,
            game: Poker,
            starting_stack: int,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        """Parse hand history logs in ACPC Protocol.

        If an error is encountered, an error is raised if
        ``error_status`` is passed as ``True`` (by default, it is
        ``False``). If ``False``, only warnings are shown.

        :param s: The hand history logs.
        :param parse_value: The value parser.
        :param error_status: Set ``True`` to raise errors, otherwise
                                  ``False``.
        :return: The generator that iterates yields hand histories and
                 returns the total number of hands parsed.
        """
        return ACPCProtocolParser(game, starting_stack)(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )

    def __iter__(self) -> Iterator[State]:
        yield from map(itemgetter(0), self.state_actions)

    @property
    def state_actions(self) -> Iterator[tuple[State, str | None]]:
        """Iterate through state-actions.

        If an action from the
        :attr:`pokerkit.notation.HandHistory.actions` field was just
        applied, the ``str`` representation of the action is yielded
        alongside the newly transitioned state. Otherwise, the
        corresponding second value of the pair is ``None``.

        :return: The state actions.
        """
        state = self.create_state()
        actions = deque(self.actions)
        action: str | None

        yield state, None

        while state.status or actions:
            if actions:
                action = actions.popleft()

                try:
                    parse_action(state, action, self.parse_value)
                except ValueError:
                    actions.appendleft(action)

                    action = None
            else:
                action = None

            if action is None:
                if state.can_post_ante():
                    state.post_ante()
                elif state.can_collect_bets():
                    state.collect_bets()
                elif state.can_post_blind_or_straddle():
                    state.post_blind_or_straddle()
                elif state.can_burn_card():
                    state.burn_card('??')

                    if Automation.CARD_BURNING in self.automations:
                        continue
                elif state.can_deal_hole():
                    state.deal_hole('??')
                elif (
                        actions
                        and not state.checking_or_calling_amount
                        and state.can_check_or_call()
                ):
                    state.check_or_call()
                elif actions and state.can_fold():
                    state.fold()
                elif state.status and state.can_show_or_muck_hole_cards(()):
                    state.show_or_muck_hole_cards(())
                elif state.can_select_runout_count():
                    state.select_runout_count()
                elif state.can_kill_hand():
                    state.kill_hand()
                elif state.can_push_chips():
                    state.push_chips()
                elif state.can_pull_chips():
                    state.pull_chips()
                else:
                    break

            yield state, action

        if actions:
            raise ValueError('Unable to repair the hand history')

    @property
    def game_type(self) -> type[Poker]:
        """Return the game type.

        :return: The game type.
        """
        return self.game_types[self.variant]

    def create_game(self) -> Poker:
        """Create the game.

        :return: The game.
        """
        automations = list(self.automations)

        if Automation.CARD_BURNING in self.automations:
            automations.remove(Automation.CARD_BURNING)

        kwargs: dict[str, Any] = {
            'automations': tuple(automations),
            'divmod': self.divmod,
            'rake': self.rake,
            'ante_trimming_status': self.ante_trimming_status,
        }

        for name in self.required_field_names[self.variant]:
            if name == 'antes' or name == 'blinds_or_straddles':
                key = f'raw_{name}'
            else:
                key = name

            kwargs[key] = getattr(self, name)

        kwargs.pop('variant')
        kwargs.pop('starting_stacks')
        kwargs.pop('actions')

        return self.game_type(**kwargs, mode=Mode.CASH_GAME)

    def create_state(self) -> State:
        """Create the initial state.

        :return: The initial state.
        """
        return self.create_game()(
            self.starting_stacks,
            len(self.starting_stacks),
        )

    def dumps(self) -> str:
        """Dump PHH as a ``str`` object.

        :return: a ``str`` object.
        """

        def clean_key(key: str) -> str:
            if set(key) & set(whitespace):
                key = f'\'{key}\''

            return key

        def clean_value(value: Any) -> str:
            cleaned_value: str

            if isinstance(value, bool):
                cleaned_value = repr(value).lower()
            elif isinstance(value, datetime.time):
                cleaned_value = str(value)
            elif isinstance(value, Decimal):
                cleaned_value = 'inf' if value == inf else str(value)
            elif isinstance(value, list):
                cleaned_value = '[' + ', '.join(map(clean_value, value)) + ']'
            elif isinstance(value, dict):
                keys = map(clean_key, value.keys())
                values = map(clean_value, value.values())
                pairs = map(' = '.join, zip(keys, values))
                cleaned_value = '{' + ', '.join(pairs) + '}'
            elif isinstance(value, str):
                if '\'' in value:
                    delimiter = '\'\'\''
                else:
                    delimiter = '\''

                cleaned_value = delimiter + value + delimiter
            else:
                cleaned_value = repr(value)

            return cleaned_value

        lines = []

        for key, value in asdict(self).items():
            if (
                    (
                        key in self.required_field_names[self.variant]
                        or key in self.optional_field_names
                    )
                    and value is not None
            ):
                lines.append(f'{clean_key(key)} = {clean_value(value)}')

        for key, value in self.user_defined_fields.items():
            if value is not None:
                lines.append(f'{clean_key(key)} = {clean_value(value)}')

        return '\n'.join(lines)

    def dump(self, fp: BinaryIO) -> None:
        """Dump PHH to a file pointer.

        :param fp: The file pointer.
        :return: ``None``.
        """
        fp.write(self.dumps().encode())

    def to_acpc_protocol(
            self,
            position: int,
            hand_number: int | None = None,
    ) -> Iterator[tuple[str, str]]:
        """Convert to the ACPC protocol.

        Only the fixed-limit/no-limit Texas hold'em variants are
        supported.

        :param position: The client position.
        :param hand_number: The optional hand number. If ``None``, it is
                            inferred from the field.
        :return: The hand histories in the ACPC protocol.
        :raises ValueError: If the game is not supported or the hand
                            number cannot be determined.
        """
        if self.variant not in self.ACPC_PROTOCOL_VARIANTS:
            raise ValueError(
                (
                    f'The variant {repr(self.variant)} is not among the'
                    ' supported ACPC variants'
                    f' {repr(self.ACPC_PROTOCOL_VARIANTS)}.'
                ),
            )

        if hand_number is None:
            if self.hand is None or not isinstance(self.hand, int):
                raise ValueError(
                    (
                        'Since the hand number is not defined in the hand'
                        ' history object, it must be passed as an argument.'
                    ),
                )

            hand_number = self.hand

        index = 0
        actions = ''
        raw_hole_cards = [['', ''] for _ in self.starting_stacks]
        hole_cards = ''
        board_cards = ''
        match_state = ''
        action = ''

        def egress() -> tuple[str, str]:
            if not all(raw_hole_cards[position]):
                raise ValueError(
                    'The hole cards at the desired position must be known.',
                )

            return 'S->', f'{match_state}\r\n'

        def ingress() -> tuple[str, str]:
            return '<-C', f'{match_state}:{action}\r\n'

        for state in self:
            while index < len(state.operations):
                operation = state.operations[index]
                index += 1

                if (
                        isinstance(
                            operation,
                            (
                                Folding
                                | CheckingOrCalling
                                | CompletionBettingOrRaisingTo
                            ),
                        )
                ):
                    yield egress()

                if isinstance(operation, Folding):
                    action = 'f'
                    actions += action
                elif isinstance(operation, CheckingOrCalling):
                    action = 'c'
                    actions += action
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    match self.variant:
                        case 'FT':
                            action = 'r'
                        case 'NT':
                            amount = -state.payoffs[operation.player_index]
                            action = f'r{amount}'
                        case _:
                            raise AssertionError

                    actions += action

                if (
                        isinstance(
                            operation,
                            (
                                Folding
                                | CheckingOrCalling
                                | CompletionBettingOrRaisingTo
                            ),
                        )
                        and operation.player_index == position
                ):
                    yield ingress()

                if isinstance(operation, HoleDealing):
                    if operation.player_index == position:
                        for i, card in enumerate(operation.cards):
                            if card:
                                raw_hole_cards[position][i] = repr(card)
                elif isinstance(operation, HoleCardsShowingOrMucking):
                    for i, card in enumerate(operation.hole_cards):
                        if card:
                            raw_hole_cards[operation.player_index][i] = repr(
                                card,
                            )

                if isinstance(operation, BoardDealing):
                    actions += '/'
                    board_cards += '/' + ''.join(map(repr, operation.cards))

                hole_cards = '|'.join(map(''.join, raw_hole_cards))
                match_state = (
                    f'MATCHSTATE'
                    f':{position}'
                    f':{hand_number}'
                    f':{actions}'
                    f':{hole_cards}{board_cards}'
                )

        if not state.status or state.actor_index is not None:
            yield egress()

    def to_pluribus_protocol(
            self,
            hand_number: int | None = None,
    ) -> str:
        """Convert to the Pluribus protocol.

        Only the no-limit Texas hold'em variant is supported.

        :param hand_number: The optional hand number. If ``None``, it is
                            inferred from the field.
        :return: The hand histories in the Pluribus protocol.
        :raises ValueError: If the game is not supported or the hand
                            number cannot be determined.
        """
        if self.variant not in self.PLURIBUS_PROTOCOL_VARIANTS:
            raise ValueError(
                (
                    f'The variant {repr(self.variant)} is not among the'
                    ' supported variants for pluribus notation'
                    f' {repr(self.PLURIBUS_PROTOCOL_VARIANTS)}.'
                ),
            )

        if hand_number is None:
            if self.hand is None or not isinstance(self.hand, int):
                raise ValueError(
                    (
                        'Since the hand number is not defined in the hand'
                        ' history object, it must be passed as an argument.'
                    ),
                )

            hand_number = self.hand

        index = 0
        actions = ''
        raw_hole_cards = [['', ''] for _ in self.starting_stacks]
        board_cards = ''

        for state in self:
            while index < len(state.operations):
                operation = state.operations[index]
                index += 1

                if isinstance(operation, Folding):
                    actions += 'f'
                elif isinstance(operation, CheckingOrCalling):
                    actions += 'c'
                elif isinstance(operation, CompletionBettingOrRaisingTo):
                    amount = -state.payoffs[operation.player_index]
                    actions += f'r{amount}'
                elif isinstance(operation, HoleDealing):
                    for i, card in enumerate(operation.cards):
                        if card:
                            raw_hole_cards[operation.player_index][i] = repr(
                                card,
                            )
                elif isinstance(operation, HoleCardsShowingOrMucking):
                    for i, card in enumerate(operation.hole_cards):
                        if card:
                            raw_hole_cards[operation.player_index][i] = repr(
                                card,
                            )
                elif isinstance(operation, BoardDealing):
                    actions += '/'
                    board_cards += '/' + ''.join(map(repr, operation.cards))

        hole_cards = '|'.join(map(''.join, raw_hole_cards))
        raw_payoffs = []

        if self.finishing_stacks is None:
            finishing_stacks = tuple(self)[-1].stacks
        else:
            finishing_stacks = self.finishing_stacks

        for starting_stack, finishing_stack in zip(
                self.starting_stacks,
                finishing_stacks,
        ):
            raw_payoffs.append(finishing_stack - starting_stack)

        payoffs = '|'.join(map(str, raw_payoffs))

        if self.players is None:
            raw_players = [
                f'p{i + 1}' for i in range(len(self.starting_stacks))
            ]
        else:
            raw_players = self.players

        players = '|'.join(raw_players)
        match_state = (
            f'STATE'
            f':{hand_number}'
            f':{actions}'
            f':{hole_cards}{board_cards}'
            f':{payoffs}'
            f':{players}'
        )

        return match_state


def parse_action(
        state: State,
        action: str,
        parse_value: Callable[[str], int] = parse_value,
) -> None:
    """Parse the action.

    :param state: The state.
    :param action: The string action.
    :param parse_value: The value parsing function.
    :return: ``None``.
    """

    def get_player_index() -> int:
        label, parsed_index = player[:1], int(player[1:]) - 1

        if label != 'p':
            raise ValueError(f'{repr(player)} is not a valid player label.')

        return parsed_index

    def verify_player(index: int | None) -> None:
        if get_player_index() != index:
            raise ValueError(
                (
                    f'The player {repr(player)} is not a valid player for the'
                    f' action {repr(action)}.'
                ),
            )

    commentary = action[action.index('#') + 2:] if '#' in action else None
    words = action.split()

    if '#' in words:
        words = words[:words.index('#')]

    match words:
        case 'd', 'db', cards:
            state.deal_board(cards)
        case 'd', 'dh', player, cards:
            state.deal_hole(
                cards,
                get_player_index(),
                commentary=commentary,
            )
        case player, 'sd':
            verify_player(state.stander_pat_or_discarder_index)
            state.stand_pat_or_discard(commentary=commentary)
        case player, 'sd', cards:
            verify_player(state.stander_pat_or_discarder_index)
            state.stand_pat_or_discard(cards, commentary=commentary)
        case player, 'pb':
            verify_player(state.actor_index)
            state.post_bring_in(commentary=commentary)
        case player, 'f':
            verify_player(state.actor_index)
            state.fold(commentary=commentary)
        case player, 'cc':
            verify_player(state.actor_index)
            state.check_or_call(commentary=commentary)
        case player, 'cbr', amount:
            verify_player(state.actor_index)
            state.complete_bet_or_raise_to(
                parse_value(amount),
                commentary=commentary,
            )
        case player, 'sm':
            state.show_or_muck_hole_cards(
                False,
                get_player_index(),
                commentary=commentary,
            )
        case player, 'sm', '-':
            state.show_or_muck_hole_cards(
                True,
                get_player_index(),
                commentary=commentary,
            )
        case player, 'sm', cards:
            state.show_or_muck_hole_cards(
                cards,
                get_player_index(),
                commentary=commentary,
            )
        case ():
            state.no_operate(commentary=commentary)
        case _:
            raise ValueError(
                f'The action {repr(action)} is an invalid action.',
            )


@dataclass
class Parser(ABC):
    """An abstract base class for hand history parser.

    Parsers, when called with raw hand history log string, return a
    generator of poker hand histories.
    """

    @abstractmethod
    def __call__(
            self,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        pass


@dataclass
class REParser(Parser, ABC):
    """An abstract base class for hand history parser using regular
    expressions.
    """

    HAND: ClassVar[Pattern[str]]
    """The hand pattern."""
    FINAL_SEAT: ClassVar[Pattern[str]]
    """Final seat pattern."""
    SEATS: ClassVar[Pattern[str]]
    """Seats pattern."""
    VARIANT: ClassVar[Pattern[str]]
    """Variant pattern."""
    VARIANTS: ClassVar[dict[str, str]]
    """Variant conversion lookup."""
    ANTE_POSTING: ClassVar[Pattern[str]]
    """Ante posting pattern."""
    BLIND_OR_STRADDLE_POSTING: ClassVar[Pattern[str]]
    """Blind or straddle posting pattern."""
    STARTING_STACKS: ClassVar[Pattern[str]]
    """Starting stacks pattern."""
    HOLE_DEALING: ClassVar[Pattern[str]]
    """Hole dealing pattern."""
    BOARD_DEALING: ClassVar[Pattern[str]]
    """Board dealing pattern."""
    FOLDING: ClassVar[Pattern[str]]
    """Folding pattern."""
    CHECKING_OR_CALLING: ClassVar[Pattern[str]]
    """Checking or calling pattern."""
    COMPLETION_BETTING_OR_RAISING: ClassVar[Pattern[str]]
    """Completion, betting, or raising to pattern."""
    HOLE_CARDS_SHOWING: ClassVar[Pattern[str]]
    """Hole cards showing pattern."""
    CONSTANTS: ClassVar[dict[str, Any]] = {}
    """Constants."""
    VARIABLES: ClassVar[
        dict[str, tuple[Pattern[str], Callable[[str], Any] | None]],
    ]
    """Variables."""
    PLAYER_VARIABLES: ClassVar[
        dict[
            str,
            tuple[
                Pattern[str],
                Callable[[str], Any] | None,
                Callable[[], Any],
                Callable[[Any, Any], Any],
            ],
        ],
    ]
    """Player variables."""

    def __call__(
            self,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        ss = findall(self.HAND, s)

        for s in ss:
            try:
                hh = self._parse(s, parse_value)
            except (KeyError, ValueError):
                message = f'Unable to parse {repr(s)}.'

                if error_status:
                    raise ValueError(message)
                else:
                    warn(message)
            else:
                yield hh

        return len(ss)

    def _parse(self, s: str, parse_value: Callable[[str], int]) -> HandHistory:
        final_seat = self._parse_final_seat(s)
        parsed_seats = self._parse_seats(s)
        parsed_players = self._parse_players(s)
        variant = self._parse_variant(s)
        parsed_antes = self._parse_antes(s, parse_value)
        parsed_blinds_or_straddles = self._parse_blinds_or_straddles(
            s,
            parse_value,
        )
        parsed_starting_stacks = self._parse_starting_stacks(s, parse_value)
        players = sorted(parsed_players, key=parsed_seats.__getitem__)
        seats = list(map(parsed_seats.__getitem__, players))
        players = self._get_ordered_players(
            s,
            final_seat,
            parsed_blinds_or_straddles,
            players,
            seats,
        )

        for player in players[2:]:
            parsed_blinds_or_straddles[player] = (
                -parsed_blinds_or_straddles[player]
            )

        seats = list(map(parsed_seats.__getitem__, players))
        antes = list(map(parsed_antes.__getitem__, players))
        blinds_or_straddles = list(
            map(parsed_blinds_or_straddles.__getitem__, players),
        )
        player_count = len(players)

        if player_count == 2:
            antes.reverse()
            blinds_or_straddles.reverse()

        starting_stacks = list(
            map(parsed_starting_stacks.__getitem__, players),
        )
        actions = self._parse_actions(s, parse_value, players)
        hh = HandHistory(
            variant=variant,
            antes=antes,
            blinds_or_straddles=blinds_or_straddles,
            min_bet=max(blinds_or_straddles[:2]),
            starting_stacks=starting_stacks,
            actions=actions,
        )
        game = hh.create_game()
        state = tuple(hh)[-1]
        hh = HandHistory.from_game_state(
            game,
            state,
            seats=seats,
            players=players,
            **self.CONSTANTS,
            **self._parse_variables(s, parse_value),
            **{
                key: cast(Any, list(map(value.__getitem__, players)))
                for key, value
                in self._parse_player_variables(s, parse_value).items()
            },
        )

        return hh

    def _parse_final_seat(self, s: str) -> int:
        m = search(self.FINAL_SEAT, s)

        if m is None:
            raise ValueError('Unable to parse final seat.')

        return int(m['final_seat'])

    def _parse_seats(self, s: str) -> dict[str, int]:
        seats = {}

        for line in s.splitlines():
            if m := search(self.SEATS, line):
                seats[m['player']] = int(m['seat'])

        return seats

    def _parse_players(self, s: str) -> set[str]:
        players = set()

        for line in s.splitlines():
            for pattern in (
                    self.ANTE_POSTING,
                    self.BLIND_OR_STRADDLE_POSTING,
                    self.FOLDING,
                    self.CHECKING_OR_CALLING,
                    self.COMPLETION_BETTING_OR_RAISING,
                    self.HOLE_CARDS_SHOWING,
            ):
                if m := search(pattern, line):
                    players.add(m['player'])

        return players

    def _parse_variant(self, s: str) -> str:
        m = search(self.VARIANT, s)

        if m is None:
            raise ValueError('Unable to parse variant.')

        return self.VARIANTS[m['variant']]

    def _parse_antes(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> defaultdict[str, int]:
        antes = defaultdict(int)

        for line in s.splitlines():
            if m := search(self.ANTE_POSTING, line):
                antes[m['player']] = parse_value(m['ante'])

        return antes

    def _parse_blinds_or_straddles(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> defaultdict[str, int]:
        blinds_or_straddles = defaultdict(int)

        for line in s.splitlines():
            if m := search(self.BLIND_OR_STRADDLE_POSTING, line):
                blinds_or_straddles[m['player']] = parse_value(
                    m['blind_or_straddle'],
                )

        return blinds_or_straddles

    def _parse_starting_stacks(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> dict[str, int]:
        starting_stacks = {}

        for line in s.splitlines():
            if m := search(self.STARTING_STACKS, line):
                starting_stacks[m['player']] = parse_value(m['starting_stack'])

        return starting_stacks

    def _get_ordered_players(
            self,
            s: str,
            final_seat: int,
            parsed_blinds_or_straddles: defaultdict[str, int],
            players: list[str],
            seats: list[int],
    ) -> list[str]:
        if final_seat in seats:
            final_player_index = seats.index(final_seat)
        else:
            if parsed_blinds_or_straddles:
                initial_player = next(iter(parsed_blinds_or_straddles))
                initial_player_index = players.index(initial_player)

                if len(players) == 2:
                    final_player_index = initial_player_index
                else:
                    final_player_index = initial_player_index - 1
            else:
                raise ValueError('Cannot find button.')

        return list(rotated(players, -final_player_index - 1))

    def _parse_actions(
            self,
            s: str,
            parse_value: Callable[[str], int],
            players: Sequence[str],
    ) -> list[str]:

        def format_player(m: Match[str]) -> str:
            player_index = players.index(m['player'])

            return f'p{player_index + 1}'

        bets = defaultdict(int)
        actions = []

        for line in s.splitlines():
            action = None

            if m := search(self.BLIND_OR_STRADDLE_POSTING, line):
                bets[format_player(m)] = parse_value(m['blind_or_straddle'])
            elif m := search(self.HOLE_DEALING, line):
                action = (
                    f'd dh {format_player(m)} {self._format_cards(m)}'
                )
            elif m := search(self.BOARD_DEALING, line):
                action = f'd db {self._format_cards(m)}'

                bets.clear()
            elif m := search(self.FOLDING, line):
                action = f'{format_player(m)} f'
            elif m := search(self.CHECKING_OR_CALLING, line):
                formatted_player = format_player(m)
                action = f'{formatted_player} cc'
                bets[formatted_player] = max(bets.values(), default=0)
            elif m := search(self.COMPLETION_BETTING_OR_RAISING, line):
                formatted_player = format_player(m)
                max_bet = max(bets.values(), default=0)
                bets[formatted_player] = (
                    self._get_completion_betting_or_raising_to_amount(
                        bets,
                        formatted_player,
                        parse_value(m['amount']),
                        line,
                    )
                )

                if bets[formatted_player] <= max_bet:
                    action = f'{formatted_player} cc'
                else:
                    action = f'{formatted_player} cbr {bets[formatted_player]}'
            elif m := search(self.HOLE_CARDS_SHOWING, line):
                action = f'{format_player(m)} sm {self._format_cards(m)}'

            if action is not None:
                actions.append(action)

        return actions

    def _format_cards(self, m: Match[str]) -> str:
        return ''.join(map(repr, Card.parse(m['cards'])))

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        return (
            max(bets.values(), default=0)
            + completion_betting_or_raising_amount
        )

    def _parse_variables(
            self,
            s: str,
            parse_value: Callable[[str], Any],
    ) -> dict[str, Any]:
        variables = {}

        for key, (pattern, parse_pattern) in self.VARIABLES.items():
            if parse_pattern is None:
                parse_pattern = parse_value

            if (m := search(pattern, s)) and key in m.groupdict():
                variables[key] = parse_pattern(m[key])

        return variables

    def _parse_player_variables(
            self,
            s: str,
            parse_value: Callable[[str], Any],
    ) -> dict[str, defaultdict[str, Any]]:
        player_variables = {}

        for (
                key,
                (pattern, parse_pattern, default_value_factory, merge),
        ) in self.PLAYER_VARIABLES.items():
            sub_player_variables = defaultdict[str, Any](default_value_factory)

            if parse_pattern is None:
                parse_pattern = parse_value

            for line in s.splitlines():
                if m := search(pattern, line):
                    player = m['player']
                    sub_player_variables[player] = merge(
                        sub_player_variables[player],
                        parse_pattern(m[key]),
                    )

            if sub_player_variables:
                player_variables[key] = sub_player_variables

        return player_variables


@dataclass
class AbsolutePokerParser(REParser):
    """A class for Absolute Poker hand history parser."""

    HAND = compile(r'^Stage #.+?(?=^\n{2,})', DOTALL | MULTILINE)
    FINAL_SEAT = compile(r' Seat #(?P<final_seat>\d+) is the( dead)? dealer')
    VARIANT = compile(r': (?P<variant>Holdem( \(1 on 1\))?  No Limit) ')
    VARIANTS = {'Holdem  No Limit': 'NT', 'Holdem (1 on 1)  No Limit': 'NT'}
    SEATS = compile(
        r'Seat (?P<seat>\d+) - (?P<player>.+) \(\D?[0-9.,]+ in chips\)',
    )
    ANTE_POSTING = compile(r'(?P<player>.+) - Ante \D?(?P<ante>[0-9.,]+)')
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'(?P<player>.+)'
            r' -'
            r' Posts'
            r' (small|big)'
            r' blind'
            r' \D?(?P<blind_or_straddle>[0-9.,]+)'
        ),
    )
    STARTING_STACKS = compile(
        (
            r'Seat'
            r' \d+'
            r' -'
            r' (?P<player>.+)'
            r' \(\D?(?P<starting_stack>[0-9.,]+)'
            r' in'
            r' chips\)'
        ),
    )
    HOLE_DEALING = UNMATCHABLE_PATTERN
    BOARD_DEALING = compile(
        (
            r'\*\*\*'
            r'('
            r' (FLOP)'
            r' \*\*\*'
            r'|'
            r' (TURN|RIVER)'
            r' \*\*\*'
            r' \[[0-9TJQKAcdhs ]+\]'
            r')'
            r' \[(?P<cards>[0-9TJQKAcdhs ]+)\]'
        ),
    )
    FOLDING = compile(r'(?P<player>.+) - Folds')
    CHECKING_OR_CALLING = compile(r'(?P<player>.+) - C(all|heck)s')
    COMPLETION_BETTING_OR_RAISING = compile(
        (
            r'(?P<player>.+)'
            r' -'
            r' (Bets|Raises|All-In(\(Raise\))?)'
            r' \D?(?P<amount>[0-9.,]+)'
        ),
    )
    HOLE_CARDS_SHOWING = compile(
        r'(?P<player>.+) - Shows \[(?P<cards>[0-9TJQKAcdhs ]+)\]',
    )
    CONSTANTS = {'venue': 'Absolute Poker'}
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r' -'
            r' (?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r' \((?P<time_zone_abbreviation>\S+)\)'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'time_zone_abbreviation': (DATETIME, str),
        'day': (DATETIME, int),
        'month': (DATETIME, int),
        'year': (DATETIME, int),
        'hand': (compile(r'Stage #(?P<hand>\d+):'), int),
        'seat_count': (compile(r'\((?P<seat_count>\d+) max\)'), int),
        'table': (compile(r"Table: (?P<table>.+?) \("), str),
        'currency_symbol': (
            compile(r'\((?P<currency_symbol>\D?)[0-9.,]+ in chips\)'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'winnings': (
            compile(
                (
                    r'Seat'
                    r' \d+:'
                    r' (?P<player>.+?)'
                    r'( \(\D+\))?'
                    r' collected'
                    r' Total'
                    r' \(\D?(?P<winnings>[0-9.,]+)\)'
                ),
            ),
            None,
            int,
            add,
        ),
    }

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        return bets[player] + completion_betting_or_raising_amount


@dataclass
class FullTiltPokerParser(REParser):
    """A class for Full Tilt Poker hand history parser."""

    HAND = compile(
        r'^Full Tilt Poker Game #.+?(?=^\n{2,})',
        DOTALL | MULTILINE,
    )
    FINAL_SEAT = compile(r'The button is in seat #(?P<final_seat>\d+)')
    VARIANT = compile(r" - (\D?\d+ Cap )?(?P<variant>No Limit Hold'em) - ")
    VARIANTS = {'No Limit Hold\'em': 'NT'}
    SEATS = compile(r'Seat (?P<seat>\d+): (?P<player>.+) \(')
    ANTE_POSTING = UNMATCHABLE_PATTERN
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'(?P<player>.+)'
            r' posts'
            r' the'
            r' (small|big)'
            r' blind'
            r' of'
            r' \D?(?P<blind_or_straddle>[0-9.,]+)'
        ),
    )
    STARTING_STACKS = compile(
        r'Seat \d+: (?P<player>.+) \(\D?(?P<starting_stack>[0-9.,]+)\)',
    )
    HOLE_DEALING = UNMATCHABLE_PATTERN
    BOARD_DEALING = compile(
        (
            r'\*\*\*'
            r'('
            r' (FLOP)'
            r' \*\*\*'
            r'|'
            r' (TURN|RIVER)'
            r' \*\*\*'
            r' \[[1-9TJQKAcdhs ]+\]'
            r')'
            r' \[(?P<cards>[1-9TJQKAcdhs ]+)\]'
        ),
    )
    FOLDING = compile(r'(?P<player>.+) folds')
    CHECKING_OR_CALLING = compile(r'(?P<player>.+) c(all|heck)s')
    COMPLETION_BETTING_OR_RAISING = compile(
        r'(?P<player>.+) (bets|raises to) \D?(?P<amount>[0-9.,]+)',
    )
    HOLE_CARDS_SHOWING = compile(
        r'(?P<player>.+) shows \[(?P<cards>[1-9TJQKAcdhs ]+)\]',
    )
    CAP: ClassVar[Pattern[str]] = compile(r' \D?(?P<cap>[0-9.,]+) Cap ')
    CONSTANTS = {'venue': 'Full Tilt Poker'}
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r' -'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r' (?P<time_zone_abbreviation>\S+)'
            r' -'
            r' (?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'time_zone_abbreviation': (DATETIME, str),
        'day': (DATETIME, int),
        'month': (DATETIME, int),
        'year': (DATETIME, int),
        'hand': (compile(r'Full Tilt Poker Game #(?P<hand>\d+):'), int),
        'seat_count': (compile(r'\((?P<seat_count>\d+) max\)'), int),
        'table': (compile(r"Table (?P<table>.+?) "), str),
        'currency_symbol': (
            compile(r'\((?P<currency_symbol>\D?)[0-9.,]+\)'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'winnings': (
            compile(
                (
                    r'Seat'
                    r' \d+:'
                    r' (?P<player>.+)'
                    r' collected'
                    r' \(\D?(?P<winnings>[0-9.,]+)\)'
                ),
            ),
            None,
            int,
            add,
        ),
    }

    def _cap_starting_stacks(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> int | None:
        m = search(self.CAP, s)

        if m is None:
            cap = None
        else:
            cap = parse_value(m['cap'])

        return cap

    def _parse_starting_stacks(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> dict[str, int]:
        starting_stacks = super()._parse_starting_stacks(s, parse_value)
        cap = self._cap_starting_stacks(s, parse_value)

        if cap is not None:
            for key, value in starting_stacks.items():
                if value > cap:
                    starting_stacks[key] = cap

        return starting_stacks

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        return completion_betting_or_raising_amount


@dataclass
class IPokerNetworkParser(REParser):
    """A class for iPoker Network hand history parser."""

    HAND = compile(r'^<game gamecode=".+?</game>', DOTALL | MULTILINE)
    FINAL_SEAT = compile(
        r'<player\b.*\bseat="(?P<final_seat>\d+)".*\bdealer="1".*/>',
    )
    VARIANT = compile(r'(?P<variant>)')
    VARIANTS = {'': 'NT'}
    SEATS = compile(
        (
            r'<player\b'
            r'.*\bseat="(?P<seat>\d+)"'
            r'.*\bname="(?P<player>.+?)"'
            r'.*/>'
        ),
    )
    ANTE_POSTING = UNMATCHABLE_PATTERN
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'<action'
            r'.*\bplayer="(?P<player>.+?)"'
            r'.*\btype="(1|2)"'
            r'.*\bsum="\D?(?P<blind_or_straddle>[0-9.,]+)"'
            r'.*/>'
        ),
    )
    STARTING_STACKS = compile(
        (
            r'<player\b'
            r'.*\bname="(?P<player>.+?)"'
            r'.*\bchips="\D?(?P<starting_stack>[0-9.,]+)"'
            r'.*\bbet="\D?(?P<bet>[0-9.,]+)"'
            r'.*/>'
        ),
    )
    HOLE_DEALING = compile(
        (
            r'<cards\b'
            r'.*\btype="Pocket"'
            r'.*\bplayer="(?P<player>.+?)"'
            r'.*>'
            r'(?P<cards>[0-9TJQKAcdhs ]+)'
            r'</cards>'
        ),
    )
    BOARD_DEALING = compile(
        (
            r'<cards\b'
            r'.*\btype="(Flop|Turn|River)"'
            r'.*>'
            r'(?P<cards>[0-9TJQKAcdhs ]+)'
            r'</cards>'
        ),
    )
    FOLDING = compile(r'<action\b.*\bplayer="(?P<player>.+?)".*\btype="0".*/>')
    CHECKING_OR_CALLING = compile(
        r'<action\b.*\bplayer="(?P<player>.+?)".*\btype="(3|4)".*/>',
    )
    COMPLETION_BETTING_OR_RAISING = compile(
        (
            r'<action\b'
            r'.*\bplayer="(?P<player>.+?)"'
            r'.*\btype="(5|6|23)"'
            r'.*\bsum="\D?(?P<amount>[0-9.,]+)"'
            r'.*/>'
        ),
    )
    HOLE_CARDS_SHOWING = UNMATCHABLE_PATTERN
    CONSTANTS = {'venue': 'iPoker Network'}
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r'<startdate>'
            r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r'</startdate>'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'day': (DATETIME, int),
        'month': (DATETIME, int),
        'year': (DATETIME, int),
        'hand': (compile(r'gamecode="(?P<hand>\d+)"'), int),
        'table': (compile(r'<tablename>(?P<table>.+)</tablename>'), str),
        'currency': (compile(r'<currency>(?P<currency>\w+)</currency>'), str),
        'currency_symbol': (
            compile(r'chips="(?P<currency_symbol>\D?)[0-9.,]+"'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'winnings': (
            compile(
                (
                    r'<player\b'
                    r'.*\bname="(?P<player>.+)"'
                    r'.*\bwin="\D?(?P<winnings>[0-9.,]+)"'
                    r'.*/>'
                ),
            ),
            None,
            int,
            add,
        ),
    }
    PLACEHOLDER_STARTING_STACK: ClassVar[int] = 10000000

    def __call__(
            self,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        variables = self._parse_variables(s, parse_value)
        it = super().__call__(
            s,
            parse_value=parse_value,
            error_status=error_status,
        )
        return_value = None

        while return_value is None:
            try:
                hh = next(it)
            except StopIteration as e:
                return_value = e.value
            else:
                for key, value in variables.items():
                    if getattr(hh, key, None) is None:
                        setattr(hh, key, value)

                yield hh

        return return_value

    def _parse_starting_stacks(
            self,
            s: str,
            parse_value: Callable[[str], int],
    ) -> dict[str, int]:
        starting_stacks = super()._parse_starting_stacks(s, parse_value)

        for key, value in starting_stacks.items():
            if value == self.PLACEHOLDER_STARTING_STACK:
                starting_stacks[key] = parse_value('inf')

        return starting_stacks

    def _get_ordered_players(
            self,
            s: str,
            final_seat: int,
            parsed_blinds_or_straddles: defaultdict[str, int],
            players: list[str],
            seats: list[int],
    ) -> list[str]:
        players = super()._get_ordered_players(
            s,
            final_seat,
            parsed_blinds_or_straddles,
            players,
            seats,
        )
        players = players[:2]

        for line in s.splitlines():
            player = None

            for pattern in (
                    self.FOLDING,
                    self.CHECKING_OR_CALLING,
                    self.COMPLETION_BETTING_OR_RAISING,
            ):
                if m := search(pattern, line):
                    player = m['player']

            if player is None:
                continue
            elif player in players:
                break

            players.append(player)

        return players

    def _format_cards(self, m: Match[str]) -> str:
        raw_cards = ''.join(
            map(''.join, map(reversed, m['cards'].replace('10', 'T').split())),
        )

        return ''.join(map(repr, Card.parse(raw_cards)))

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        if 'type="6"' in line.split():
            amount = bets[player] + completion_betting_or_raising_amount
        else:
            amount = completion_betting_or_raising_amount

        return amount


@dataclass
class OngameNetworkParser(REParser):
    """A class for Ongame Network hand history parser."""

    HAND = compile(
        r'^\*\*\*\*\* History for hand .+?(?=^\n{2,})',
        DOTALL | MULTILINE,
    )
    FINAL_SEAT = compile(r'Button: seat (?P<final_seat>\d+)')
    VARIANT = compile(r'\((?P<variant>NO_LIMIT TEXAS_HOLDEM) ')
    VARIANTS = {'NO_LIMIT TEXAS_HOLDEM': 'NT'}
    SEATS = compile(r'Seat (?P<seat>\d+): (?P<player>.+) \(\D?[0-9.,]+\)[^,]')
    ANTE_POSTING = UNMATCHABLE_PATTERN
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'(?P<player>.+)'
            r' posts'
            r' (small|big)'
            r' blind'
            r' \(\D?(?P<blind_or_straddle>[0-9.,]+)\)'
        ),
    )
    STARTING_STACKS = compile(
        (
            r'Seat'
            r' \d+:'
            r' (?P<player>.+)'
            r' \(\D?(?P<starting_stack>[0-9.,]+)\)[^,]'
        ),
    )
    HOLE_DEALING = UNMATCHABLE_PATTERN
    BOARD_DEALING = compile(
        (
            r'---'
            r' Dealing'
            r' (flop|turn|river)'
            r' \[(?P<cards>[1-9TJQKAcdhs ,]+)\]'
        ),
    )
    FOLDING = compile(r'(?P<player>.+) folds')
    CHECKING_OR_CALLING = compile(r'(?P<player>.+) c(all|heck)s')
    COMPLETION_BETTING_OR_RAISING = compile(
        (
            r'(?P<player>.+)'
            r' (bet|raise)s'
            r' \D?(?P<amount>[0-9.,]+)'
        ),
    )
    HOLE_CARDS_SHOWING = compile(
        (
            r'Seat'
            r' \d+:'
            r' (?P<player>.+)'
            r' \(\D?[0-9.,]+\),'
            r' net:'
            r' (\+|-)?\D?[0-9.,]+,'
            r' \[(?P<cards>[1-9TJQKAcdhs ,]+)\]'
        ),
    )
    CONSTANTS = {'venue': 'Ongame Network'}
    MONTHS: ClassVar[dict[str, int]] = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12,
    }
    """Months as written in Ongame network hand logs."""
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r'Start'
            r' hand:'
            r' \w+'
            r' (?P<month>\w+)'
            r' (?P<day>\d+)'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r' (?P<time_zone_abbreviation>\S+)'
            r' (?P<year>\d+)'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'time_zone_abbreviation': (DATETIME, str),
        'day': (DATETIME, int),
        'month': (DATETIME, MONTHS.get),
        'year': (DATETIME, int),
        'hand': (
            compile(r'\*\*\*\*\* History for hand (?P<hand>.+) \*\*\*\*\*'),
            str,
        ),
        'table': (
            compile(r'Table: (?P<table>\S+) \['),
            str,
        ),
        'currency_symbol': (
            compile(r'\((?P<currency_symbol>\D?)[0-9.,]+\)'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'finishing_stacks': (
            compile(
                (
                    r'Seat'
                    r' \d+:'
                    r' (?P<player>.+)'
                    r' \(\D?(?P<finishing_stacks>[0-9.,]+)\),'
                    r' net:'
                    r' (\+|-)?\D?[0-9.,]+'
                ),
            ),
            None,
            int,
            add,
        ),
        'winnings': (
            compile(
                (
                    r'pot: \D?[0-9.,]+'
                    r' won'
                    r' by'
                    r' (?P<player>.+)'
                    r' \(\D?(?P<winnings>[0-9.,]+)\)'
                ),
            ),
            None,
            int,
            add,
        ),
    }

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        if 'bets' in line.split():
            amount = completion_betting_or_raising_amount
        else:
            amount = bets[player] + completion_betting_or_raising_amount

        return amount


@dataclass
class PartyPokerParser(REParser):
    """A class for PartyPoker hand history parser."""

    HAND = compile(r'^Game #.+?(?=^\n{2,})', DOTALL | MULTILINE)
    FINAL_SEAT = compile(r'Seat (?P<final_seat>\d+) is the button')
    VARIANT = compile(r" (?P<variant>NL Texas Hold'em) - ")
    VARIANTS = {'NL Texas Hold\'em': 'NT'}
    SEATS = compile(r'Seat (?P<seat>\d+): (?P<player>.+) \(')
    ANTE_POSTING = UNMATCHABLE_PATTERN
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'(?P<player>.+)'
            r' posts'
            r' (small|big)'
            r' blind'
            r' \[\D?(?P<blind_or_straddle>[0-9.,]+)'
            r' \w+\]\.'
        ),
    )
    STARTING_STACKS = compile(
        (
            r'Seat'
            r' \d+:'
            r' (?P<player>.+)'
            r' \('
            r' \D?(?P<starting_stack>[0-9.,]+)'
            r' \w+'
            r' \)'
        ),
    )
    HOLE_DEALING = UNMATCHABLE_PATTERN
    BOARD_DEALING = compile(
        (
            r'\*\*'
            r' Dealing'
            r' (Flop|Turn|River)'
            r' \*\*'
            r' \[(?P<cards>[1-9TJQKAcdhs ,]+)\]'
        ),
    )
    FOLDING = compile(r'(?P<player>.+) folds')
    CHECKING_OR_CALLING = compile(r'(?P<player>.+) c(all|heck)s')
    COMPLETION_BETTING_OR_RAISING = compile(
        (
            r'(?P<player>.+)'
            r' (bets|raises|is all-In )'
            r' \[\D?(?P<amount>[0-9.,]+)'
            r' \w+\]'
        ),
    )
    HOLE_CARDS_SHOWING = compile(
        (
            r'(?P<player>.+)'
            r" shows"
            r' \[(?P<cards>[1-9TJQKAcdhs ,]+)\]'
        ),
    )
    CONSTANTS = {'venue': 'PartyPoker'}
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r' -'
            r' \w+,'
            r' (?P<month>\w+)'
            r' (?P<day>\d+),'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r' (?P<time_zone_abbreviation>\S+)'
            r' (?P<year>\d+)'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'time_zone_abbreviation': (DATETIME, str),
        'day': (DATETIME, int),
        'month': (DATETIME, parse_month),
        'year': (DATETIME, int),
        'hand': (
            compile(
                r'\*\*\*\*\* Hand History for Game (?P<hand>\d+) \*\*\*\*\*',
            ),
            int,
        ),
        'table': (compile(r'Table (?P<table>.+?) \('), str),
        'currency': (compile(r'\( \D?[0-9.,]+ (?P<currency>\w+) \)'), str),
        'currency_symbol': (
            compile(r'\( (?P<currency_symbol>\D?)[0-9.,]+ \w+ \)'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'winnings': (
            compile(
                r'^(?P<player>\S+) wins \D?(?P<winnings>[0-9.,]+)',
                MULTILINE,
            ),
            None,
            int,
            add,
        ),
    }

    def _get_completion_betting_or_raising_to_amount(
            self,
            bets: defaultdict[str, int],
            player: str,
            completion_betting_or_raising_amount: int,
            line: str,
    ) -> int:
        return bets[player] + completion_betting_or_raising_amount


@dataclass
class PokerStarsParser(REParser):
    """A class for PokerStars hand history parser."""

    HAND = compile(r'^PokerStars .+?(?=^\n{2,})', DOTALL | MULTILINE)
    FINAL_SEAT = compile(r'#(?P<final_seat>\d+) is the button')
    VARIANT = compile(r":  (?P<variant>Hold'em No Limit) \(")
    VARIANTS = {'Hold\'em No Limit': 'NT'}
    SEATS = compile(r'Seat (?P<seat>\d+): (?P<player>.+) \(')
    ANTE_POSTING = UNMATCHABLE_PATTERN
    BLIND_OR_STRADDLE_POSTING = compile(
        (
            r'(?P<player>.+):'
            r' posts'
            r' (small|big)'
            r' blind'
            r' \D?(?P<blind_or_straddle>[0-9.]+)'
        ),
    )
    STARTING_STACKS = compile(
        (
            r'Seat'
            r' \d+:'
            r' (?P<player>.+)'
            r' \(\D?(?P<starting_stack>[0-9.]+)'
            r' in'
            r' chips\)'
        ),
    )
    HOLE_DEALING = compile(
        r'Dealt to (?P<player>.+) \[(?P<cards>[1-9TJQKAcdhs ]+)\]',
    )
    BOARD_DEALING = compile(
        (
            r'\*\*\*'
            r'('
            r' (FLOP)'
            r' \*\*\*'
            r'|'
            r' (TURN|RIVER)'
            r' \*\*\*'
            r' \[[1-9TJQKAcdhs ]+\]'
            r')'
            r' \[(?P<cards>[1-9TJQKAcdhs ]+)\]'
        ),
    )
    FOLDING = compile(r'(?P<player>.+): folds')
    CHECKING_OR_CALLING = compile(r'(?P<player>.+): c(all|heck)s')
    COMPLETION_BETTING_OR_RAISING = compile(
        r'(?P<player>.+): (bet|raise)s \D?(?P<amount>[0-9.]+)',
    )
    HOLE_CARDS_SHOWING = compile(
        r'(?P<player>.+): shows \[(?P<cards>[1-9TJQKAcdhs ]+)\] (.+)',
    )
    CONSTANTS = {'venue': 'PokerStars'}
    DATETIME: ClassVar[Pattern[str]] = compile(
        (
            r' -'
            r' (?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)'
            r' (?P<time>\d{1,2}:\d{2}:\d{2})'
            r' (?P<time_zone_abbreviation>\S+)'
        ),
    )
    """The datetime pattern."""
    VARIABLES = {
        'time': (DATETIME, parse_time),
        'time_zone_abbreviation': (DATETIME, str),
        'day': (DATETIME, int),
        'month': (DATETIME, int),
        'year': (DATETIME, int),
        'hand': (compile(r'PokerStars (Hand|Game) #(?P<hand>\d+):'), int),
        'seat_count': (compile(r' (?P<seat_count>\d+)-max '), int),
        'table': (compile(r"Table '(?P<table>.+)'"), str),
        'currency_symbol': (
            compile(r'\((?P<currency_symbol>\D?)[0-9.,]+ in chips\)'),
            str,
        ),
    }
    PLAYER_VARIABLES = {
        'winnings': (
            compile(
                (
                    r'Seat'
                    r' \d+:'
                    r' (?P<player>.+)'
                    r' collected'
                    r' \(\D?(?P<winnings>[0-9.,]+)\)'
                ),
            ),
            None,
            int,
            add,
        ),
    }


@dataclass
class ACPCProtocolParser(Parser):
    """A class for ACPC Protocol hand history parser."""

    HAND: ClassVar[tuple[Pattern[str], ...]] = (
        compile(
            (
                r'^(?P<players>[^:\n]+)'
                r':(?P<hand>\d+)'
                r':(?P<actions>[^:\n]+)'
                r':(?P<cards>[^:\n]+)'
                r':(?P<results>[^:\n]+)$'
            ),
            MULTILINE,
        ),
        compile(
            (
                r'^STATE'
                r':(?P<hand>\d+)'
                r':(?P<actions>[^:\n]+)'
                r':(?P<cards>[^:\n]+)'
                r':(?P<results>[^:\n]+)'
                r':(?P<players>[^:\n]+)$'
            ),
            MULTILINE,
        ),
    )
    """The hand patterns."""
    BLIND_POSTING: ClassVar[Pattern[str]] = compile(r'b(?P<blind>\d+)')
    """The blind-posting pattern."""
    FOLDING: ClassVar[Pattern[str]] = compile(r'f')
    """The folding pattern."""
    CHECKING_OR_CALLING: ClassVar[Pattern[str]] = compile(r'c(?P<amount>\d*)')
    """The checking or calling pattern."""
    BETTING_OR_RAISING_TO: ClassVar[Pattern[str]] = compile(
        r'r(?P<amount>\d*)',
    )
    """The betting or raising_to pattern."""
    BOARD_DEALING: ClassVar[Pattern[str]] = compile(r'/')
    """The board-dealing pattern."""
    AUTOMATIONS: ClassVar[tuple[Automation, ...]] = (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        Automation.RUNOUT_COUNT_SELECTION,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    )
    """The automations for the game being simulated."""
    game: Poker
    """The game being played."""
    starting_stack: int
    """The starting stacks."""

    def __post_init__(self) -> None:
        self.game = deepcopy(self.game)
        self.game.automations = self.AUTOMATIONS
        self.game.mode = Mode.CASH_GAME

    def __call__(
            self,
            s: str,
            *,
            parse_value: Callable[[str], int] = parse_value,
            error_status: bool = False,
    ) -> Generator[HandHistory, None, int]:
        count = 0

        for pattern in self.HAND:
            for m in finditer(pattern, s):
                count += 1

                try:
                    hh = self._parse(m, parse_value)
                except (KeyError, ValueError):
                    message = f'Unable to parse {repr(m[0])}.'

                    if error_status:
                        raise ValueError(message)
                    else:
                        warn(message)
                else:
                    yield hh

        return count

    def _parse(
            self,
            m: Match[str],
            parse_value: Callable[[str], int],
    ) -> HandHistory:
        hand = int(m['hand'])
        actions = m['actions']
        raw_hole_cards, *raw_board_cards = m['cards'].split('/')
        hole_cards = deque(
            map(list, map(Card.parse, raw_hole_cards.split('|'))),
        )
        board_cards = deque(map(list, map(Card.parse, raw_board_cards)))
        results = list(map(parse_value, m['results'].split('|')))
        players = m['players'].split('|')
        state = self.game(self.starting_stack, len(players))

        while hole_cards:
            state.deal_hole(hole_cards.popleft())

        assert not hole_cards

        previous_max_amount = 0
        max_amount = max(state.blinds_or_straddles)

        while actions:
            n: Match[str] | None = None

            if n := match(self.BLIND_POSTING, actions):
                pass
            elif n := match(self.FOLDING, actions):
                state.fold()
            elif n := match(self.CHECKING_OR_CALLING, actions):
                if not state.all_in_status:
                    state.check_or_call()
            elif n := match(self.BETTING_OR_RAISING_TO, actions):
                raw_amount = n['amount']
                amount = parse_value(raw_amount) if raw_amount else None

                if amount is not None:
                    max_amount = amount
                    amount -= previous_max_amount

                state.complete_bet_or_raise_to(amount)
            elif n := match(self.BOARD_DEALING, actions):
                state.burn_card('??')
                state.deal_board(board_cards.popleft())

                previous_max_amount = max_amount

            if n is None:
                raise ValueError(f'Invalid next action in {repr(actions)}.')

            actions = actions[len(n.group()):]

        while board_cards:
            state.burn_card('??')
            state.deal_board(board_cards.popleft())

        if state.status:
            raise ValueError('State is not terminal.')

        hh = HandHistory.from_game_state(
            self.game,
            state,
            hand=hand,
            players=players,
            _results=results,
        )

        return hh
