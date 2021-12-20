from enum import Enum


class ApiBaseUri(Enum):
    LOCAL = "http://localhost:8000/v2"
    PRODUCTION = "https://api.caplena.com/v2"

    @property
    def url(self) -> str:
        return self.value
