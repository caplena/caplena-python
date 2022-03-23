from enum import Enum
from json import dumps
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Union

from caplena.http.http_response import HttpResponse
from caplena.http.json_encoder import JsonDateEncoder
from caplena.logging.default_logger import DefaultLogger
from caplena.logging.logger import Logger


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

    def __str__(self) -> str:
        return self.name


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
    DEFAULT_LOGGER: ClassVar[Logger] = DefaultLogger("http[shared]")
    DEFAULT_ENCODER: ClassVar[JsonDateEncoder] = JsonDateEncoder()

    @property
    def identifier(self) -> str:
        raise NotImplementedError("HttpClient subclasses must provide a `identifier` property.")

    def __init__(
        self,
        *,
        timeout: int = DEFAULT_TIMEOUT,
        retry: HttpRetry = DEFAULT_RETRY,
        logger: Logger = DEFAULT_LOGGER,
        encoder: JsonDateEncoder = DEFAULT_ENCODER,
    ):
        self.timeout = timeout
        self.retry = retry
        self.logger = logger
        self.encoder = encoder

    def request(
        self,
        uri: str,
        *,
        method: HttpMethod = HttpMethod.GET,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
        timeout: Optional[int] = None,
        retry: Optional[HttpRetry] = None,
    ) -> HttpResponse:
        timeout = self.get_timeout(timeout)
        retry = self.get_retry(retry)
        self.logger.info("Sending request to Caplena API", method=str(method), uri=uri)

        data = None
        headers = headers if headers is not None else {}
        if json is not None:
            headers["content-type"] = "application/json"
            data = dumps(json, cls=JsonDateEncoder)
            self.logger.debug("Sending request to Caplena API", data=data)

        # TODO: handle retry here
        response = self.request_raw(
            uri=uri,
            method=method,
            timeout=timeout,
            headers=headers,
            data=data,
        )
        self.logger.debug(
            "Received response from server",
            status_code=str(response.status_code),
            text=str(response.text),
        )

        return response

    def request_raw(
        self,
        uri: str,
        *,
        method: HttpMethod,
        timeout: int,
        headers: Dict[str, str],
        data: Optional[str] = None,
    ) -> HttpResponse:
        raise NotImplementedError("HttpClient subclasses must implement `request_raw`.")

    def get_timeout(self, timeout: Optional[int] = None) -> int:
        return timeout if timeout is not None else self.timeout

    def get_retry(self, retry: Optional[HttpRetry] = None) -> HttpRetry:
        return retry if retry is not None else self.retry
