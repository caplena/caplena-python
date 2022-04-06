import copy
from typing import Dict, List, Optional, Tuple, Type, TypeVar

from typing_extensions import Literal

from caplena.helpers import Helpers

T = TypeVar("T", bound="ApiOrdering")
Ordering = List[Tuple[Literal["asc", "desc"], str]]


class ApiOrdering:
    def __init__(self, ordering: Optional[Ordering] = None):
        if ordering is None:
            self._ordering = []
        else:
            self._ordering = ordering

    def to_query_params(self) -> Dict[str, str]:
        stringified_ordering: List[str] = []
        for (direction, name) in self._ordering:
            name = Helpers.build_escaped_filter_str(name)
            stringified_ordering.append(f"{direction}:{name}")
        return {"order_by": ";".join(stringified_ordering)}

    def __str__(self) -> str:
        stringified_ordering: List[str] = []
        for (direction, name) in self._ordering:
            stringified_ordering.append(f"{direction}({name})")
        return "ApiOrdering(" + ", ".join(stringified_ordering) + ")"

    @classmethod
    def asc(cls: Type[T], name: str) -> T:
        return cls(ordering=[("asc", name)])

    @classmethod
    def desc(cls: Type[T], name: str) -> T:
        return cls(ordering=[("desc", name)])

    def __and__(self: T, other: T) -> T:
        new_ordering = copy.deepcopy(self._ordering)
        other_ordering = copy.deepcopy(other._ordering)
        new_ordering.extend(other_ordering)

        return type(self)(ordering=new_ordering)
