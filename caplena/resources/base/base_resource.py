from typing import Any, Dict, Generic, Type, TypeVar

from caplena.controllers.base_controller import BaseController
from caplena.resources.base.base_mixin import DictMixin

U = TypeVar("U", bound="BaseController")
T = TypeVar("T")


class BaseResource(DictMixin, Generic[U]):
    @property
    def id(self):
        return self._id

    @property
    def controller(self):
        return self._controller

    def __init__(
        self,
        *,
        controller: U,
        id: str,
        **attrs: Any,
    ):
        super().__init__(**attrs)

        self._id = id
        self._controller = controller

    def __str__(self):
        return f"{self.__class__.__name__}(id={self._id})"

    def dict(self) -> Dict[str, Any]:
        resource = super().dict()
        resource["id"] = self._id
        return resource

    @classmethod
    def parse_obj(cls: Type[T], obj: Dict[str, Any], *, controller: U) -> T:
        raise NotImplementedError(f"{cls.__name__} must implement the classmethod `parse_obj`.")
