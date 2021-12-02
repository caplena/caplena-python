from enum import Enum
from typing import Any, Dict, Optional, Union

from caplena.helpers import Helpers
from caplena.http.http_client import HttpClient, HttpMethod


class ApiBaseUri(Enum):
    LOCAL = "http://localhost:8000/v2"
    PRODUCTION = "https://api.caplena.com/v2"

    @property
    def url(self) -> str:
        return self.value


class ApiVersion(Enum):
    DEFAULT = 0
    VER_2021_12_01 = 1

    @property
    def version(self) -> str:
        if self.name != ApiVersion.DEFAULT.name:
            return self.name.replace("VER_", "").replace("_", "-")
        else:
            raise ValueError(f"Cannot convert `{self.name}` to a valid version string.")


class ApiRequestor:
    def __init__(
        self,
        *,
        http_client: HttpClient,
    ):
        self._http_client = http_client

    def build_absolute_uri(
        self,
        *,
        base_uri: Union[str, ApiBaseUri],
        path: str,
        path_params: Optional[Dict[str, str]] = None,
    ) -> str:
        if isinstance(base_uri, ApiBaseUri):
            base_uri = base_uri.url

        # TODO: clean up URIs (e.g. removing double slashes, and similar)
        # TODO: implement path parameters
        # TODO: implement query parameters
        return base_uri + path

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
        headers["User-Agent"] = Helpers.get_user_agent(identifier=self._http_client.identifier)
        if api_key is not None:
            headers["Caplena-API-Key"] = api_key
        if api_version != ApiVersion.DEFAULT:
            headers["Caplena-API-Version"] = api_version.version

        return headers

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
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        absolute_uri = self.build_absolute_uri(
            base_uri=base_uri,
            path=path,
            path_params=path_params,
        )
        headers = self.build_request_headers(
            headers=headers,
            api_version=api_version,
            api_key=api_key,
        )

        return self._http_client.request(
            uri=absolute_uri,
            method=method,
            query_params=query_params,
            headers=headers,
            json=json,
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
    ):
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
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
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
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
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
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
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
    ):
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
        )
