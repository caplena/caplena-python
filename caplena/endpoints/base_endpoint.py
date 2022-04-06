from copy import deepcopy
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
from caplena.constants import NOT_SET
from caplena.helpers import Helpers
from caplena.http.http_response import HttpResponse
from caplena.iterator import CaplenaIterator
from caplena.list import CaplenaList

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

    def build(self, resource: Type[BO], obj: Dict[str, Any]) -> BO:
        return resource.build_obj(obj=obj, controller=self, obj_exists=False)

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

    def build_response(
        self,
        response: HttpResponse,
        *,
        resource: Type[BO],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BO:
        json = self._retrieve_json_or_raise(response)
        return resource.build_obj(obj=json, controller=self, obj_exists=True, metadata=metadata)

    def build_iterator(
        self,
        *,
        fetcher: Callable[[int], HttpResponse],
        resource: Type[BO],
        limit: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CaplenaIterator[BO]:
        def results_fetcher(page: int) -> Tuple[List[BO], bool, int]:
            response = fetcher(page)
            json = self._retrieve_json_or_raise(response)

            results = [
                resource.build_obj(res, controller=self, obj_exists=True, metadata=metadata)
                for res in json["results"]
            ]
            return results, json["next_url"] is not None, json["count"]

        return CaplenaIterator(
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
    _previous: Dict[str, Any]
    _metadata: Dict[str, Any]
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

    @property
    def is_modified(self) -> bool:
        return self._attrs != self._previous

    def __init__(self, **attrs: Any):
        self._controller = None
        self._metadata = {}
        self._previous = {}
        self._attrs = Helpers.partial_dict(attrs, self.__fields__)

    def dict(self) -> Dict[str, Any]:
        if self.is_modified:
            raise ValueError(
                "Cannot call `.dict()` on a modified object. HINT: Please call `.save()` to "
                "propagate your updates to our API servers."
            )

        resource: Dict[str, Any] = {}
        for field in self.__fields__:
            attr = self._attrs[field]
            resource[field] = self._rec_dict(attr)

        return resource

    def modified_dict(self) -> Any:
        resource: Dict[str, Any] = {}
        for field in self.__fields__:
            if field not in self._previous:
                resource[field] = self._rec_modified_dict(
                    previous=NOT_SET, next=self._attrs[field], field=field
                )
            elif self._previous[field] != self._attrs[field]:
                resource[field] = self._rec_modified_dict(
                    previous=self._previous[field], next=self._attrs[field], field=field
                )

        return resource if resource != {} else NOT_SET

    def _refresh_from(self, *, attrs: Dict[str, Any]) -> None:
        self._attrs = Helpers.partial_dict(attrs, self.__fields__)
        self._previous = deepcopy(self._attrs)

    def _prepare(
        self,
        *,
        controller: Optional[BC],
        obj_exists: bool = False,
    ) -> None:
        self._controller = controller
        if obj_exists:
            self._previous = deepcopy(self._attrs)

        for field in self.__fields__:
            self._rec_prepare(self._attrs[field], controller=controller, obj_exists=obj_exists)

    def _rec_dict(self, attr: Any) -> Any:
        if isinstance(attr, BaseObject):
            return attr.dict()
        elif isinstance(attr, CaplenaList):
            return [self._rec_dict(i) for i in attr]  # pyright: reportUnknownVariableType=false
        else:
            return attr

    def _rec_modified_dict(self, *, previous: Any, next: Any, field: str) -> Any:
        if isinstance(next, BaseObject):
            return next.modified_dict()
        elif isinstance(next, CaplenaList):
            if len(previous) != len(next):  # pyright: reportUnknownArgumentType=false
                raise ValueError(
                    "Failed computing the version difference, as the previous and new lists have a different length."
                )

            modified_list = [
                self._rec_modified_dict(previous=p, next=n, field=f"{field}.{idx}")
                for idx, (p, n) in enumerate(zip(previous, next))
            ]
            return [item for item in modified_list if item != NOT_SET]

        else:
            return next

    def _rec_prepare(self, attr: Any, *, controller: Optional[BC], obj_exists: bool) -> None:
        if isinstance(attr, BaseObject):
            attr._prepare(
                controller=controller, obj_exists=obj_exists
            )  # pyright: reportUnknownMemberType=false
        elif isinstance(attr, CaplenaList):
            for i in attr:
                self._rec_prepare(i, controller=controller, obj_exists=obj_exists)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __setattr__(self, name: str, value: Any) -> None:
        # TODO: interface for patching can still be improved, currently customer has to
        # manually instantiate the class instance, e.g. when adding new topics.
        if name in self.__fields__ and name in self.__mutable__:
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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseObject):
            return False

        if self.__fields__ != other.__fields__:
            return False

        for field in self.__fields__:
            if self._attrs[field] != other._attrs[field]:
                return False

        return True

    @classmethod
    def build_obj(
        cls: Type[BO],
        obj: Dict[str, Any],
        *,
        controller: Optional[BC],
        obj_exists: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BO:
        instance = cls.parse_obj(obj)
        instance._prepare(controller=controller, obj_exists=obj_exists)
        instance._metadata = metadata if metadata else {}

        return instance

    @classmethod
    def parse_obj(cls: Type[BO], obj: Dict[str, Any]) -> BO:
        return cls(**obj)


class BaseResource(BaseObject[BC]):
    @property
    def id(self) -> str:
        return self._id

    def __init__(self, id: str, **attrs: Any):
        self._id = id
        super().__init__(**attrs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"

    def dict(self) -> Dict[str, Any]:
        resource = super().dict()
        resource["id"] = self._id
        return resource
