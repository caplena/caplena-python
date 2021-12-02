from typing import Any, Dict, Optional


class HttpResponse:
    def __init__(
        self,
        *,
        status_code: int,
        reason: str,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        pass

    def json(self) -> Dict[str, Any]:
        # TODO: implement json parsing
        return {}
