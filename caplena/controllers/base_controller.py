from typing import Any, ClassVar, Dict, Iterable, List, Optional, Union

from caplena.api import ApiFilter, ApiOrdering
from caplena.configuration import Configuration


class BaseController:
    DEFAULT_ALLOWED_CODES: ClassVar[Iterable[int]] = frozenset({200})
    DEFAULT_ALLOWED_POST_CODES: ClassVar[Iterable[int]] = frozenset({201})
    DEFAULT_ALLOWED_DELETE_CODES: ClassVar[Iterable[int]] = frozenset({204})

    @property
    def config(self):
        return self._config

    @property
    def api(self):
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
    ):
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
    ):
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
    ):
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
    ):
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
    ):
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
