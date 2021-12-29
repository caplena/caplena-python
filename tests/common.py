from caplena.api.api_base_uri import ApiBaseUri
from caplena.configuration import Configuration
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging.logger import LoggingLevel

common_api_key = "4e5df2b6f642bf4f6b9eb36af587eef96dbc4b8e"

common_config = Configuration(
    api_key=common_api_key,
    http_client=RequestsHttpClient,
    api_base_uri=ApiBaseUri.LOCAL,
    logging_level=LoggingLevel.DEBUG,
)
