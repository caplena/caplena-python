import copy
from typing import List, Optional, Tuple, TypeVar

from typing_extensions import Literal

T = TypeVar("T", bound="ApiOrdering")
Ordering = List[Tuple[Literal["asc", "desc"], str]]


class ApiOrdering:
    def __init__(self, ordering: Optional[Ordering] = None):
        if ordering is None:
            self._ordering = []
        else:
            self._ordering = ordering

    @classmethod
    def asc(cls, name: str):
        return cls(ordering=[("asc", name)])

    @classmethod
    def desc(cls, name: str):
        return cls(ordering=[("desc", name)])

    def __and__(self: T, other: T) -> T:
        new_ordering = copy.deepcopy(self._ordering)
        other_ordering = copy.deepcopy(other._ordering)
        new_ordering.extend(other_ordering)

        return type(self)(ordering=new_ordering)
