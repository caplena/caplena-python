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
        super().__init__(f"{type}[{code}]: {message}")

        self.type = type
        self.code = code
        self.message = message
        self.details = details
        self.help = help
        self.context = context
