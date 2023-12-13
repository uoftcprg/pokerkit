""":mod:`pokerkit.notation` implements classes related to poker
notations.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import asdict, dataclass, fields, KW_ONLY
from tomllib import load as load_toml, loads as loads_toml
from typing import Any, ClassVar, BinaryIO

from pokerkit.state import (
    Automation,
    BoardDealing,
    BringInPosting,
    CheckingOrCalling,
    CompletionBettingOrRaisingTo,
    Folding,
    HoleCardsShowingOrMucking,
    HoleDealing,
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
from pokerkit.utilities import divmod, parse_value


@dataclass
class HandHistory(Iterable[State]):
    automations: ClassVar[tuple[Automation, ...]] = (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    )
    """The automations."""
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
    game_field_names: ClassVar[dict[str, tuple[str, ...]]] = {
        'FT': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'NT': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'divmod',
        ),
        'NS': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'divmod',
        ),
        'PO': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'divmod',
        ),
        'FO/8': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'F7S': (
            'automations',
            'ante_trimming_status',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'F7S/8': (
            'automations',
            'ante_trimming_status',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'FR': (
            'automations',
            'ante_trimming_status',
            'antes',
            'bring_in',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'N2L1D': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'min_bet',
            'divmod',
        ),
        'F2L3D': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'divmod',
        ),
        'FB': (
            'automations',
            'ante_trimming_status',
            'antes',
            'blinds_or_straddles',
            'small_bet',
            'big_bet',
            'divmod',
        ),
    }
    """The game fields."""
    ignored_field_names: ClassVar[tuple[str, ...]] = (
        'divmod',
        'parse_value',
    )
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
    day: int | None = None
    """The day."""
    month: int | None = None
    """The month."""
    year: int | None = None
    """The year."""
    hand: int | None = None
    """The hand number."""
    seats: list[int] | None = None
    """The seat numbers."""
    seat_count: int | None = None
    """The number of seats."""
    table: int | None = None
    """The table number."""
    players: list[str] | None = None
    """The player names."""
    finishing_stacks: list[int] | None = None
    """The finishing stacks."""
    currency: str | None = None
    """The currency."""
    divmod: Callable[[int, int], tuple[int, int]] = divmod
    """The divmod function."""
    parse_value: Callable[[str], int] = parse_value
    """The value parsing function."""

    @classmethod
    def loads(
            cls,
            s: str,
            **kwargs: Any,
    ) -> HandHistory:
        """Load PHH from ``str`` object.

        :param s: The ``str`` object.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        return cls(**loads_toml(s), **kwargs)

    @classmethod
    def load(
            cls,
            fp: BinaryIO,
            **kwargs: Any,
    ) -> HandHistory:
        """Load PHH from a file pointer.

        :param fp: The file pointer.
        :param kwargs: The metadata.
        :return: The hand history object.
        """
        return cls(**load_toml(fp), **kwargs)

    @classmethod
    def from_game_state(
            cls,
            game: Poker,
            state: State,
            **kwargs: Any,
    ) -> HandHistory:
        """Create a hand history from game state.

        :param game: The game.
        :param state: The state.
        :param kwargs: The metadata.
        :return: The hand history.
        """
        variant = cls.variants[type(game)]
        actions = []

        for operation in state.operations:
            if isinstance(operation, BoardDealing):
                action = 'd db ' + ''.join(map(repr, operation.cards))
            elif isinstance(operation, HoleDealing):
                action = (
                    f'd dh p{operation.player_index + 1} '
                    + ''.join(map(repr, operation.cards))
                )
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

            if action is not None:
                actions.append(action.strip())

        kwargs.setdefault('variant', variant)
        kwargs.setdefault('actions', actions)
        kwargs.setdefault('starting_stacks', list(state.starting_stacks))

        field_names = [field.name for field in fields(cls)]

        for key in cls.game_field_names[variant]:
            if key not in field_names:
                continue

            try:
                value = getattr(game, key)
            except AttributeError:
                try:
                    value = getattr(state, key)
                except AttributeError:
                    continue

            if isinstance(value, Iterable):
                value = list(value)

            kwargs.setdefault(key, value)

        return HandHistory(**kwargs)

    def __iter__(self) -> Iterator[State]:
        state = self.create_state()

        yield state

        for action in self.actions:
            while state.can_burn_card():
                state.burn_card('??')

            parse_action(state, action, self.parse_value)

            yield state

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
        args = (
            getattr(self, name) for name in self.game_field_names[self.variant]
        )

        return self.game_type(*args)

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

        def clean(value: Any) -> str:
            cleaned_value: str

            if isinstance(value, bool):
                cleaned_value = repr(value).lower()
            else:
                cleaned_value = repr(value)

            return cleaned_value

        return '\n'.join(
            f'{key} = {clean(value)}' for (
                key,
                value,
            ) in asdict(self).items() if (
                value is not None
                and key not in self.ignored_field_names
            )
        )

    def dump(self, fp: BinaryIO) -> None:
        """Dump PHH to a file pointer.

        :param fp: The file pointer.
        :return: ``None``.
        """
        fp.write(self.dumps().encode())


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
    def verify_player(index: int | None) -> None:
        label, parsed_index = player[:1], int(player[1:]) - 1

        if label != 'p' or parsed_index != index:
            raise ValueError(f'invalid Player \'{player}\'')

    match action.split():
        case 'd', 'db', cards:
            state.deal_board(cards)
        case 'd', 'dh', player, cards:
            verify_player(state.hole_dealee_index)
            state.deal_hole(cards)
        case player, 'sd':
            verify_player(state.stander_pat_or_discarder_index)
            state.stand_pat_or_discard()
        case player, 'sd', cards:
            verify_player(state.stander_pat_or_discarder_index)
            state.stand_pat_or_discard(cards)
        case player, 'pb':
            verify_player(state.actor_index)
            state.post_bring_in()
        case player, 'f':
            verify_player(state.actor_index)
            state.fold()
        case player, 'cc':
            verify_player(state.actor_index)
            state.check_or_call()
        case player, 'cbr', amount:
            verify_player(state.actor_index)
            state.complete_bet_or_raise_to(parse_value(amount))
        case player, 'sm':
            verify_player(state.showdown_index)
            state.show_or_muck_hole_cards(False)
        case player, 'sm', cards:
            verify_player(state.showdown_index)
            state.show_or_muck_hole_cards(cards)
        case _:
            raise ValueError(f'invalid action \'{action}\'')
