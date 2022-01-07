from typing import Iterable, Type, Union

from caplena.api import ApiBaseUri, ApiVersion
from caplena.configuration import Configuration
from caplena.endpoints.projects_endpoint import ProjectsController
from caplena.http.http_client import HttpClient, HttpMethod, HttpRetry
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging.logger import LoggingLevel


class Client:
    @property
    def projects(self) -> ProjectsController:
        return self._projects_controller

    @property
    def config(self) -> Configuration:
        return self._config

    def __init__(
        self,
        api_key: str,
        *,
        api_base_uri: ApiBaseUri = ApiBaseUri.PRODUCTION,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        timeout: int = HttpClient.DEFAULT_TIMEOUT,
        max_retries: int = HttpRetry.DEFAULT_MAX_RETRIES,
        backoff_factor: float = HttpRetry.DEFAULT_BACKOFF_FACTOR,
        retry_status_codes: Iterable[int] = HttpRetry.DEFAULT_STATUS_CODES_TO_RETRY,
        retry_methods: Iterable[HttpMethod] = HttpRetry.DEFAULT_ALLOWED_METHOD,
        http_client: Union[Type[HttpClient], HttpClient] = RequestsHttpClient,
        logging_level: LoggingLevel = LoggingLevel.WARNING,
    ):
        self._config = Configuration(
            api_key=api_key,
            http_client=http_client,
            api_base_uri=api_base_uri,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            retry_status_codes=retry_status_codes,
            retry_methods=retry_methods,
            logging_level=logging_level,
        )

        self._projects_controller = ProjectsController(config=self._config)
