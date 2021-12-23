from typing import Any, ClassVar, Dict, Set

from caplena.helpers import Helpers


class DictMixin:
    __fields__: ClassVar[Set[str]] = set()
    __mutable__: ClassVar[Set[str]] = set()

    _attrs: Dict[str, Any]
    _unpersisted_attributes: Set[str]

    def __init__(self, **attrs: Any):
        self.refresh_from(attrs=attrs)

    def refresh_from(self, *, attrs: Dict[str, Any]):
        # pick only allowed attributes
        partial = Helpers.partial_dict(attrs, self.__fields__)
        validated = partial

        self._attrs = validated
        self._unpersisted_attributes = set()

    def dict(self) -> Dict[str, Any]:
        resource: Dict[str, Any] = {}
        for field in self.__fields__:
            attr = self._attrs[field]
            resource[field] = self._recursive_dict(attr)

        return resource

    def _recursive_dict(self, attr: Any) -> Any:
        if isinstance(attr, DictMixin):
            return attr.dict()
        elif isinstance(attr, list):
            return [self._recursive_dict(i) for i in attr]  # type: ignore
        else:
            return attr

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__fields__ and name in self.__mutable__:
            self._unpersisted_attributes.add(name)
            self._attrs[name] = value
        elif name in self.__fields__:
            raise AttributeError(
                f"{name}. HINT: You cannot modify this attribute, as it is immutable."
            )
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if name in self.__fields__:
            return self._attrs[name]
        else:
            return super().__getattribute__(name)

    def __delattr__(self, name: str) -> None:
        raise ValueError(f"{name}. HINT: You cannot delete any attributes.")
