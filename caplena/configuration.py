from enum import Enum


class Environment(Enum):
    PRODUCTION = 0
    LOCAL = 1


class Configuration:
    @property
    def api_key(self):
        return self._api_key

    @property
    def timeout(self):
        return self._timeout

    @property
    def max_retries(self):
        return self._max_retries

    @property
    def backoff_factor(self):
        return self._backoff_factor

    @property
    def environment(self):
        return self._environment

    def __init__(
        self,
        *,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 1,
        backoff_factor: int = 2,
        environment: Environment = Environment.PRODUCTION
    ):
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._environment = environment
