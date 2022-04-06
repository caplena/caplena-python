from typing import Any, Dict


class _NOT_SET:
    def __str__(self) -> str:
        return "<NOT_SET>"

    def __copy__(self) -> Any:
        return NOT_SET

    def __deepcopy__(self, memodict: Dict[str, Any] = {}) -> Any:
        return NOT_SET


# note: we use NOT_SET in order to differentiate between `null` and
# `undefined` in JSON. this is especially relevant for update requests
# where not all properties need to be present.
NOT_SET: Any = _NOT_SET()
