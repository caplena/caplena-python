from typing import Any, Dict, Type, TypeVar

from caplena.resources.base.base_mixin import DictMixin

T = TypeVar("T", bound="BaseObject")


class BaseObject(DictMixin):
    @classmethod
    def parse_obj(cls: Type[T], obj: Dict[str, Any]) -> T:
        raise NotImplementedError(f"{cls.__name__} must implement the classmethod `parse_obj`.")
