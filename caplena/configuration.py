from typing import Type

from caplena.api import ApiBaseUri, ApiRequestor, ApiVersion
from caplena.http.http_client import HttpClient
from caplena.logging import LoggingLevel


class Configuration:
    @property
    def api_key(self):
        return self._api_key

    @property
    def api_base_uri(self):
        return self._api_base_uri

    @property
    def api_version(self):
        return self._api_version

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def backoff_factor(self):
        return self._backoff_factor

    @property
    def logging_level(self):
        return self._logging_level

    @property
    def api_requestor(self):
        return self._api_requestor

    def __init__(
        self,
        *,
        api_key: str,
        api_base_uri: ApiBaseUri = ApiBaseUri.PRODUCTION,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        timeout: int = 30,
        max_retries: int = 0,
        backoff_factor: int = 2,
        http_client_class: Type[HttpClient],
        logging_level: LoggingLevel = LoggingLevel.WARNING,
    ):
        self._api_key = api_key
        self._api_base_uri = api_base_uri
        self._api_version = api_version
        self._http_client_class = http_client_class
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._logging_level = logging_level

        self._http_client = http_client_class()
        self._api_requestor = ApiRequestor(http_client=self._http_client)
