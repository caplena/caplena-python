from enum import Enum
from json import dumps
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Type, Union

import backoff

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
    DEFAULT_MAX_RETRIES: ClassVar[int] = 5
    DEFAULT_BACKOFF_FACTOR: ClassVar[float] = 2

    def __init__(
        self,
        *,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor


class HttpClient:
    DEFAULT_TIMEOUT: ClassVar[int] = 120
    DEFAULT_RETRY: ClassVar[HttpRetry] = HttpRetry()
    DEFAULT_LOGGER: ClassVar[Logger] = DefaultLogger("http[shared]")
    DEFAULT_ENCODER: ClassVar[JsonDateEncoder] = JsonDateEncoder()
    RETRYABLE_EXCEPTIONS: Sequence[Type[Exception]] = []

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
        req_timeout: int = self.get_timeout(timeout)
        retry = self.get_retry(retry)
        self.logger.info("Sending request to Caplena API", method=str(method), uri=uri)

        data = None
        req_headers: Dict[str, str] = headers if headers is not None else {}
        if json is not None:
            req_headers["content-type"] = "application/json"
            data = dumps(json, cls=JsonDateEncoder)
            self.logger.debug("Sending request to Caplena API", data=data)

        @backoff.on_exception(
            backoff.expo,
            self.RETRYABLE_EXCEPTIONS,
            max_tries=retry.max_retries,
            factor=retry.backoff_factor,
            jitter=backoff.full_jitter,
        )
        def _do_request() -> HttpResponse:
            return self.request_raw(
                uri=uri,
                method=method,
                timeout=req_timeout,
                headers=req_headers,
                data=data,
            )

        response = _do_request()
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
