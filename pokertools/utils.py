from enum import Enum
from functools import total_ordering
from typing import Any


@total_ordering
class OrderedEnum(Enum):
    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.index < other.index
        else:
            return NotImplemented

    @property
    def index(self) -> int:
        return list(type(self)).index(self)  # type: ignore
