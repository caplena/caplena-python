from typing import Any, Dict, List, Optional

from caplena.controllers.projects_controller import ProjectsController
from caplena.endpoints.base_endpoint import BaseEndpoint
from caplena.resources.project_detail import ProjectDetail


class ProjectsEndpoint(BaseEndpoint[ProjectsController]):
    def create(
        self,
        *,
        name: str,
        language: str,
        columns: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        translation_engine: Optional[str] = None,
    ):
        response = self._controller.create(
            name=name,
            language=language,
            columns=columns,
            tags=tags,
            translation_engine=translation_engine,
        )

        return self.build_response(response, resource=ProjectDetail)
