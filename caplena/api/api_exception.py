import json
from typing import Any, ClassVar, Optional


class ApiException(Exception):
    """The API Exception that is thrown by the Caplena REST API.

    :param type: The type of the error returned.
    :param code: A short string that uniquely identifies the reason for this error.
        Useful for programmatic error handling. Should never be shown to your end users.
    :param message: A brief human-readable message providing more details about the error
        that has occurred. Please note that error messages might change and are therefore
        not suitable for programmatic error handling. Can be shown to end users.
    :param details: A lengthier human-readable explanation of the error. This property
        is intened for use by developers only and provides additional information on how
        this issue could be resolved. Should never be shown to your end users.
    :param help: URL that links to part of our developer documentation, allowing engineers
        to learn more about how to fix the given issue. Should never be shown
        to your end users.
    :param context: Additional context that might be present depending on the error type and code.
    """

    DEFAULT_MESSAGE: ClassVar[
        str
    ] = "An unknown error occurred. Please reach out to us at support@caplena.com."

    type: str
    """The type of the error returned."""

    code: str
    """A short string that uniquely identifies the reason for this error.
    Useful for programmatic error handling. Should never be shown to your end users.
    """

    message: str
    """A brief human-readable message providing more details about the error
    that has occurred. Please note that error messages might change and are therefore
    not suitable for programmatic error handling. Can be shown to end users.
    """

    details: Optional[str]
    """A lengthier human-readable explanation of the error. This property
    is intened for use by developers only and provides additional information on how
    this issue could be resolved. Should never be shown to your end users.
    """

    help: Optional[str]
    """URL that links to part of our developer documentation, allowing engineers
    to learn more about how to fix the given issue. Should never be shown
    to your end users.
    """

    context: Any
    """Additional context that might be present depending on the error type and code."""

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
