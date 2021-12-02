from enum import Enum
from typing import Any, Dict, Optional

from caplena.http.http_response import HttpResponse


class HttpMethod(Enum):
    GET = 0
    POST = 1
    PUT = 2
    PATCH = 3
    DELETE = 4
    HEAD = 5


class HttpClient:
    @property
    def identifier(self) -> str:
        raise NotImplementedError("HttpClient subclasses must provide a `identifier` property.")

    def __init__(self):
        pass

    def request(
        self,
        uri: str,
        *,
        method: HttpMethod = HttpMethod.GET,
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        raise NotImplementedError("HttpClient subclasses must implement `request`.")
