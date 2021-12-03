from enum import Enum
from typing import Any, ClassVar, Dict, Iterable, Optional

from caplena.http.http_response import HttpResponse


class HttpMethod(Enum):
    GET = 0
    POST = 1
    PUT = 2
    PATCH = 3
    DELETE = 4
    HEAD = 5

    @property
    def method(self) -> str:
        return self.name.lower()


class HttpRetry:
    DEFAULT_MAX_RETRIES: ClassVar[int] = 0
    DEFAULT_BACKOFF_FACTOR: ClassVar[float] = 2
    DEFAULT_STATUS_CODES_TO_RETRY: ClassVar[Iterable[int]] = frozenset(
        {408, 409, 413, 429, 500, 502, 503, 504}
    )
    DEFAULT_ALLOWED_METHOD = frozenset({HttpMethod.GET, HttpMethod.PUT, HttpMethod.HEAD})

    def __init__(
        self,
        *,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        retry_status_codes: Iterable[int] = DEFAULT_STATUS_CODES_TO_RETRY,
        retry_methods: Iterable[HttpMethod] = DEFAULT_ALLOWED_METHOD,
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_status_codes = retry_status_codes
        self.retry_methods = retry_methods


class HttpClient:
    DEFAULT_TIMEOUT: ClassVar[int] = 120
    DEFAULT_RETRY: ClassVar[HttpRetry] = HttpRetry()

    @property
    def identifier(self) -> str:
        raise NotImplementedError("HttpClient subclasses must provide a `identifier` property.")

    def __init__(self, *, timeout: int = DEFAULT_TIMEOUT, retry: HttpRetry = DEFAULT_RETRY):
        self.timeout = timeout
        self.retry = retry

    def request(
        self,
        uri: str,
        *,
        method: HttpMethod = HttpMethod.GET,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        raise NotImplementedError("HttpClient subclasses must implement `request`.")

    def get_timeout(self, timeout: Optional[int] = None):
        return timeout if timeout is not None else self.timeout

    def get_retry(self, retry: Optional[HttpRetry] = None):
        return retry if retry is not None else self.retry
