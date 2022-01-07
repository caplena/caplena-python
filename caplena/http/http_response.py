import json
from typing import Any, Dict, Optional


class HttpResponse:
    _json: Optional[Dict[str, Any]]

    @property
    def json(self) -> Optional[Dict[str, Any]]:
        if hasattr(self, "_json"):
            return self._json
        elif self.text:
            self._json = json.loads(self.text)
            return self._json
        else:
            return None

    def __init__(
        self,
        *,
        status_code: int,
        reason: str,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.reason = reason
        self.text = text
        self.headers = headers

    def __str__(self) -> str:
        concat_text = (
            self.text[:50] + "..." if self.text and len(self.text) > 50 else str(self.text)
        )
        return f"HttpResponse(status_code={self.status_code}, reason='{self.reason}', text='{concat_text}')"
