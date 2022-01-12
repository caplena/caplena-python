from typing import Iterable, Type, Union

from caplena.api import ApiBaseUri, ApiVersion
from caplena.configuration import Configuration
from caplena.controllers import ProjectsController
from caplena.http.http_client import HttpClient, HttpMethod, HttpRetry
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging.logger import LoggingLevel


class Client:
    """Represents a client connection that connects to Caplena. This class is used
    to interact with the Caplena REST API.

    :param api_key: The API key to use for making requests.
    :param api_base_uri: The API Base URI to use, defaults to :code:`https://api.caplena.com/v2`.
    :type api_base_uri: ApiBaseUri
    :param api_version: The API Version to use, defaults to :code:`2022-01-01`.
    :type api_version: ApiVersion
    :param timeout: The maximum number of seconds before the request times out, defaults to :code:`120`.
    :param max_retries: The maximum number of times the request is retried before giving up, defaults to :code:`0`.
    :param backoff_factor: The backoff factor to apply between attempts, defaults to :code:`2`.
    :param retry_status_codes: A set of HTTP status codes that we should retry on, defaults to
        :code:`{408, 409, 413, 429, 500, 502, 503, 504}`.
    :param retry_methods: A set of HTTP methods that we should retry on, defaults to :code:`{GET, PUT, HEAD}`.
    :type retry_methods: Iterable[HttpMethod]
    :param http_client: The HTTP client class or instance to use for making requests, defaults to :code:`RequestsHttpClient`.
        If an HTTP class is given, the factory method :code:`build_http_client` is used to create an instance.
    :type http_client: Union[HttpClient, Type[HttpClient]]
    :param logging_level: The level of events to log out to console, defaults to :code:`WARNING`.
    :type logging_level: LoggingLevel
    """

    @property
    def projects(self) -> ProjectsController:
        """The projects controller, encapsulating all project actions."""
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
