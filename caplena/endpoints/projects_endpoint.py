from datetime import datetime
from typing import Any, Dict, List, Optional

from typing_extensions import Literal

from caplena.api import ApiOrdering
from caplena.endpoints.base_endpoint import BaseController, BaseObject, BaseResource
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter
from caplena.helpers import Helpers

# --- Controller --- #


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

        response = self.post(path="/projects", json=json)
        return self.build_response(response, resource=ProjectDetail)

    def retrieve(self, *, id: str):
        response = self.get(path="/projects/{id}", path_params={"id": id})
        return self.build_response(response, resource=ProjectDetail)

    def remove(self, *, id: str):
        self.delete(path="/projects/{id}", path_params={"id": id})

    def list(
        self,
        *,
        limit: int = 10,
        filter: Optional[ProjectsFilter] = None,
        order_by: ApiOrdering = ApiOrdering.desc("last_modified"),
    ):
        def fetcher(page: int):
            return self.get(
                path="/projects",
                query_params={
                    "page": str(page),
                    "limit": str(limit),
                },
                filter=filter,
                order_by=order_by,
            )

        return self.build_iterator(fetcher=fetcher, limit=limit, resource=ProjectList)

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


# --- Resources --- #


class ProjectDetail(BaseResource[ProjectsController]):
    class Column(BaseObject[ProjectsController]):
        __fields__ = {"ref", "name", "type"}

        ref: str
        name: str
        type: Literal["numerical", "boolean", "text", "any", "text_to_analyze"]

    class TextToAnalyze(Column):
        __fields__ = {"ref", "name", "type", "description"}

        type: Literal["text_to_analyze"]
        description: str

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]):
            # TODO: implement topics and metadata, add test
            return cls(
                ref=obj["ref"],
                name=obj["name"],
                type=obj["type"],
                description=obj["description"],
            )

    class Auxiliary(Column):
        type: Literal["numerical", "boolean", "text", "any"]

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]):
            return cls(
                ref=obj["ref"],
                name=obj["name"],
                type=obj["type"],
            )

    __fields__ = {
        "name",
        "owner",
        "tags",
        "upload_status",
        "language",
        "columns",
        "created",
        "last_modified",
        "translation_status",
        "translation_engine",
    }

    name: str
    owner: str
    tags: List[str]
    upload_status: Literal["pending", "in_progress", "succeeded", "failed"]
    # fmt: off
    language: Literal["af", "sq", "eu", "ca", "cs", "da", "nl", "en", "et", "fi",
                      "fr", "gl", "de", "el", "hu", "is", "it", "lb", "lt", "lv", "mk", "no",
                      "pl", "pt", "ro", "sr", "sk", "sl", "es", "sv", "tr"]  # fmt: on
    columns: List[TextToAnalyze]
    created: datetime
    last_modified: datetime
    translation_status: Optional[str]
    translation_engine: Optional[str]

    def delete(self):
        self._controller

    def append_row(self):
        pass

    def append_rows(self):
        pass

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]):
        columns = [cls.TextToAnalyze.parse_obj(column) if column['type'] == 'text_to_analyze' else cls.Auxiliary.parse_obj(column) for column in obj['columns']]
        created = Helpers.from_rfc3339_datetime(obj['created'])
        last_modified = Helpers.from_rfc3339_datetime(obj['last_modified'])

        return cls(
            id=obj['id'],
            name=obj['name'],
            owner=obj['owner'],
            tags=obj['tags'],
            upload_status=obj['upload_status'],
            language=obj['language'],
            columns=columns,
            created=created,
            last_modified=last_modified,
            translation_status=obj['translation_status'],
            translation_engine=obj['translation_engine'],
        )


class ProjectList(BaseResource[ProjectsController]):
    __fields__ = {
        "name",
        "owner",
        "tags",
        "upload_status",
        "language",
        "created",
        "last_modified",
        "translation_status",
        "translation_engine",
    }

    name: str
    owner: str
    tags: List[str]
    upload_status: Literal["pending", "in_progress", "succeeded", "failed"]
    # fmt: off
    language: Literal["af", "sq", "eu", "ca", "cs", "da", "nl", "en", "et", "fi",
                      "fr", "gl", "de", "el", "hu", "is", "it", "lb", "lt", "lv", "mk", "no",
                      "pl", "pt", "ro", "sr", "sk", "sl", "es", "sv", "tr"]  # fmt: on
    created: datetime
    last_modified: datetime
    translation_status: Optional[str]
    translation_engine: Optional[str]

    def delete(self):
        self._controller

    def append_row(self):
        pass

    def append_rows(self):
        pass

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]):
        created = Helpers.from_rfc3339_datetime(obj['created'])
        last_modified = Helpers.from_rfc3339_datetime(obj['last_modified'])

        return cls(
            id=obj['id'],
            name=obj['name'],
            owner=obj['owner'],
            tags=obj['tags'],
            upload_status=obj['upload_status'],
            language=obj['language'],
            created=created,
            last_modified=last_modified,
            translation_status=obj['translation_status'],
            translation_engine=obj['translation_engine'],
        )
