from sys import stderr

from caplena.logging.logger import Logger, LoggingLevel


class DefaultLogger(Logger):
    def log(self, msg: str, *, level: LoggingLevel, **extra: str) -> None:
        msg = f"{level.name}[{self.name}]: {msg}"
        extra_str = [f"{tup[0]}={tup[1]}" for tup in extra.items()]
        if len(extra_str) > 0:
            msg += " (" + ", ".join(extra_str) + ")"

        if level.level >= self._logging_level.level:
            print(msg, file=stderr)
