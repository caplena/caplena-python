import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Union

from cachetools.func import ttl_cache
from typing_extensions import Literal, Self

from caplena.api import ApiOrdering
from caplena.constants import LIST_PAGINATION_LIMIT, NOT_SET
from caplena.endpoints.base_endpoint import BaseController, BaseObject, BaseResource
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter
from caplena.helpers import Helpers
from caplena.http.http_response import HttpResponse
from caplena.iterator import CaplenaIterator
from caplena.list import CaplenaList

# --- Controller --- #
TTL_STATUS_CACHE_EXPIRE = 10


class ProjectsController(BaseController):
    """The projects controller, encapsulating all project actions.

    :param config: The configuration object that a particular controller should use.
    """

    def create(
        self,
        *,
        name: str,
        language: str,
        columns: List[Dict[str, Any]],
        tags: Optional[List[str]] = NOT_SET,
        translation_engine: Optional[str] = NOT_SET,
        anonymize_pii: Optional[Dict[str, List[str]]] = NOT_SET,
    ) -> "ProjectDetail":
        """Creates a new project.

        :param name: Project name, as displayed in the user interface.
        :param language: Base language for this project.
        :param columns: Columns of a project define its schema. In a sense, every project column corresponds to
            exactly one column in an Excel sheet. The four column types numerical, date, boolean and text are
            auxiliary columns, meaning that they won't be analyzed, but they can be used to visualize your results.
            Please note that for columns of type `numerical`, its integer values must be between `-(2^53-1)` and
            `2^53-1`. For bigger numbers, please use a column of type `text`.
        :param tags: Tags assigned to this project. If omitted, no tags are assigned.
        :param translation_engine: Translation engine used to translate rows into the base language of this project.
            If omitted, no translation will be performed.
        :param anonymize_pii: settings to use for anonymization, visit the developer docs for more information.
        :raises caplena.api.ApiException: An API exception.
        """
        json = self.api.build_payload(
            name=name,
            language=language,
            columns=columns,
            tags=tags,
            translation_engine=translation_engine,
            anonymize_pii=anonymize_pii,
        )

        response = self.post(path="/projects", json=json)
        return self.build_response(response, resource=ProjectDetail)

    def retrieve(self, *, id: str) -> "ProjectDetail":
        """Retrieves a project you have previously created.

        :param id: The project identifier.
        :raises caplena.api.ApiException: An API exception.
        """
        response = self.get(path="/projects/{id}", path_params={"id": id})
        return self.build_response(response, resource=ProjectDetail)

    def remove(self, *, id: str) -> None:
        """Removes a previously created project.

        :param id: The project identifier.
        :raises caplena.api.ApiException: An API exception.
        """
        self.delete(path="/projects/{id}", path_params={"id": id})

    def list(
        self,
        *,
        order_by: ApiOrdering = ApiOrdering.desc("last_modified"),
        limit: Optional[int] = None,
        filter: Optional[ProjectsFilter] = None,
    ) -> "CaplenaIterator[ListedProject]":
        """Returns an iterator of all projects you have previously created. By default, the projects are returned
        in sorted order, with the most recently modified project appearing first.

        :param order_by: Column on which the results should be ordered on. Defaults to :code:`desc:last_modified`.
        :type order_by: ApiOrdering
        :param limit: Number of results returned per page. If unspecified, will return all results.
        :param filter: Filters to apply to this request. If omitted, no filters are applied.
        :raises caplena.api.ApiException: An API exception.
        """

        def fetcher(page: int) -> HttpResponse:
            return self.get(
                path="/projects",
                query_params={
                    "page": str(page),
                    "limit": str(LIST_PAGINATION_LIMIT),
                },
                filter=filter,
                order_by=order_by,
            )

        return self.build_iterator(fetcher=fetcher, limit=limit, resource=ListedProject)

    def update(
        self,
        *,
        id: str,
        name: Optional[str] = NOT_SET,
        columns: Optional[List[Dict[str, Any]]] = NOT_SET,
        tags: Optional[List[str]] = NOT_SET,
    ) -> "ProjectDetail":
        """Updates a project you have previously created.

        :param id: The project identifier.
        :param name: Project name, as displayed in the user interface.
        :param columns: Columns of a project.
        :param tags: Tags assigned to this project.
        :raises caplena.api.ApiException: An API exception.
        """
        json = self.api.build_payload(
            name=name,
            tags=tags,
            columns=columns,
        )

        response = self.patch(path="/projects/{id}", path_params={"id": id}, json=json)
        return self.build_response(response, resource=ProjectDetail)

    def append_rows(
        self,
        *,
        id: str,
        rows: List[Dict[str, Any]],
    ) -> "RowsAppend":
        """Appends multiple rows to a previously created project. It is possible to append a
        maximum of 20 rows in a single request.

        :param id: The project identifier.
        :param rows: The rows to append to the specified project.
        :raises caplena.api.ApiException: An API exception.
        """
        response = self.post(
            path="/projects/{id}/rows/bulk",
            path_params={"id": id},
            json=rows,
            allowed_codes={202},
        )

        return self.build_response(response, resource=RowsAppend)

    @ttl_cache(ttl=TTL_STATUS_CACHE_EXPIRE)
    def get_append_status(
        self, *, project_id: str, task_id: Optional[Union[uuid.UUID, str]] = None
    ) -> "RowsAppendStatus":
        """Checks statuses of all upload tasks for requested project
        or only requested upload task if its ID is provided

        Note: We keep the status of upload tasks only for the 7 days. After that time task info won't be available.

        :param project_id: (Optional) The project identifier. If it's missing, all tasks statuses of the project are
         returned.
        :param task_id: Task id which status will be checked
        :raises caplena.api.ApiException: An API exception.
        :raises ValueError: when task_id is not proper UUID or uuid in a string
        """
        params = {"project_id": project_id}
        if task_id and not isinstance(task_id, uuid.UUID):
            try:
                task_id = uuid.UUID(task_id)
            except (AttributeError, ValueError) as exc:
                raise ValueError("task_id must be UUID or uuid in a string") from exc
        url = "/projects/{project_id}/rows/bulk"
        if task_id:
            url = f"{url}/{task_id}"
            params["task_id"] = str(task_id)

        response = self.get(
            path=url,
            path_params=params,
            allowed_codes={200},
        )
        return self.build_response(response, resource=RowsAppendStatus)

    def append_row(
        self,
        *,
        id: str,
        columns: List[Dict[str, Any]],
    ) -> "Row":
        """Appends a single row to a previously created project.

        :param id: The project identifier.
        :param columns: The columns for the new row.
        :raises caplena.api.ApiException: An API exception.
        """
        json = self.api.build_payload(columns=columns)
        response = self.post(
            path="/projects/{id}/rows",
            path_params={"id": id},
            json=json,
        )

        return self.build_response(response, resource=Row, metadata={"project": id})

    def list_rows(
        self,
        *,
        id: str,
        limit: Optional[int] = None,
        filter: Optional[RowsFilter] = None,
    ) -> "CaplenaIterator[Row]":
        """Returns a list of all rows you have previously created for this project. The rows are returned in
        sorted order, with the least recently added row appearing first.

        :param id: The project identifier.
        :param limit: Number of results returned per page. If unspecified, will return all results.
        :param filter: Filters to apply to this request. If omitted, no filters are applied.
        :raises caplena.api.ApiException: An API exception.
        """

        def fetcher(page: int) -> HttpResponse:
            return self.get(
                path="/projects/{id}/rows",
                path_params={"id": id},
                query_params={
                    "page": str(page),
                    "limit": str(LIST_PAGINATION_LIMIT),
                },
                filter=filter,
            )

        return self.build_iterator(
            fetcher=fetcher, limit=limit, resource=Row, metadata={"project": id}
        )

    def retrieve_row(self, *, p_id: str, r_id: str) -> "Row":
        """Retrieves a row for a project you have previously created.

        :param p_id: The project identifier.
        :param r_id: The row identifier.
        :raises caplena.api.ApiException: An API exception.
        """
        response = self.get(
            path="/projects/{p_id}/rows/{r_id}",
            path_params={"p_id": p_id, "r_id": r_id},
        )
        return self.build_response(response, resource=Row, metadata={"project": id})

    def remove_row(self, *, p_id: str, r_id: str) -> None:
        """Removes a previously created row.

        :param p_id: The project identifier.
        :param r_id: The row identifier.
        :raises caplena.api.ApiException: An API exception.
        """
        self.delete(path="/projects/{p_id}/rows/{r_id}", path_params={"p_id": p_id, "r_id": r_id})

    def update_row(
        self,
        *,
        p_id: str,
        r_id: str,
        columns: List[Dict[str, Any]],
    ) -> "Row":
        """Updates a row you have previously created.

        :param p_id: The project identifier.
        :param r_id: The row identifier.
        :param columns: Columns for this row.
        :raises caplena.api.ApiException: An API exception.
        """
        json = self.api.build_payload(columns=columns)

        response = self.patch(
            path="/projects/{p_id}/rows/{r_id}", path_params={"p_id": p_id, "r_id": r_id}, json=json
        )
        return self.build_response(response, resource=Row, metadata={"project": id})


# --- Resources & Objects--- #


class OperationsProtocol(Protocol):
    # controller: ProjectsController
    @property
    def controller(self) -> ProjectsController:
        ...

    @property
    def id(self) -> str:
        ...

    def _refresh_from(self, *, attrs: Dict[str, Any]) -> None:
        ...

    def modified_dict(self) -> Any:
        ...


class RowOperationsMixin(OperationsProtocol, Protocol):
    def list_rows(
        self,
        *,
        limit: Optional[int] = None,
        filter: Optional[RowsFilter] = None,
    ) -> "CaplenaIterator[Row]":
        """Returns a list of all rows you have previously created for this project. The rows are returned in
        sorted order, with the least recently added row appearing first.

        :param limit: Number of results returned per page.
        :param filter: Filters to apply to this request. If omitted, no filters are applied.
        :raises caplena.api.ApiException: An API exception.
        """
        return self.controller.list_rows(id=self.id, limit=limit, filter=filter)

    def retrieve_row(self, *, id: str) -> "Row":
        """Retrieves a previously created row for this project.

        :param id: The row identifier.
        :raises caplena.api.ApiException: An API exception.
        """
        return self.controller.retrieve_row(p_id=self.id, r_id=id)

    def append_row(self, *, columns: List[Dict[str, Any]]) -> "Row":
        """Appends a single row to this project.

        :param columns: The columns for the new row.
        :raises caplena.api.ApiException: An API exception.
        """
        return self.controller.append_row(id=self.id, columns=columns)

    def append_rows(self, *, rows: List[Dict[str, Any]]) -> "RowsAppend":
        """Appends multiple rows to this project. It is possible to append a
        maximum of 20 rows in a single request.

        :param rows: The rows to append to the specified project.
        :raises caplena.api.ApiException: An API exception.
        """
        return self.controller.append_rows(id=self.id, rows=rows)

    def get_append_status(
        self, *, task_id: Optional[Union[uuid.UUID, str]] = None
    ) -> "RowsAppendStatus":
        """Checks statuses of all upload tasks for requested project
        or only requested upload task if its ID is provided

        Note: We keep the status of upload tasks only for the 7 days. After that time task info won't be available.

        :param project_id: The project identifier.
        :param task_id: Task id which status will be checked
        :raises caplena.api.ApiException: An API exception.
        :raises ValueError: when task_id is not proper UUID or uuid in a string
        """
        return self.controller.get_append_status(project_id=self.id, task_id=task_id)


class BaseProjectOperationsMixin(OperationsProtocol, Protocol):
    def remove(self) -> None:
        """Removes this project.

        :raises caplena.api.ApiException: An API exception.
        """
        self.controller.remove(id=self.id)

    def refresh(self) -> None:
        """Refreshes the properties of this project.

        :raises caplena.api.ApiException: An API exception.
        """
        project = self.controller.retrieve(id=self.id)
        self._refresh_from(attrs=project._attrs)

    def save(self) -> None:
        """Saves the unpersisted properties of this project.

        :raises caplena.api.ApiException: An API exception.
        """
        modified_dict = self.modified_dict()
        if modified_dict != NOT_SET:
            project = self.controller.update(id=self.id, **modified_dict)
            self._refresh_from(attrs=project._attrs)


class ProjectDetail(
    BaseResource[ProjectsController], BaseProjectOperationsMixin, RowOperationsMixin
):
    """The project detail resource."""

    class Column(BaseObject[ProjectsController]):
        __fields__ = {"ref", "name", "type"}
        __mutable__ = {"name"}

        ref: str
        """Human-readable identifier for this column. The reference field
        is immutable and is unique among all columns within the same project.
        """

        name: str
        """Human-readable name for this column."""

        type: Literal["numerical", "boolean", "text", "date", "any", "text_to_analyze"]
        """Type of this column."""

        def modified_dict(self) -> Any:
            modified: Any = super().modified_dict()
            if modified != NOT_SET:
                modified["ref"] = self.ref
                modified["type"] = self.type

            return modified

        def __repr__(self) -> str:
            return f"ProjectColumn(ref={self.ref}, type={self.type}, name={self.name})"

    class TextToAnalyze(Column):
        class Topic(BaseResource[ProjectsController]):
            class Sentiment(BaseObject[ProjectsController]):
                __fields__ = {"code", "label"}

                code: int
                """Code for this topic sentiment."""

                label: str
                """Label for this topic sentiment."""

                def __repr__(self) -> str:
                    return f"TopicSentiment(code={self.code}, label={self.label})"

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
            """Label for this topic."""

            category: str
            """Category for this topic"""

            color: str
            """Color for this topic."""

            description: str
            """Description for this topic."""

            sentiment_enabled: bool
            """If enabled, Caplena will assign the topic with a corresponding sentiment."""

            sentiment_neutral: Sentiment
            """Neutral topic sentiment."""

            sentiment_negative: Sentiment
            """Negative topic sentiment."""

            sentiment_positive: Sentiment
            """Positive topic sentiment."""

            def __repr__(self) -> str:
                return (
                    f"{self.__class__.__name__}(label={self.label}, category={self.category}, "
                    f"sentiment_enabled={self.sentiment_enabled})"
                )

            @classmethod
            def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail.TextToAnalyze.Topic":
                obj["sentiment_neutral"] = cls.Sentiment.parse_obj(obj["sentiment_neutral"])
                obj["sentiment_negative"] = cls.Sentiment.parse_obj(obj["sentiment_negative"])
                obj["sentiment_positive"] = cls.Sentiment.parse_obj(obj["sentiment_positive"])

                return super().parse_obj(obj)

        class Metadata(BaseObject[ProjectsController]):
            class LearnsForm(BaseObject[ProjectsController]):
                __fields__ = {"project", "ref"}
                __mutable__ = {"project", "ref"}

                project: str
                """Base project that this column learns from."""

                ref: str
                """Column identifier that this column learns from."""

            __fields__ = {
                "reviewed_count",
                "learns_from",
            }
            __mutable__ = {"learns_from"}

            reviewed_count: int
            """Number of reviewed rows for this column."""

            learns_from: Optional[LearnsForm]
            """Base column that this column learns from."""

        __fields__ = {"ref", "name", "type", "description", "topics", "metadata"}
        __mutable__ = {"name", "description"}

        type: Literal["text_to_analyze"]
        """Type of this column."""

        description: Optional[str] = ""
        """Column description displayed for this column."""

        topics: CaplenaList[Topic]
        """List of topics associated with this column."""

        metadata: Metadata
        """Metadata associated with this column."""

        def __repr__(self) -> str:
            return f"ProjectColumn(ref={self.ref}, type={self.type}, name={self.name}, topics={self.topics.__repr__()})"

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail.TextToAnalyze":
            obj["topics"] = CaplenaList(
                values=[cls.Topic.parse_obj(topic) for topic in obj["topics"]]
            )
            obj["metadata"] = cls.Metadata.parse_obj(obj["metadata"])
            return super().parse_obj(obj)

    class Auxiliary(Column):
        type: Literal["numerical", "boolean", "text", "date", "any"]
        """Type of this column."""

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
    __mutable__ = {"name", "tags"}

    name: str
    """Name of this project."""

    owner: str
    """Identifier of the user that owns this project."""

    tags: List[str]
    """Tags associated with this project."""

    upload_status: Literal["pending", "in_progress", "succeeded", "failed"]
    """Current upload status of this project."""

    language: str
    """Base language for this project as an ISO-639-1 Code"""

    columns: CaplenaList[Column]
    """Columns for this projects."""

    created: datetime
    """Timestamp at which the project was created."""

    last_modified: datetime
    """Timestamp at which the project was last updated."""

    translation_status: Optional[str]
    """Current translation status for this project."""

    translation_engine: Optional[str]
    """Translation engine used for translating :code:`text_to_analyze` columns."""

    anonymize_pii: Optional[Dict[str, List[str]]]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, columns={self.columns.__repr__()})"

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "ProjectDetail":
        obj["columns"] = CaplenaList(
            values=[
                cls.TextToAnalyze.parse_obj(column)
                if column["type"] == "text_to_analyze"
                else cls.Auxiliary.parse_obj(column)
                for column in obj["columns"]
            ]
        )
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)


class ListedProject(
    BaseResource[ProjectsController], BaseProjectOperationsMixin, RowOperationsMixin
):
    """The project list resource."""

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
    __mutable__ = {"name", "tags"}

    name: str
    """Name of this project."""

    owner: str
    """Identifier of the user that owns this project."""

    tags: List[str]
    """Tags associated with this project."""

    upload_status: Literal["pending", "in_progress", "succeeded", "failed"]
    """Current upload status of this project."""

    language: str
    """Base language for this project as an ISO-639-1 Code"""

    created: datetime
    """Timestamp at which the project was created."""

    last_modified: datetime
    """Timestamp at which the project was last updated."""

    translation_status: Optional[str]
    """Current translation status for this project."""

    translation_engine: Optional[str]
    """Translation engine used for translating :code:`text_to_analyze` columns."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "ListedProject":
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)


class RowsAppend(BaseObject[ProjectsController]):
    """The bulk row create response object."""

    class RowsAppendResult(BaseObject[ProjectsController]):
        __fields__ = {"id"}

        id: str
        """The identifier of the row that was appended."""

    __fields__ = {"status", "task_id", "queued_rows_count", "estimated_minutes", "results"}

    status: Literal["pending"]
    """Status of the bulk append operation."""

    task_id: str
    """Task ID of the bulk append operation."""

    queued_rows_count: int
    """Number of rows that were queued for appending."""

    estimated_minutes: float
    """Estimation in minutes about how long this bulk operation will approximately take."""

    results: CaplenaList[RowsAppendResult]
    """The results of the bulk append operation."""

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "RowsAppend":
        obj["results"] = CaplenaList(
            values=[cls.RowsAppendResult.parse_obj(res) for res in obj["results"]]
        )
        return super().parse_obj(obj)


class RowsAppendStatus(BaseObject[ProjectsController]):
    """Status of requested task and its subtasks"""

    class MeerkatSubTaskStatus(BaseObject[ProjectsController]):
        """Subtask and its sub-subtasks status"""

        __fields__ = {"id", "status", "subtasks"}

        id: uuid.UUID
        """ID of the subtask"""

        status: Optional[Literal["in_progress", "succeeded", "failed", "timed_out"]]
        """Status of the subtask"""

        subtasks: Optional[List[Self]]
        """subtasks of the task"""

    __fields__ = {"status", "tasks"}

    status: Literal["in_progress", "succeeded", "failed", "timed_out"]
    """Status of requested upload task"""

    tasks: Optional[List[MeerkatSubTaskStatus]]
    """tasks of the project"""


class Row(BaseResource[ProjectsController]):
    """The Row resource."""

    class Column(BaseObject[ProjectsController]):
        __fields__ = {"ref", "type", "value"}
        __mutable__ = {"value"}

        ref: str
        """Human-readable identifier for this column."""

        type: Literal["numerical", "boolean", "text", "date", "any", "text_to_analyze"]
        """Type of this column."""

        value: Union[int, float, bool, None, str, datetime]
        """Value assigned to this column."""

        def __repr__(self) -> str:
            return f"RowColumn(ref={self.ref}, type={self.type}, value={self.value})"

        def modified_dict(self) -> Any:
            modified: Any = super().modified_dict()
            if modified != NOT_SET:
                modified["ref"] = self.ref

            return modified

    class NumericalColumn(Column):
        type: Literal["numerical"]
        """Type of this column."""

        value: Optional[Union[int, float]]
        """Numerical value assigned to this column."""

    class BooleanColumn(Column):
        type: Literal["boolean"]
        """Type of this column."""

        value: Optional[bool]
        """Boolean value assigned to this column."""

    class DateColumn(Column):
        type: Literal["date"]
        """Type of this column."""

        value: Optional[datetime]
        """ISO 8601 datetime or date value assigned to this column."""

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "Row.DateColumn":
            if obj["value"] is not None:
                obj["value"] = Helpers.from_rfc3339_datetime(obj["value"])

            return super().parse_obj(obj)

    class AnyColumn(Column):
        type: Literal["any"]
        """Type of this column."""

        value: None
        """Any value assigned to this column."""

    class TextColumn(Column):
        type: Literal["text"]
        """Type of this column."""

        value: str
        """Text value assigned to this column."""

    class TextToAnalyzeColumn(Column):
        class Topic(BaseObject[ProjectsController]):
            __fields__ = {"id", "label", "category", "code", "sentiment_label", "sentiment"}
            __mutable__ = {"sentiment"}

            id: str
            """Unique identifier for this topic."""

            label: str
            """Label for this topic."""

            category: str
            """Category for this topic."""

            code: int
            """Code for the inferred topic sentiment. If sentiment is disabled, the neutral
            topic sentiment :code:`code` will be used."""

            sentiment_label: str
            """Label for the inferred topic sentiment. If sentiment is disabled, the neutral
            topic sentiment :code:`label` will be used."""

            sentiment: Literal["neutral", "positive", "negative", "any"]
            """Inferred sentiment for this column value."""

            def __repr__(self) -> str:
                return f"{self.__class__.__name__}(label={self.label}, category={self.category}, sentiment={self.sentiment})"

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
        __mutable__ = {"value", "was_reviewed", "topics"}

        type: Literal["text_to_analyze"]
        """Type of this column."""

        value: str
        """Text value assigned to this column."""

        was_reviewed: Optional[bool]
        """Indicates whether the row value for this column has been reviewed."""

        sentiment_overall: Optional[Literal["neutral", "positive", "negative"]]
        """Inferred overall sentiment for this column."""

        source_language: Optional[str]
        """Source language of this value as an ISO-639-1 Code (https://cloud.google.com/translate/docs/languages)."""

        translated_value: Optional[str]
        """Translated value if translation is enabled for this column."""

        topics: CaplenaList[Topic]
        """Topics matching the value of this column. If no topics match, an empty array is returned."""

        def __repr__(self) -> str:
            return (
                f"RowColumn(ref={self.ref}, type={self.type}, value={self.value[:50]}..., "
                f"sentiment_overall={self.sentiment_overall}, topics={self.topics.__repr__()})"
            )

        @classmethod
        def parse_obj(cls, obj: Dict[str, Any]) -> "Row.TextToAnalyzeColumn":
            obj["topics"] = CaplenaList(
                values=[cls.Topic.parse_obj(topic) for topic in obj["topics"]]
            )
            return super().parse_obj(obj)

    __fields__ = {"created", "last_modified", "columns"}

    created: datetime
    """Timestamp at which this row was created."""

    last_modified: datetime
    """Timestamp at which this row was last updated."""

    columns: CaplenaList[Column]
    """Columns for this row."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, columns={self.columns.__repr__()})"

    def remove(self) -> None:
        """Removes this row.

        :raises caplena.api.ApiException: An API exception.
        """
        self.controller.remove_row(p_id=self._metadata["project"], r_id=self.id)

    def refresh(self) -> None:
        """Refreshes the properties of this row.

        :raises caplena.api.ApiException: An API exception.
        """
        row = self.controller.retrieve_row(p_id=self._metadata["project"], r_id=self.id)
        self._refresh_from(attrs=row._attrs)

    def save(self) -> None:
        """Saves the unpersisted properties of this row.

        :raises caplena.api.ApiException: An API exception.
        """
        modified_dict = self.modified_dict()
        if modified_dict != NOT_SET:
            row = self.controller.update_row(
                p_id=self._metadata["project"],
                r_id=self.id,
                **modified_dict,
            )
            self._refresh_from(attrs=row._attrs)

    def retrieve_project(self) -> "ProjectDetail":
        """Retrieves the project that this row belongs to.

        :raises caplena.api.ApiException: An API exception.
        """
        return self.controller.retrieve(id=self._metadata["project"])

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
        obj["columns"] = CaplenaList(
            values=[type_to_column[column["type"]].parse_obj(column) for column in obj["columns"]]
        )
        obj["created"] = Helpers.from_rfc3339_datetime(obj["created"])
        obj["last_modified"] = Helpers.from_rfc3339_datetime(obj["last_modified"])

        return super().parse_obj(obj)
