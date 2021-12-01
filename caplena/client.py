from .configuration import Configuration, Environment
from .controllers.projects_controller import ProjectsController


class Client:
    def projects(self):
        return ProjectsController(self.config)

    def __init__(
        self,
        api_key: str,
        *,
        timeout: int = 30,
        max_retries: int = 1,
        backoff_factor: int = 2,
        environment: Environment = Environment.PRODUCTION,
    ):
        self.config = Configuration(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            environment=environment,
        )
