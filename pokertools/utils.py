from enum import Enum
from functools import total_ordering
from typing import Any


@total_ordering
class OrderedEnum(Enum):
    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            items: list[Enum] = list(type(self))

            return items.index(self) < items.index(other)
        else:
            return NotImplemented
