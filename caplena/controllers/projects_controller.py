from typing import Any, Dict, List, Optional

from caplena.api import ApiOrdering
from caplena.controllers.base_controller import BaseController
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter


class ProjectsController(BaseController):
    def create(
        self,
        *,
        name: str,
        language: str,
        columns: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
        translation_engine: Optional[str] = None,
    ):
        json = self.api.build_payload(
            name=name,
            language=language,
            columns=columns,
            tags=tags,
            translation_engine=translation_engine,
        )
        return self.post(
            path="/projects",
            json=json,
        )

    def retrieve(self, *, id: str):
        return self.get(
            path="/projects/{id}",
            path_params={"id": id},
        )

    def remove(self, *, id: str):
        return self.delete(
            path="/projects/{id}",
            path_params={"id": id},
        )

    def list(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        filter: Optional[ProjectsFilter] = None,
        order_by: ApiOrdering = ApiOrdering.desc("last_modified"),
    ):
        return self.get(
            path="/projects",
            query_params={
                "page": str(page),
                "limit": str(limit),
            },
            filter=filter,
            order_by=order_by,
        )

    def append_rows(
        self,
        *,
        id: str,
        rows: List[Dict[str, Any]],
    ):
        return self.post(
            path="/projects/{id}/rows/bulk",
            path_params={"id": id},
            json=rows,
            allowed_codes={202},
        )

    def append_row(
        self,
        *,
        id: str,
        columns: List[Dict[str, Any]],
    ):
        json = self.api.build_payload(columns=columns)
        return self.post(
            path="/projects/{id}/rows",
            path_params={"id": id},
            json=json,
        )

    def list_rows(
        self,
        *,
        id: str,
        page: int = 1,
        limit: int = 10,
        filter: Optional[RowsFilter] = None,
    ):
        return self.get(
            path="/projects/{id}/rows",
            path_params={"id": id},
            query_params={
                "page": str(page),
                "limit": str(limit),
            },
            filter=filter,
        )

    def retrieve_row(self, *, p_id: str, r_id: str):
        return self.get(
            path="/projects/{p_id}/rows/{r_id}",
            path_params={"p_id": p_id, "r_id": r_id},
        )
