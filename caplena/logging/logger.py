from enum import Enum


class LoggingLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @property
    def level(self) -> int:
        return self.value


class Logger:
    @property
    def name(self) -> str:
        return self._name

    @property
    def logging_level(self) -> LoggingLevel:
        return self._logging_level

    def __init__(self, name: str, logging_level: LoggingLevel = LoggingLevel.WARNING):
        self._name = name
        self._logging_level = logging_level

    def log(self, msg: str, *, level: LoggingLevel, **extra: str) -> None:
        raise NotImplementedError("Logger subclasses must implement `log`.")

    def debug(self, msg: str, **extra: str) -> None:
        self.log(msg, level=LoggingLevel.DEBUG, **extra)

    def info(self, msg: str, **extra: str) -> None:
        self.log(msg, level=LoggingLevel.INFO, **extra)

    def warning(self, msg: str, **extra: str) -> None:
        self.log(msg, level=LoggingLevel.WARNING, **extra)

    def error(self, msg: str, **extra: str) -> None:
        self.log(msg, level=LoggingLevel.ERROR, **extra)
