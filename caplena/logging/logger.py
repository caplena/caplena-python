from enum import Enum


class LoggingLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger:
    @property
    def name(self):
        return self._name

    def __init__(self, name: str):
        self._name = name

    def log(self, msg: str, *, level: LoggingLevel, **extra: str) -> None:
        raise NotImplementedError("Logger subclasses must implement `log`.")

    def debug(self, msg: str, **extra: str):
        self.log(msg, level=LoggingLevel.DEBUG, **extra)

    def info(self, msg: str, **extra: str):
        self.log(msg, level=LoggingLevel.INFO, **extra)

    def warning(self, msg: str, **extra: str):
        self.log(msg, level=LoggingLevel.WARNING, **extra)

    def error(self, msg: str, **extra: str):
        self.log(msg, level=LoggingLevel.ERROR, **extra)
