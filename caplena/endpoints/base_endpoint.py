from typing import Any, Callable, Generic, Type, TypeVar

from caplena.controllers.base_controller import BaseController
from caplena.http.http_response import HttpResponse
from caplena.resources.base.base_iterator import BaseIterator
from caplena.resources.base.base_resource import BaseResource

T = TypeVar("T", bound="BaseController")
U = TypeVar("U", bound="BaseResource")

M = TypeVar("M", bound="BaseResource[Any]")


class BaseEndpoint(Generic[T]):
    @property
    def controller(self):
        return self._controller

    def __init__(self, *, controller: T):
        self._controller = controller

    def build_response(self, response: HttpResponse, *, resource: Type[U]) -> U:
        json = self._retrieve_json_or_raise(response)
        return resource.parse_obj(json, controller=self._controller)

    def build_iterator(
        self,
        *,
        fetcher: Callable[[int], HttpResponse],
        limit: int,
        resource: Type[M],
    ) -> BaseIterator[M]:
        def results_fetcher(page: int):
            response = fetcher(page)
            json = self._retrieve_json_or_raise(response)

            results = [
                resource.parse_obj(res, controller=self._controller) for res in json["results"]
            ]
            return results, json["next_url"] is not None, json["count"]

        return BaseIterator(
            results_fetcher=results_fetcher,
            limit=limit,
        )

    def _retrieve_json_or_raise(self, response: HttpResponse):
        json = response.json
        if json is None:
            raise self._controller.api.build_exc(response)
        else:
            return json
