from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Literal

from caplena.api import ApiOrdering
from caplena.endpoints.base_endpoint import BaseController, BaseObject, BaseResource
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter
from caplena.helpers import Helpers
from caplena.http.http_response import HttpResponse
from caplena.iterator import Iterator

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
    ) -> "ProjectDetail":
        json = self.api.build_payload(
            name=name,
            language=language,
            columns=columns,
            tags=tags,
            translation_engine=translation_engine,
        )

        response = self.post(path="/projects", json=json)
        return self.build_response(response, resource=ProjectDetail)

    def retrieve(self, *, id: str) -> "ProjectDetail":
        response = self.get(path="/projects/{id}", path_params={"id": id})
        return self.build_response(response, resource=ProjectDetail)

    def remove(self, *, id: str) -> None:
        self.delete(path="/projects/{id}", path_params={"id": id})

    def list(
        self,
        *,
        limit: int = 10,
        filter: Optional[ProjectsFilter] = None,
        order_by: ApiOrdering = ApiOrdering.desc("last_modified"),
    ) -> "Iterator[ProjectList]":
        def fetcher(page: int) -> HttpResponse:
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
    ) -> "RowsAppend":
        response = self.post(
            path="/projects/{id}/rows/bulk",
            path_params={"id": id},
            json=rows,
            allowed_codes={202},
        )

        return self.build_response(response, resource=RowsAppend)

    def append_row(
        self,
        *,
        id: str,
        columns: List[Dict[str, Any]],
    ) -> "Row":
        json = self.api.build_payload(columns=columns)
        response = self.post(
            path="/projects/{id}/rows",
            path_params={"id": id},
            json=json,
        )

        return self.build_response(response, resource=Row)

    def list_rows(
        self,
        *,
        id: str,
        limit: int = 10,
        filter: Optional[RowsFilter] = None,
    ) -> "Iterator[Row]":
        def fetcher(page: int) -> HttpResponse:
            return self.get(
                path="/projects/{id}/rows",
                path_params={"id": id},
                query_params={
                    "page": str(page),
                    "limit": str(limit),
                },
                filter=filter,
            )

        return self.build_iterator(fetcher=fetcher, limit=limit, resource=Row)

    def retrieve_row(self, *, p_id: str, r_id: str) -> "Row":
        response = self.get(
            path="/projects/{p_id}/rows/{r_id}",
            path_params={"p_id": p_id, "r_id": r_id},
        )
        return self.build_response(response, resource=Row)


# --- Resources & Objects--- #


class ProjectDetail(BaseResource[ProjectsController]):
    class Column(BaseObject[ProjectsController]):
        __fields__ = {"ref", "name", "type"}

        ref: str
        name: str
        type: Literal["numerical", "boolean", "text", "date", "any", "text_to_analyze"]

    class TextToAnalyze(Column):
        class Topic(BaseResource[ProjectsController]):
            class Sentiment(BaseObject[ProjectsController]):
                __fields__ = {"code", "label"}

                code: int
                label: str

            __fields__ = {
                "label",
                "category",
                "color",
                "description",
                "sentiment_enabled",
                "sentiment_neutral",
                "sentiment_negative",
                "sentiment_positive",
            }

            label: str
            category: str
            color: str
            description: str
            sentiment_enabled: bool
            sentiment_neutral: Sentiment
            sentiment_negative: Sentiment
            sentiment_positive: Sentiment

            @classmethod
            def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail.TextToAnalyze.Topic":
                obj["sentiment_neutral"] = cls.Sentiment.parse_obj(obj["sentiment_neutral"])
                obj["sentiment_negative"] = cls.Sentiment.parse_obj(obj["sentiment_negative"])
                obj["sentiment_positive"] = cls.Sentiment.parse_obj(obj["sentiment_positive"])

                return super().parse_obj(obj)

        class Metadata(BaseObject[ProjectsController]):
            __fields__ = {"reviewed_count"}

            reviewed_count: int

        __fields__ = {"ref", "name", "type", "description", "topics", "metadata"}

        type: Literal["text_to_analyze"]
        description: str
        topics: List[Topic]
        metadata: Metadata

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail.TextToAnalyze":
            obj["topics"] = [cls.Topic.parse_obj(topic) for topic in obj["topics"]]
            obj["metadata"] = cls.Metadata.parse_obj(obj["metadata"])
            return super().parse_obj(obj)

    class Auxiliary(Column):
        type: Literal["numerical", "boolean", "text", "date", "any"]

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
                      "pl", "pt", "ro", "sr", "sk", "sl", "es", "sv", "tr"]
    # fmt: on
    columns: List[Column]
    created: datetime
    last_modified: datetime
    translation_status: Optional[str]
    translation_engine: Optional[str]

    def remove(self) -> None:
        self.controller.remove(id=self.id)

    def append_row(self, *, columns: List[Dict[str, Any]]) -> "Row":
        return self.controller.append_row(id=self.id, columns=columns)

    def append_rows(self, *, rows: List[Dict[str, Any]]) -> "RowsAppend":
        return self.controller.append_rows(id=self.id, rows=rows)

    def list_rows(
        self,
        *,
        limit: int = 10,
        filter: Optional[RowsFilter] = None,
    ) -> "Iterator[Row]":
        return self.controller.list_rows(id=self.id, limit=limit, filter=filter)

    def retrieve_row(self, *, id: str) -> "Row":
        return self.controller.retrieve_row(p_id=self.id, r_id=id)

    def refresh(self) -> None:
        project = self.controller.retrieve(id=self.id)
        self.refresh_from(attrs=project._attrs)

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail":
        obj["columns"] = [
            cls.TextToAnalyze.parse_obj(column)
            if column["type"] == "text_to_analyze"
            else cls.Auxiliary.parse_obj(column)
            for column in obj["columns"]
        ]
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)


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
                      "pl", "pt", "ro", "sr", "sk", "sl", "es", "sv", "tr"]
    # fmt: on
    created: datetime
    last_modified: datetime
    translation_status: Optional[str]
    translation_engine: Optional[str]

    def remove(self) -> None:
        self.controller.remove(id=self.id)

    def append_row(self, *, columns: List[Dict[str, Any]]) -> "Row":
        return self.controller.append_row(id=self.id, columns=columns)

    def append_rows(self, *, rows: List[Dict[str, Any]]) -> "RowsAppend":
        return self.controller.append_rows(id=self.id, rows=rows)

    def list_rows(
        self,
        *,
        limit: int = 10,
        filter: Optional[RowsFilter] = None,
    ) -> "Iterator[Row]":
        return self.controller.list_rows(id=self.id, limit=limit, filter=filter)

    def retrieve_row(self, *, id: str) -> "Row":
        return self.controller.retrieve_row(p_id=self.id, r_id=id)

    def refresh(self) -> None:
        project = self.controller.retrieve(id=self.id)
        self.refresh_from(attrs=project._attrs)

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectList":
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)


class RowsAppend(BaseObject[ProjectsController]):
    __fields__ = {"status", "queued_rows_count", "estimated_minutes"}

    status: Literal["pending"]
    queued_rows_count: int
    estimated_minutes: float


class Row(BaseResource[ProjectsController]):
    class Column(BaseObject[ProjectsController]):
        __fields__ = {"ref", "type", "value"}

        ref: str
        type: Literal["numerical", "boolean", "text", "date", "any", "text_to_analyze"]
        value: Union[float, bool, None, str, datetime]

    class NumericalColumn(Column):
        type: Literal["numerical"]
        value: Optional[float]

    class BooleanColumn(Column):
        type: Literal["boolean"]
        value: Optional[bool]

    class DateColumn(Column):
        type: Literal["date"]
        value: Optional[datetime]

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "Row.DateColumn":
            if obj["value"] is not None:
                obj["value"] = Helpers.from_rfc3339_datetime(obj["value"])

            return super().parse_obj(obj)

    class AnyColumn(Column):
        type: Literal["any"]
        value: None

    class TextColumn(Column):
        type: Literal["text"]
        value: str

    class TextToAnalyzeColumn(Column):
        class Topic(BaseObject[ProjectsController]):
            __fields__ = {"id", "label", "category", "code", "sentiment_label", "sentiment"}

            id: str
            label: str
            category: str
            code: int
            sentiment_label: str
            sentiment: Literal["neutral", "positive", "negative"]

        __fields__ = {
            "ref",
            "type",
            "value",
            "was_reviewed",
            "sentiment_overall",
            "source_language",
            "translated_value",
            "topics",
        }

        type: Literal["text_to_analyze"]
        value: str
        was_reviewed: Optional[bool]
        sentiment_overall: Optional[Literal["neutral", "positive", "negative"]]
        # fmt: off
        source_language: Optional[Literal["af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "ceb", "co", "cs", "cy", "da",
                                          "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fr", "fy", "ga", "gd", "gl",
                                          "gu", "ha", "haw", "hi", "hmn", "hr", "ht", "hu", "hy", "id", "ig", "is", "it", "iw",
                                          "he", "ja", "jw", "ka", "kk", "km", "kn", "ko", "ku", "ky", "la", "lb", "lo", "lt",
                                          "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "no", "ny",
                                          "pa", "pl", "ps", "pt", "ro", "ru", "sd", "si", "sk", "sl", "sm", "sn", "so", "sq",
                                          "sr", "st", "su", "sv", "sw", "ta", "te", "tg", "th", "tl", "tr", "tk", "uk", "ur",
                                          "uz", "vi", "xh", "yi", "yo", "zh", "zh-CN", "zh-TW", "zu"]]
        # fmt: on
        translated_value: Optional[str]
        topics: List[Topic]

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "Row.TextToAnalyzeColumn":
            obj["topics"] = [cls.Topic.parse_obj(topic) for topic in obj["topics"]]
            return super().parse_obj(obj)

    __fields__ = {"created", "last_modified", "columns"}

    created: datetime
    last_modified: datetime
    columns: List[Column]

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "Row":
        type_to_column = {
            "numerical": cls.NumericalColumn,
            "boolean": cls.BooleanColumn,
            "date": cls.DateColumn,
            "any": cls.AnyColumn,
            "text": cls.TextColumn,
            "text_to_analyze": cls.TextToAnalyzeColumn,
        }
        obj["columns"] = [
            type_to_column[column["type"]].parse_obj(column) for column in obj["columns"]
        ]
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)
