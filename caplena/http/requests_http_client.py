from typing import Any, Dict, List, Optional, Union

import requests
from requests.sessions import Session

from caplena.http.http_client import HttpClient, HttpMethod, HttpRetry
from caplena.http.http_response import HttpResponse


class RequestsHttpClient(HttpClient):
    @property
    def identifier(self) -> str:
        return f"requests({requests.__version__})"

    def __init__(
        self,
        *,
        timeout: int = HttpClient.DEFAULT_TIMEOUT,
        retry: HttpRetry = HttpClient.DEFAULT_RETRY,
        session: Optional[Session] = None,
    ):
        super().__init__(timeout=timeout, retry=retry)
        self.session = session if session is not None else Session()

    def request_raw(
        self,
        uri: str,
        *,
        method: HttpMethod,
        timeout: int,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> HttpResponse:
        response = self.session.request(
            url=uri,
            method=method.method,
            json=json,
            headers=headers,
            timeout=timeout,
        )

        # note: we only support utf-8 encodings
        if response.encoding != "utf-8":
            raise ValueError(
                f"Received a response with an unsupported encoding scheme (encoding='{response.encoding}')."
            )

        self.logger.debug(
            f"Received response from server (status_code=${response.status_code}, text={response.text})"
        )
        return HttpResponse(
            status_code=response.status_code,
            reason=response.reason,
            text=response.text,
            headers=dict(response.headers),
        )
