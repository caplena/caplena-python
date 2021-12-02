from caplena.controllers.base_controller import BaseController


class ProjectsController(BaseController):
    def list_projects(self):
        response = self.config.api_requestor.get(
            base_uri=self.config.api_base_uri,
            path="/projects",
            api_key=self.config.api_key,
            query_params={},
        )
        print(response)
