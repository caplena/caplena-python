from datetime import datetime
from typing import Any, Dict, List, Optional

from typing_extensions import Literal

from caplena.controllers.projects_controller import ProjectsController
from caplena.helpers import Helpers
from caplena.resources.base.base_object import BaseObject
from caplena.resources.base.base_resource import BaseResource

# --- Child Resources --- #


class Column(BaseObject):
    __fields__ = {"ref", "name", "type"}

    ref: str
    name: str
    type: Literal["numerical", "boolean", "text", "any", "text_to_analyze"]


class Auxiliary(Column):
    type: Literal["numerical", "boolean", "text", "any"]

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]):
        return cls(
            ref=obj["ref"],
            name=obj["name"],
            type=obj["type"],
        )


class TextToAnalyze(Column):
    __fields__ = {"ref", "name", "type", "description"}

    type: Literal["text_to_analyze"]
    description: str

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]):
        return cls(
            ref=obj["ref"],
            name=obj["name"],
            type=obj["type"],
            description=obj["description"],
        )


# --- Root Resource --- #


class ProjectDetail(BaseResource[ProjectsController]):
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
    columns: List[Column]
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
    def parse_obj(cls, obj: Dict[str, Any], *, controller: ProjectsController):
        columns = [TextToAnalyze.parse_obj(column) if column['type'] == 'text_to_analyze' else Auxiliary.parse_obj(column) for column in obj['columns']]
        created = Helpers.from_rfc3339_datetime(obj['created'])
        last_modified = Helpers.from_rfc3339_datetime(obj['last_modified'])

        return cls(
            controller=controller,
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
