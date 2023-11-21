from typing import Type, Union

from caplena.api import ApiBaseUri, ApiRequestor, ApiVersion
from caplena.http.http_client import HttpClient, HttpRetry
from caplena.logging.default_logger import DefaultLogger
from caplena.logging.logger import Logger, LoggingLevel


class Configuration:
    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def api_base_uri(self) -> ApiBaseUri:
        return self._api_base_uri

    @property
    def api_version(self) -> ApiVersion:
        return self._api_version

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def backoff_factor(self) -> float:
        return self._backoff_factor

    @property
    def http_client(self) -> HttpClient:
        return self._http_client

    @property
    def api_requestor(self) -> ApiRequestor:
        return self._api_requestor

    @property
    def logging_level(self) -> LoggingLevel:
        return self._logging_level

    @property
    def logger(self) -> Logger:
        return self._logger

    def __init__(
        self,
        *,
        api_key: str,
        http_client: Union[Type[HttpClient], HttpClient],
        api_base_uri: ApiBaseUri = ApiBaseUri.PRODUCTION,
        api_version: ApiVersion = ApiVersion.VER_2022_11_22,
        timeout: int = HttpClient.DEFAULT_TIMEOUT,
        max_retries: int = HttpRetry.DEFAULT_MAX_RETRIES,
        backoff_factor: float = HttpRetry.DEFAULT_BACKOFF_FACTOR,
        logging_level: LoggingLevel = LoggingLevel.WARNING,
    ):
        self._api_key = api_key
        self._api_base_uri = api_base_uri
        self._api_version = api_version
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._logging_level = logging_level

        self._logger = DefaultLogger("caplena", self._logging_level)
        self._http_client = self.build_http_client(
            http_client,
            logger=self._logger,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
        self._api_requestor = ApiRequestor(
            http_client=self._http_client,
            logger=self._logger,
        )

    @staticmethod
    def build_http_client(
        http_client: Union[Type[HttpClient], HttpClient],
        *,
        logger: Logger,
        timeout: int = HttpClient.DEFAULT_TIMEOUT,
        max_retries: int = HttpRetry.DEFAULT_MAX_RETRIES,
        backoff_factor: float = HttpRetry.DEFAULT_BACKOFF_FACTOR,
    ) -> HttpClient:
        # check if we get http client instance or if we should instantiate it ourselves
        if not isinstance(http_client, HttpClient):
            http_client = http_client()

        http_client.logger = logger
        http_client.timeout = timeout
        http_client.retry.max_retries = max_retries
        http_client.retry.backoff_factor = backoff_factor

        return http_client
