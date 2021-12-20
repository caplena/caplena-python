import json
from typing import Any, ClassVar, Optional


class ApiException(Exception):
    DEFAULT_MESSAGE: ClassVar[
        str
    ] = "An unknown error occurred. Please reach out to us at support@caplena.com."

    def __init__(
        self,
        *,
        type: str,
        code: str,
        message: str = DEFAULT_MESSAGE,
        details: Optional[str] = None,
        help: Optional[str] = None,
        context: Any = None,
    ):
        msg = f"{type}[{code}]: {message}"
        if details:
            msg += " " + details
        if help:
            msg += f" For more information, please visit {help}."
        if context:
            msg += f" (context={json.dumps(context)})"
        super().__init__(msg)

        self.type = type
        self.code = code
        self.message = message
        self.details = details
        self.help = help
        self.context = context
