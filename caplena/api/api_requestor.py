from typing import Any, Dict, List, Optional, Union

from caplena.api.api_base_uri import ApiBaseUri
from caplena.api.api_exception import ApiException
from caplena.api.api_filter import ApiFilter
from caplena.api.api_ordering import ApiOrdering
from caplena.api.api_version import ApiVersion
from caplena.helpers import Helpers
from caplena.http.http_client import HttpClient, HttpMethod, HttpRetry
from caplena.http.http_response import HttpResponse
from caplena.logging.logger import Logger


class ApiRequestor:
    def __init__(
        self,
        *,
        http_client: HttpClient,
        logger: Logger,
    ):
        self.http_client = http_client
        self.logger = logger

    def build_payload(self, **kwargs: Any) -> Dict[str, Any]:
        return Helpers.build_dict(**kwargs)

    def build_uri(
        self,
        *,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> str:
        path_params = path_params if path_params is not None else {}
        query_params = query_params if query_params is not None else {}
        if isinstance(base_uri, ApiBaseUri):
            base_uri = base_uri.url

        absolute_uri = Helpers.append_path(base_uri=base_uri, path=path)
        return Helpers.build_qualified_uri(
            absolute_uri,
            path_params=path_params,
            query_params=query_params,
        )

    def build_query_params(
        self,
        *,
        query_params: Optional[Dict[str, str]] = None,
        filter: Optional[ApiFilter] = None,
        order_by: Optional[ApiOrdering] = None,
    ) -> Dict[str, str]:
        new_query_params: Dict[str, str] = {}

        if filter is not None:
            new_query_params.update(filter.to_query_params())
        if order_by is not None:
            new_query_params.update(order_by.to_query_params())
        if query_params is not None:
            new_query_params.update(query_params)

        return new_query_params

    def build_request_headers(
        self,
        *,
        headers: Optional[Dict[str, str]] = None,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
    ) -> Dict[str, str]:
        headers = {} if headers is None else headers.copy()
        headers.setdefault("Accept", "application/json")

        # note: we do not allow clients to overwrite user-agent, caplena-api-key or caplena-api-version
        headers["User-Agent"] = Helpers.get_user_agent(identifier=self.http_client.identifier)
        if api_key is not None:
            headers["Caplena-API-Key"] = api_key
        if api_version != ApiVersion.DEFAULT:
            headers["Caplena-API-Version"] = api_version.version

        return headers

    def build_exc(self, response: HttpResponse) -> ApiException:
        exc_body = response.json
        if exc_body:
            self.logger.info(
                "Received error from server", type=exc_body["type"], code=exc_body["code"]
            )
            return ApiException(
                type=exc_body["type"],
                code=exc_body["code"],
                message=exc_body["message"],
                details=exc_body.get("details"),
                help=exc_body.get("help"),
                context=exc_body.get("context"),
            )
        else:
            return ApiException(type="internal_error", code="body.invalid_format")

    def request_raw(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        method: HttpMethod = HttpMethod.GET,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        absolute_uri = self.build_uri(
            base_uri=base_uri,
            path=path,
            path_params=path_params,
            query_params=query_params,
        )
        headers = self.build_request_headers(
            headers=headers,
            api_version=api_version,
            api_key=api_key,
        )

        return self.http_client.request(
            uri=absolute_uri,
            method=method,
            headers=headers,
            json=json,
            timeout=timeout,
            retry=retry,
        )

    def get(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        filter: Optional[ApiFilter] = None,
        order_by: Optional[ApiOrdering] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        query_params = self.build_query_params(
            filter=filter, order_by=order_by, query_params=query_params
        )
        return self.request_raw(
            base_uri=base_uri,
            path=path,
            method=HttpMethod.GET,
            api_version=api_version,
            api_key=api_key,
            path_params=path_params,
            query_params=query_params,
            json=None,
            headers=headers,
            timeout=timeout,
            retry=retry,
        )

    def post(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        return self.request_raw(
            base_uri=base_uri,
            path=path,
            method=HttpMethod.POST,
            api_version=api_version,
            api_key=api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
        )

    def put(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        return self.request_raw(
            base_uri=base_uri,
            path=path,
            method=HttpMethod.PUT,
            api_version=api_version,
            api_key=api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
        )

    def patch(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        return self.request_raw(
            base_uri=base_uri,
            path=path,
            method=HttpMethod.PATCH,
            api_version=api_version,
            api_key=api_key,
            path_params=path_params,
            query_params=query_params,
            json=json,
            headers=headers,
            timeout=timeout,
            retry=retry,
        )

    def delete(
        self,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        *,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        api_key: Optional[str] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        return self.request_raw(
            base_uri=base_uri,
            path=path,
            method=HttpMethod.DELETE,
            api_version=api_version,
            api_key=api_key,
            path_params=path_params,
            query_params=query_params,
            json=None,
            headers=headers,
            timeout=timeout,
            retry=retry,
        )
