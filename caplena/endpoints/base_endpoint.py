from typing import Generic, Type, TypeVar

from caplena.controllers.base_controller import BaseController
from caplena.http.http_response import HttpResponse
from caplena.resources.base.base_resource import BaseResource

T = TypeVar("T", bound="BaseController")
U = TypeVar("U", bound="BaseResource")


class BaseEndpoint(Generic[T]):
    @property
    def controller(self):
        return self._controller

    def __init__(self, *, controller: T):
        self._controller = controller

    def build_response(self, response: HttpResponse, *, resource: Type[U]) -> U:
        json = response.json
        if json is None:
            raise self._controller.api.build_exc(response)
        else:
            return resource.parse_obj(json, controller=self._controller)
