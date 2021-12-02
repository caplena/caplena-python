from typing import Type

from caplena.api import ApiBaseUri, ApiVersion
from caplena.configuration import Configuration
from caplena.controllers.projects_controller import ProjectsController
from caplena.http.http_client import HttpClient
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging import LoggingLevel


class Client:
    @property
    def projects(self):
        return ProjectsController(config=self.config)

    @property
    def config(self):
        return self._config

    def __init__(
        self,
        api_key: str,
        *,
        api_base_uri: ApiBaseUri = ApiBaseUri.PRODUCTION,
        api_version: ApiVersion = ApiVersion.DEFAULT,
        timeout: int = 30,
        max_retries: int = 0,
        backoff_factor: int = 2,
        http_client_class: Type[HttpClient] = RequestsHttpClient,
        logging_level: LoggingLevel = LoggingLevel.WARNING,
    ):
        self._config = Configuration(
            api_key=api_key,
            api_base_uri=api_base_uri,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            http_client_class=http_client_class,
            logging_level=logging_level,
        )
