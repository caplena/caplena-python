from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from caplena.api import ApiFilter, ApiOrdering
from caplena.api.api_requestor import ApiRequestor
from caplena.configuration import Configuration
from caplena.helpers import Helpers
from caplena.http.http_response import HttpResponse
from caplena.iterator import Iterator

OBO = TypeVar("OBO", bound="BaseObject[Any]")
BO = TypeVar("BO", bound="BaseObject[Any]")
BC = TypeVar("BC", bound="BaseController")
T = TypeVar("T")


class BaseController:
    DEFAULT_ALLOWED_CODES: ClassVar[Iterable[int]] = frozenset({200})
    DEFAULT_ALLOWED_POST_CODES: ClassVar[Iterable[int]] = frozenset({201})
    DEFAULT_ALLOWED_DELETE_CODES: ClassVar[Iterable[int]] = frozenset({204})

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def api(self) -> ApiRequestor:
        return self._config.api_requestor

    def __init__(self, *, config: Configuration):
        self._config = config

    def get(
        self,
        path: str,
        *,
        allowed_codes: Iterable[int] = DEFAULT_ALLOWED_CODES,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        filter: Optional[ApiFilter] = None,
        order_by: Optional[ApiOrdering] = None,
    ) -> HttpResponse:
        response = self._config.api_requestor.get(
            base_uri=self._config.api_base_uri,
            path=path,
            api_key=self._config.api_key,
            path_params=path_params,
            query_params=query_params,
            filter=filter,
            order_by=order_by,
        )

        if response.status_code not in allowed_codes:
            raise self._config.api_requestor.build_exc(response)

        return response

    def post(
        self,
        path: str,
        *,
        allowed_codes: Iterable[int] = DEFAULT_ALLOWED_POST_CODES,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> HttpResponse:
        response = self._config.api_requestor.post(
            base_uri=self._config.api_base_uri,
            path=path,
            api_key=self._config.api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
        )

        if response.status_code not in allowed_codes:
            raise self._config.api_requestor.build_exc(response)

        return response

    def put(
        self,
        path: str,
        *,
        allowed_codes: Iterable[int] = DEFAULT_ALLOWED_CODES,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> HttpResponse:
        response = self._config.api_requestor.put(
            base_uri=self._config.api_base_uri,
            path=path,
            api_key=self._config.api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
        )

        if response.status_code not in allowed_codes:
            raise self._config.api_requestor.build_exc(response)

        return response

    def patch(
        self,
        path: str,
        *,
        allowed_codes: Iterable[int] = DEFAULT_ALLOWED_CODES,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> HttpResponse:
        response = self._config.api_requestor.patch(
            base_uri=self._config.api_base_uri,
            path=path,
            api_key=self._config.api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
        )

        if response.status_code not in allowed_codes:
            raise self._config.api_requestor.build_exc(response)

        return response

    def delete(
        self,
        path: str,
        *,
        allowed_codes: Iterable[int] = DEFAULT_ALLOWED_DELETE_CODES,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        response = self._config.api_requestor.delete(
            base_uri=self._config.api_base_uri,
            path=path,
            api_key=self._config.api_key,
            path_params=path_params,
            query_params=query_params,
        )

        if response.status_code not in allowed_codes:
            raise self._config.api_requestor.build_exc(response)

        return response

    def build_response(self, response: HttpResponse, *, resource: Type[BO]) -> BO:
        json = self._retrieve_json_or_raise(response)
        return resource.build_obj(obj=json, controller=self)

    def build_iterator(
        self,
        *,
        fetcher: Callable[[int], HttpResponse],
        limit: int,
        resource: Type[BO],
    ) -> Iterator[BO]:
        def results_fetcher(page: int) -> Tuple[List[BO], bool, int]:
            response = fetcher(page)
            json = self._retrieve_json_or_raise(response)

            results = [resource.build_obj(res, controller=self) for res in json["results"]]
            return results, json["next_url"] is not None, json["count"]

        return Iterator(
            results_fetcher=results_fetcher,
            limit=limit,
        )

    def _retrieve_json_or_raise(self, response: HttpResponse) -> Dict[str, Any]:
        json = response.json
        if json is None:
            raise self.api.build_exc(response)
        else:
            return json


class BaseObject(Generic[BC]):
    __fields__: ClassVar[Set[str]] = set()
    __mutable__: ClassVar[Set[str]] = set()

    _attrs: Dict[str, Any]
    _unpersisted_attributes: Set[str]
    _controller: Optional[BC]

    @property
    def controller(self) -> BC:
        if self._controller is None:
            raise ValueError(
                "You cannot access the non-existing controller for this object. HINT: This object either "
                "does not have a controller attached, or you forgot to manually set the controller after initializing it. "
                "(object.controller = your_controller)"
            )
        return self._controller

    @controller.setter
    def controller(self, value: BC) -> None:
        self._controller = value

        for field in self.__fields__:
            self._recursive_controller_set(self._attrs[field], value=value)

    def __init__(self, **attrs: Any):
        self._controller = None

        self.refresh_from(attrs=attrs)

    def _recursive_controller_set(self, attr: Any, *, value: BC) -> None:
        if isinstance(attr, BaseObject):
            self._controller = value
        elif isinstance(attr, list):
            [self._recursive_controller_set(i, value=value) for i in attr]  # type: ignore

    def refresh_from(self, *, attrs: Dict[str, Any]) -> None:
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
        if isinstance(attr, BaseObject):
            return attr.dict()
        elif isinstance(attr, list):
            return [
                self._recursive_dict(i) for i in attr
            ]  # pyright: reportUnknownVariableType=false
        else:
            return attr

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

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

    @classmethod
    def build_obj(cls: Type[BO], obj: Dict[str, Any], *, controller: Optional[BC]) -> BO:
        instance = cls.parse_obj(obj)
        instance.controller = controller
        return instance

    @classmethod
    def parse_obj(cls: Type[BO], obj: Dict[str, Any]) -> BO:
        return cls(**obj)


class BaseResource(BaseObject[BC]):
    @property
    def id(self) -> str:
        return self._id

    def __init__(self, id: str, **attrs: Any):
        super().__init__(**attrs)
        self._id = id

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"

    def dict(self) -> Dict[str, Any]:
        resource = super().dict()
        resource["id"] = self._id
        return resource
