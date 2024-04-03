from typing import Any, Dict


class DuplicatedTopicsError(Exception):
    """Exception that is thrown when there are two or more topics with identical names
    provided for TTACell.

    :param message: A brief human-readable message providing more details about the error
        that has occurred. Please note that error messages might change and are therefore
        not suitable for programmatic error handling.
    :param duplicates: A dict which specifies which topic ids had duplicates.
        Keys are topic ids and values are number of occurences.
    """

    def __init__(self, message: str, duplicates: Dict[str, int], *args: Any) -> None:
        self.message = message
        self.duplicates = duplicates
        super().__init__(message, *args)
