from caplena.configuration import Configuration


class BaseController:
    @property
    def config(self):
        return self._config

    def __init__(self, *, config: Configuration):
        self._config = config
