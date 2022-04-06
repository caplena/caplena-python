import copy
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar, Union

from caplena.helpers import Helpers

T = TypeVar("T")
U = TypeVar("U", bound="ApiFilter")

ZeroOrMany = Optional[Union[T, List[T]]]
Constraints = Dict[str, List[Dict[str, List[Any]]]]


class ApiFilter:
    DEFAULT: ClassVar[str] = "__default__"

    def __init__(
        self,
        constraints: Optional[Constraints] = None,
        has_conjunction: bool = False,
    ):
        # TODO: how to restrict AND, OR, NONE operations
        self._constraints: Constraints = constraints if constraints is not None else {}
        self._has_conjunction = has_conjunction

    def to_query_params(self) -> Dict[str, str]:
        query_params: Dict[str, str] = {}
        for query_param, clauses in self._constraints.items():
            stringified_clauses: List[str] = []
            for clause in clauses:
                stringified_literals: List[str] = []
                for modifier, values in clause.items():
                    for value in values:
                        str_value = Helpers.build_escaped_filter_str(self.to_string(value=value))
                        if modifier != self.DEFAULT:
                            str_value = f"{modifier}:" + str_value
                        stringified_literals.append(str_value)
                stringified_clauses.append(",".join(stringified_literals))
            query_params[query_param] = ";".join(stringified_clauses)
        return query_params

    def __str__(self) -> str:
        stringified_clauses: List[str] = []
        for name, clauses in self._constraints.items():
            for clause in clauses:
                stringified_literals: List[str] = []
                for modifier, values in clause.items():
                    filt_name = f"{name}"
                    if modifier != self.DEFAULT:
                        filt_name += f".{modifier}"
                    str_values = ",".join([str(value) for value in values])
                    stringified_literals.append(f"{filt_name}={{{str_values}}}")
                stringified_clauses.append("(" + " | ".join(stringified_literals) + ")")
        return "ApiFilter(" + " & ".join(stringified_clauses) + ")"

    def __and__(self: U, other: U) -> U:
        """Creates and returns the immutable conjunction of two separate filters. The original
        filters will not be modified.

        :param self: The first filter.
        :type self: Filter
        :param other: The second filter.
        :type other: Filter
        :rtype: Filter
        """
        new_constraints = copy.deepcopy(self._constraints)
        other_constraints = copy.deepcopy(other._constraints)

        has_conjunction = len(new_constraints.keys()) > 0 and len(other_constraints.keys()) > 0
        has_conjunction = self._has_conjunction if self._has_conjunction else has_conjunction
        has_conjunction = other._has_conjunction if other._has_conjunction else has_conjunction

        for name, clauses in other_constraints.items():
            if name in new_constraints:
                new_constraints[name].extend(clauses)
            else:
                new_constraints[name] = clauses

        return type(self)(constraints=new_constraints, has_conjunction=has_conjunction)

    def __or__(self: U, other: U) -> U:
        """Creates and returns the immutable disjunction of two separate filters. The original
        filters will not be modified.

        :param self: The first filter.
        :type self: Filter
        :param other: The second filter.
        :type other: Filter
        :rtype: Filter
        """
        new_constraints = copy.deepcopy(self._constraints)
        other_constraints = copy.deepcopy(other._constraints)
        new_filters = list(new_constraints.keys())
        other_filters = list(other_constraints.keys())

        has_conjunction = False
        if len(new_filters) == 0:
            has_conjunction = other._has_conjunction
            new_constraints = other_constraints
        elif len(other_filters) == 0:
            has_conjunction = other._has_conjunction
        elif self._has_conjunction or other._has_conjunction:
            raise ValueError(
                "Cannot build the disjunction of already conjuncted filters To fix this error, please make sure "
                "that your filters are in conjunctive normal form (CNF)."
            )
        else:
            if len(new_filters) > 1 or len(other_filters) > 1:
                raise ValueError("Should never execute this code.")
            elif (
                len(new_filters) == 1
                and len(other_filters) == 1  # noqa: W503
                and new_filters[0] != other_filters[0]  # noqa: W503
            ):
                raise ValueError(
                    f"Cannot build the disjunction for filter `{other_filters[0]}`, as there is already a different "
                    f"filter `{new_filters[0]}` being applied."
                )
            elif len(new_filters) == 1 and len(other_filters) == 1:
                name = new_filters[0]
                for filt_name, values in other_constraints[name][0].items():
                    new_constraints[name][0].setdefault(filt_name, [])
                    new_constraints[name][0][filt_name].extend(values)

        return type(self)(constraints=new_constraints, has_conjunction=has_conjunction)

    @classmethod
    def construct(cls: Type[U], *, name: str, filters: Dict[str, ZeroOrMany[Any]]) -> U:
        constraints: Constraints = {}

        clauses: List[Dict[str, List[Any]]] = []
        for filter_name, values in filters.items():
            values_list = cls.to_list(values=values)
            if values_list is not None:
                clause: Dict[str, List[Any]] = {}
                clause[filter_name] = values_list
                clauses.append(clause)

        if len(clauses) > 0:
            constraints[name] = clauses
        has_conjunction = len(clauses) > 1
        return cls(constraints=constraints, has_conjunction=has_conjunction)

    @staticmethod
    def to_list(*, values: ZeroOrMany[Any]) -> Optional[List[Any]]:
        if values is None:
            return None
        elif isinstance(values, list) and len(values) > 0:
            return list(values)
        elif isinstance(values, list):
            return None
        else:
            return [values]

    @staticmethod
    def to_string(*, value: Any) -> str:
        if isinstance(value, datetime):
            return Helpers.to_rfc3339_datetime(value)
        else:
            return str(value)
