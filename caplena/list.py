from typing import Any, Iterable, List, MutableSequence, TypeVar, Union, overload

T = TypeVar("T")


class CaplenaList(MutableSequence[T]):
    """A custom sequence list, restricting certain modifications of sequence items."""

    _values: List[T]

    _can_replace: bool
    _can_append: bool
    _can_remove: bool

    def __init__(
        self,
        values: Iterable[T] = [],
        *,
        can_replace: bool = False,
        can_append: bool = False,
        can_remove: bool = False,
    ) -> None:
        self._values = list(values)

        # TODO: implement removing, replacing and appending logic in `BaseObject` diff logic.
        if can_replace or can_append or can_remove:
            raise ValueError(
                "Replacing, appending and removing is currently not supported. HINT: To support it, "
                "please implement the respective diff. logic in `BaseObject`."
            )
        self._can_replace = can_replace
        self._can_append = can_append
        self._can_remove = can_remove

    def insert(self, index: int, value: T) -> None:
        if self._can_append is False:
            raise ValueError(
                f"Error appending item at index {index}. HINT: You cannot append any items to this list."
            )

        self._values.insert(index, value)

    def __str__(self) -> str:
        return str(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CaplenaList):
            return False

        return self._values == other._values  # pyright: reportUnknownMemberType=false

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> MutableSequence[T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[T, MutableSequence[T]]:
        return self._values[index]

    @overload
    def __setitem__(self, index: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[T]) -> None:
        ...

    def __setitem__(self, index: Union[int, slice], value: Union[T, Iterable[T]]) -> None:
        if isinstance(index, slice):
            raise ValueError("Using slices to set list items is not supported.")

        if self._can_replace is False:
            raise ValueError(
                f"Error setting item at index {index}. HINT: You cannot replace any items from this list. If you "
                "want to modify an object, consider updating its properties instead of replacing the object itself."
            )

        self._values[index] = value  # type: ignore

    @overload
    def __delitem__(self, index: int) -> None:
        ...

    @overload
    def __delitem__(self, index: slice) -> None:
        ...

    def __delitem__(self, index: Union[int, slice]) -> None:
        if self._can_remove is False:
            raise ValueError(
                f"Error deleting item at index {index}. HINT: You cannot remove any items from this list."
            )

        del self._values[index]
