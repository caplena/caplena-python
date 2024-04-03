import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, cast
from uuid import uuid4

import pytest
import requests_mock
from typing_extensions import Protocol

from caplena.api.api_exception import ApiException
from caplena.controllers import ProjectsController
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter
from caplena.models.projects import (
    MultipleCellPayload,
    MultipleRowPayload,
    NonTTACell,
    NonTTAColumnDefinition,
    NonTTAColumnType,
    ProjectLanguage,
    ProjectSettings,
    RowPayload,
    TopicDefinition,
    TTACell,
    TTAColumnDefinition,
    TTAColumnType,
)
from caplena.resources import ProjectDetail, Row
from tests.common import common_config


class CreateProjectFunctionType(Protocol):
    def __call__(self, payload: Optional[Dict[str, Any]] = None) -> ProjectDetail: ...


def project_create_payload() -> Dict[str, Any]:
    return {
        "name": "Project Name",
        "tags": ["my-tag"],
        "language": "en",
        "translation_engine": None,
        "columns": [
            {
                "ref": "customer_age",
                "type": "numerical",
                "name": "Age of the customer",
            },
            {
                "ref": "our_strengths",
                "name": "Do you like us?",
                "type": "text_to_analyze",
                "topics": [
                    {
                        "label": "price",
                        "sentiment_enabled": True,
                        "category": "SERVICE",
                    },
                    {
                        "label": "network quality",
                        "sentiment_enabled": False,
                        "category": "SERVICE",
                    },
                ],
            },
            {"type": "boolean", "ref": "boolean_col", "name": "Some example boolean"},
            {"type": "text", "ref": "text_col", "name": "Some auxiliary text"},
            {"type": "date", "ref": "date_col", "name": "Some date time values."},
        ],
    }


def project_create_payload_model() -> Dict[str, Any]:
    return ProjectSettings(
        name="Project Name",
        tags=["my-tag"],
        language=ProjectLanguage.EN,
        translation_engine=None,
        columns=[
            NonTTAColumnDefinition(
                ref="customer_age",
                type=NonTTAColumnType.numerical,
                name="Age of the customer",
            ),
            TTAColumnDefinition(
                ref="our_strengths",
                name="Do you like us?",
                type=TTAColumnType.text_to_analyze,
                topics=[
                    TopicDefinition(
                        label="price",
                        sentiment_enabled=True,
                        category="SERVICE",
                    ),
                    TopicDefinition(
                        label="network quality",
                        sentiment_enabled=False,
                        category="SERVICE",
                    ),
                ],
            ),
            NonTTAColumnDefinition(
                type=NonTTAColumnType.boolean, ref="boolean_col", name="Some example boolean"
            ),
            NonTTAColumnDefinition(
                type=NonTTAColumnType.text, ref="text_col", name="Some auxiliary text"
            ),
            NonTTAColumnDefinition(
                type=NonTTAColumnType.date, ref="date_col", name="Some date time values."
            ),
            TTAColumnDefinition(
                ref="another_tta",
                name="Do you want more tta?",
                type=TTAColumnType.text_to_analyze,
                topics=[
                    TopicDefinition(
                        label="label1",
                        sentiment_enabled=True,
                        category="ANOTHER",
                    ),
                    TopicDefinition(
                        label="label2",
                        sentiment_enabled=False,
                        category="ANOTHER",
                    ),
                ],
            ),
        ],
    ).model_dump(exclude_none=True)


def project_rows_create_payload() -> List[Dict[str, Any]]:
    return [
        {
            "columns": [
                {"ref": "customer_age", "value": 120},
                {"ref": "our_strengths", "value": "This is nice."},
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
            ]
        },
        {
            "columns": [
                {"ref": "customer_age", "value": None},
                {"ref": "our_strengths", "value": "Some other text."},
                {"ref": "boolean_col", "value": True},
                {"ref": "text_col", "value": "oneplus"},
                {
                    "ref": "date_col",
                    "value": datetime(year=2022, month=3, day=31, hour=14, minute=14, second=14),
                },
            ]
        },
    ]


def project_rows_create_payload_model() -> List[Dict[str, Any]]:
    return MultipleRowPayload(  # type: ignore[no-any-return]
        rows=[
            RowPayload(
                columns=[
                    NonTTACell(ref="customer_age", value=120),
                    TTACell(ref="our_strengths", value="This is nice.", topics=[]),
                    NonTTACell(ref="boolean_col", value=False),
                    NonTTACell(ref="text_col", value="iphone"),
                    NonTTACell(
                        ref="date_col", value=datetime(year=2020, month=10, day=10, hour=17)
                    ),
                ]
            ),
            RowPayload(
                columns=[
                    NonTTACell(ref="customer_age", value=None),
                    TTACell(ref="our_strengths", value="Some other text.", topics=[]),
                    NonTTACell(ref="boolean_col", value=True),
                    NonTTACell(ref="text_col", value="oneplus"),
                    NonTTACell(
                        ref="date_col",
                        value=datetime(year=2022, month=3, day=31, hour=14, minute=14, second=14),
                    ),
                ]
            ),
        ]
    ).model_dump()["rows"]


def project_row_cells_payload() -> List[Dict[str, Any]]:
    return [
        {"ref": "customer_age", "value": None},
        {"ref": "our_strengths", "value": "Good price."},
        {"ref": "boolean_col", "value": False},
        {"ref": "text_col", "value": None},
        {
            "ref": "date_col",
            "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
        },
    ]


def project_row_cells_payload_model() -> List[Dict[str, Any]]:
    return MultipleCellPayload(  # type: ignore[no-any-return]
        cells=[
            NonTTACell(ref="customer_age", value=None),
            TTACell(ref="our_strengths", value="Good price.", topics=[], was_reviewed=False),
            NonTTACell(ref="boolean_col", value=False),
            NonTTACell(ref="text_col", value=None),
            NonTTACell(
                ref="date_col",
                value=datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            ),
        ]
    ).model_dump()["cells"]


@pytest.fixture(scope="session")
def controller() -> ProjectsController:
    controller = ProjectsController(config=common_config)
    return controller


@pytest.fixture(scope="function")
def create_project(
    controller: ProjectsController,
) -> Generator[CreateProjectFunctionType, None, None]:
    created_projects: List[str] = []

    def create(payload: Optional[Dict[str, Any]] = None) -> ProjectDetail:
        if payload is None:
            payload = project_create_payload()

        project = controller.create(**payload)
        created_projects.append(project.id)

        return project

    yield create

    for project_id in created_projects:
        try:
            controller.remove(id=project_id)
        except ApiException:
            print("Could not remove project with id:", project_id)


def test_creating_a_project_succeeds(create_project: CreateProjectFunctionType) -> None:
    project = create_project()

    assert isinstance(project.id, str)
    assert "Project Name" == project.name
    assert isinstance(project.owner, str)
    assert ["my-tag"] == project.tags
    assert "pending" == project.upload_status
    assert "en" == project.language
    assert project.translation_status is None
    assert project.translation_engine is None
    assert isinstance(project.created, datetime)
    assert isinstance(project.last_modified, datetime)

    assert 5 == len(project.columns)
    assert isinstance(project.columns[0], ProjectDetail.TextToAnalyze)
    assert isinstance(project.columns[1], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[2], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[3], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[4], ProjectDetail.Auxiliary)
    our_strengths = cast(ProjectDetail.TextToAnalyze, project.columns[0])  # type: ignore
    customer_age = cast(ProjectDetail.Auxiliary, project.columns[1])  # type: ignore
    boolean_col = cast(ProjectDetail.Auxiliary, project.columns[2])  # type: ignore
    text_col = cast(ProjectDetail.Auxiliary, project.columns[3])  # type: ignore
    date_col = cast(ProjectDetail.Auxiliary, project.columns[4])  # type: ignore

    # our strenghts column
    assert "our_strengths" == our_strengths.ref
    assert "Do you like us?" == our_strengths.name
    assert "text_to_analyze" == our_strengths.type
    assert "" == our_strengths.description
    assert {"reviewed_count": 0, "learns_from": None} == our_strengths.metadata.dict()
    assert 2 == len(our_strengths.topics)

    topic1, topic2 = our_strengths.topics[0], our_strengths.topics[1]
    assert re.search(r"^cd_", topic1.id)
    assert "price" == topic1.label
    assert "SERVICE" == topic1.category
    assert "" == topic1.color
    assert "" == topic1.description
    assert topic1.sentiment_enabled is True
    assert {"code": 0, "label": ""} == topic1.sentiment_neutral.dict()
    assert {"code": 1, "label": ""} == topic1.sentiment_positive.dict()
    assert {"code": 2, "label": ""} == topic1.sentiment_negative.dict()

    assert re.search(r"^cd_", topic2.id)
    assert "network quality" == topic2.label
    assert "SERVICE" == topic2.category
    assert "" == topic2.color
    assert "" == topic2.description
    assert topic2.sentiment_enabled is False
    assert {"code": 3, "label": ""} == topic2.sentiment_neutral.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_negative.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_positive.dict()

    # auxiliary columns
    assert "customer_age" == customer_age.ref
    assert "Age of the customer" == customer_age.name
    assert "numerical" == customer_age.type

    assert "boolean_col" == boolean_col.ref
    assert "Some example boolean" == boolean_col.name
    assert "boolean" == boolean_col.type

    assert "text_col" == text_col.ref
    assert "Some auxiliary text" == text_col.name
    assert "text" == text_col.type

    assert "date_col" == date_col.ref
    assert "Some date time values." == date_col.name
    assert "date" == date_col.type


def test_creating_a_project_with_settings_succeeds(
    create_project: CreateProjectFunctionType,
) -> None:
    project = create_project(project_create_payload_model())

    assert isinstance(project.id, str)
    assert "Project Name" == project.name
    assert isinstance(project.owner, str)
    assert ["my-tag"] == project.tags
    assert "pending" == project.upload_status
    assert "en" == project.language
    assert project.translation_status is None
    assert project.translation_engine is None
    assert isinstance(project.created, datetime)
    assert isinstance(project.last_modified, datetime)

    assert 6 == len(project.columns)
    assert isinstance(project.columns[0], ProjectDetail.TextToAnalyze)
    assert isinstance(project.columns[1], ProjectDetail.TextToAnalyze)
    assert isinstance(project.columns[2], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[3], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[4], ProjectDetail.Auxiliary)
    assert isinstance(project.columns[5], ProjectDetail.Auxiliary)
    our_strengths = cast(ProjectDetail.TextToAnalyze, project.columns[0])  # type: ignore
    another_tta = cast(ProjectDetail.TextToAnalyze, project.columns[1])  # type: ignore
    customer_age = cast(ProjectDetail.Auxiliary, project.columns[2])  # type: ignore
    boolean_col = cast(ProjectDetail.Auxiliary, project.columns[3])  # type: ignore
    text_col = cast(ProjectDetail.Auxiliary, project.columns[4])  # type: ignore
    date_col = cast(ProjectDetail.Auxiliary, project.columns[5])  # type: ignore

    # our strenghts column
    assert "our_strengths" == our_strengths.ref
    assert "Do you like us?" == our_strengths.name
    assert "text_to_analyze" == our_strengths.type
    assert "" == our_strengths.description
    assert {"reviewed_count": 0, "learns_from": None} == our_strengths.metadata.dict()
    assert 2 == len(our_strengths.topics)

    topic1, topic2 = our_strengths.topics[0], our_strengths.topics[1]
    assert re.search(r"^cd_", topic1.id)
    assert "price" == topic1.label
    assert "SERVICE" == topic1.category
    assert "" == topic1.color
    assert "" == topic1.description
    assert topic1.sentiment_enabled is True
    assert {"code": 0, "label": ""} == topic1.sentiment_neutral.dict()
    assert {"code": 1, "label": ""} == topic1.sentiment_positive.dict()
    assert {"code": 2, "label": ""} == topic1.sentiment_negative.dict()

    assert re.search(r"^cd_", topic2.id)
    assert "network quality" == topic2.label
    assert "SERVICE" == topic2.category
    assert "" == topic2.color
    assert "" == topic2.description
    assert topic2.sentiment_enabled is False
    assert {"code": 3, "label": ""} == topic2.sentiment_neutral.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_negative.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_positive.dict()

    # another tta column
    assert "another_tta" == another_tta.ref
    assert "Do you want more tta?" == another_tta.name
    assert "text_to_analyze" == another_tta.type
    assert "" == another_tta.description
    assert {"reviewed_count": 0, "learns_from": None} == another_tta.metadata.dict()
    assert 2 == len(another_tta.topics)

    topic1, topic2 = another_tta.topics[0], another_tta.topics[1]
    assert re.search(r"^cd_", topic1.id)
    assert "label1" == topic1.label
    assert "ANOTHER" == topic1.category
    assert "" == topic1.color
    assert "" == topic1.description
    assert topic1.sentiment_enabled is True
    assert {"code": 0, "label": ""} == topic1.sentiment_neutral.dict()
    assert {"code": 1, "label": ""} == topic1.sentiment_positive.dict()
    assert {"code": 2, "label": ""} == topic1.sentiment_negative.dict()

    assert re.search(r"^cd_", topic2.id)
    assert "label2" == topic2.label
    assert "ANOTHER" == topic2.category
    assert "" == topic2.color
    assert "" == topic2.description
    assert topic2.sentiment_enabled is False
    assert {"code": 3, "label": ""} == topic2.sentiment_neutral.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_negative.dict()
    assert {"code": -1, "label": ""} == topic2.sentiment_positive.dict()

    # auxiliary columns
    assert "customer_age" == customer_age.ref
    assert "Age of the customer" == customer_age.name
    assert "numerical" == customer_age.type

    assert "boolean_col" == boolean_col.ref
    assert "Some example boolean" == boolean_col.name
    assert "boolean" == boolean_col.type

    assert "text_col" == text_col.ref
    assert "Some auxiliary text" == text_col.name
    assert "text" == text_col.type

    assert "date_col" == date_col.ref
    assert "Some date time values." == date_col.name
    assert "date" == date_col.type


def test_retrieving_a_project_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    retrieved = controller.retrieve(id=project.id)

    assert project.dict() == retrieved.dict()


def test_removing_a_project_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    old_num_projects = controller.list(limit=1).count
    project = create_project()
    interim_num_projects = controller.list(limit=1).count
    controller.remove(id=project.id)
    new_num_projects = controller.list(limit=1).count

    assert old_num_projects == new_num_projects
    assert old_num_projects + 1 == interim_num_projects


def test_updating_a_project_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project_to_learn_from = create_project()
    project = create_project()

    # test: updating properties succeeds
    expected_dict = project.dict()
    project.name = "MY SUPER NOVEL PROJECT NAME"
    project.tags = ["new", "tags", "are", "cool"]
    our_strengths: ProjectDetail.TextToAnalyze = project.columns[0]  # type: ignore
    our_strengths.name = "Do you still like us?"
    our_strengths.description = "Please explain."
    our_strengths.metadata.learns_from = controller.build(
        ProjectDetail.TextToAnalyze.Metadata.LearnsForm,
        {"project": project_to_learn_from.id, "ref": project_to_learn_from.columns[0].ref},
    )
    project.columns[1].name = "COOL NAME"
    project.save()
    expected_dict["name"] = "MY SUPER NOVEL PROJECT NAME"
    expected_dict["tags"] = ["new", "tags", "are", "cool"]
    expected_dict["columns"][0].update(
        {"name": "Do you still like us?", "description": "Please explain."}
    )
    expected_dict["columns"][0]["metadata"].update(
        {
            "learns_from": {
                "project": project_to_learn_from.id,
                "ref": project_to_learn_from.columns[0].ref,
            }
        }
    )
    expected_dict["columns"][1]["name"] = "COOL NAME"
    assert project.dict() == expected_dict

    # test: resetting learns_from succeeds
    our_strengths: ProjectDetail.TextToAnalyze = project.columns[0]  # type: ignore
    our_strengths.metadata.learns_from = None
    project.save()
    expected_dict["columns"][0]["metadata"]["learns_from"] = None

    # last modified is updated
    project_dict = project.dict()
    project_dict.pop("last_modified")
    expected_dict.pop("last_modified")
    assert project_dict == expected_dict


def test_listing_all_projects_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    projects = controller.list(limit=1)

    assert isinstance(projects.count, int)
    assert projects.count >= 0
    assert len(projects) == 1
    retrieved = (list(projects))[0]

    project_dict = project.dict()
    project_dict.pop("columns")
    assert project_dict == retrieved.dict()


def test_filtering_projects_succeeds(controller: ProjectsController) -> None:
    filt = ProjectsFilter.language("tr")
    projects = controller.list(filter=filt)

    assert 0 == len(projects)
    assert 0 == projects.count


@pytest.mark.parametrize(
    # "payload", [project_rows_create_payload(), project_rows_create_payload_model()]
    "payload",
    [project_rows_create_payload_model()],
)
def test_appending_multiple_rows_succeeds(
    controller: ProjectsController,
    create_project: CreateProjectFunctionType,
    payload: List[Dict[str, Any]],
) -> None:
    project = create_project()
    response = controller.append_rows(id=project.id, rows=payload)

    assert "pending" == response.status
    assert 2 == response.queued_rows_count
    assert 1.02 == response.estimated_minutes
    assert 2 == len(response.results)
    assert all([isinstance(row.id, str) for row in response.results])


def test_getting_status_of_multiple_rows_upload_task(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    row_1 = project.append_rows(rows=project_rows_create_payload())
    row_2 = project.append_rows(rows=project_rows_create_payload())

    all_tasks_status = controller.get_append_status(project_id=project.id)
    assert all_tasks_status.tasks is not None
    all_tasks_ids = [task["id"] for task in all_tasks_status.tasks]  # type: ignore[index]
    assert row_1.task_id in all_tasks_ids
    assert row_2.task_id in all_tasks_ids
    assert all_tasks_status.status in ["in_progress", "succeeded"]
    # As we do not re-play api responses in tests here we do not know if status is already finished or no
    assert len(all_tasks_status.dict()["tasks"]) == 2

    tasks_ids = [task["id"] for task in all_tasks_status.tasks]  # type: ignore[index]
    for task_id in tasks_ids:
        task_data = controller.get_append_status(project_id=project.id, task_id=task_id)
        assert task_data.status in ["in_progress", "succeeded"]


@pytest.mark.parametrize(
    "payload", [project_row_cells_payload(), project_row_cells_payload_model()]
)
def test_appending_single_row_succeeds(
    controller: ProjectsController,
    create_project: CreateProjectFunctionType,
    payload: List[Dict[str, Any]],
) -> None:
    project = create_project()
    row = controller.append_row(id=project.id, columns=payload)

    assert isinstance(row.id, str)
    assert isinstance(row.created, datetime)
    assert isinstance(row.last_modified, datetime)

    assert 5 == len(row.columns)
    assert isinstance(row.columns[0], Row.TextToAnalyzeColumn)
    assert isinstance(row.columns[1], Row.NumericalColumn)
    our_strengths = cast(Row.TextToAnalyzeColumn, row.columns[0])  # type: ignore
    customer_age = cast(Row.NumericalColumn, row.columns[1])  # type: ignore
    boolean_col = cast(Row.BooleanColumn, row.columns[2])
    text_col = cast(Row.TextColumn, row.columns[3])
    date_col = cast(Row.DateColumn, row.columns[4])

    assert "our_strengths" == our_strengths.ref
    assert "text_to_analyze" == our_strengths.type
    assert "Good price." == our_strengths.value
    assert our_strengths.was_reviewed is False
    assert our_strengths.source_language is None
    assert our_strengths.translated_value is None
    assert 1 == len(our_strengths.topics)
    topic = our_strengths.topics[0]
    assert re.search(r"^cd_", topic.id)
    assert topic.label == "price"
    assert topic.category == "SERVICE"
    assert topic.code == 1
    assert topic.sentiment_label == ""
    assert topic.sentiment == "positive"

    assert "customer_age" == customer_age.ref
    assert "numerical" == customer_age.type
    assert customer_age.value is None

    assert "boolean_col" == boolean_col.ref
    assert "boolean" == boolean_col.type
    assert boolean_col.value is False

    assert "text_col" == text_col.ref
    assert "text" == text_col.type
    assert "" == text_col.value

    assert "date_col" == date_col.ref
    assert "date" == date_col.type
    assert datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc) == date_col.value


def test_listing_all_rows_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    row1 = controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": None},
            {"ref": "our_strengths", "value": "Some other text."},
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": "iphone"},
            {
                "ref": "date_col",
                "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            },
        ],
    )
    row2 = controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": 12},
            {"ref": "our_strengths", "value": "This is my review. Very nice."},
            {"ref": "boolean_col", "value": True},
            {"ref": "text_col", "value": "samsung"},
            {
                "ref": "date_col",
                "value": datetime(year=2000, month=4, day=4, hour=4, tzinfo=timezone.utc),
            },
        ],
    )
    rows = [row1.dict(), row2.dict()]
    retrieved = controller.list_rows(id=project.id, limit=2)

    assert 2 == retrieved.count
    assert 2 == len(retrieved)

    retrieved_dict = [row.dict() for row in retrieved]
    assert rows == retrieved_dict


def test_filtering_rows_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": None},
            {"ref": "our_strengths", "value": "Some other text."},
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": "iphone"},
            {
                "ref": "date_col",
                "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            },
        ],
    )

    with_results = controller.list_rows(id=project.id)
    assert 1 == with_results.count

    filt = RowsFilter.Columns.text_to_analyze(ref="our_strengths", contains__i=["some"])
    filtered_results = controller.list_rows(id=project.id, filter=filt)
    assert 1 == filtered_results.count

    filt = RowsFilter.Columns.text_to_analyze(ref="our_strengths", was_reviewed=True)
    no_results = controller.list_rows(id=project.id, filter=filt)
    assert 0 == no_results.count


def test_retrieving_a_row_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    row = controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": 400},
            {"ref": "our_strengths", "value": "Some other text."},
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": "iphone"},
            {
                "ref": "date_col",
                "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            },
        ],
    )
    retrieved = controller.retrieve_row(p_id=project.id, r_id=row.id)

    assert row.dict() == retrieved.dict()
    assert row._metadata == {"project": project.id}


def test_removing_a_row_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()

    old_num_rows = controller.list_rows(id=project.id, limit=1).count
    row = controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": 400},
            {"ref": "our_strengths", "value": "Some other text."},
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": "iphone"},
            {
                "ref": "date_col",
                "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            },
        ],
    )
    interim_num_rows = controller.list_rows(id=project.id, limit=1).count
    controller.remove_row(p_id=project.id, r_id=row.id)
    new_num_rows = controller.list_rows(id=project.id, limit=1).count

    assert old_num_rows == new_num_rows
    assert old_num_rows + 1 == interim_num_rows


def test_updating_a_row_succeeds(
    controller: ProjectsController, create_project: CreateProjectFunctionType
) -> None:
    project = create_project()
    row = controller.append_row(
        id=project.id,
        columns=[
            {"ref": "customer_age", "value": 400},
            {"ref": "our_strengths", "value": "Some other text."},
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": "iphone"},
            {
                "ref": "date_col",
                "value": datetime(year=2020, month=10, day=10, hour=17, tzinfo=timezone.utc),
            },
        ],
    )
    expected_dict = row.dict()
    our_strengths: Row.TextToAnalyzeColumn = row.columns[0]  # type: ignore
    our_strengths.value = "this is a new text value."
    our_strengths.was_reviewed = True
    customer_age: Row.NumericalColumn = row.columns[1]  # type: ignore
    customer_age.value = 100000

    row.save()
    row_dict = row.dict()
    expected_dict["columns"][0].update({"value": "this is a new text value.", "was_reviewed": True})
    computed_row_fields = {"last_modified"}
    # computed fields are updated when the value is changed, so don't compare them
    for field in computed_row_fields:
        expected_dict.pop(field)
        row_dict.pop(field)
    computed_tta_column_fields = {"sentiment_overall", "translated_value", "topics"}
    for computed_field in computed_tta_column_fields:
        expected_dict["columns"][0].pop(computed_field)
        row_dict["columns"][0].pop(computed_field)
    expected_dict["columns"][1].update({"value": 100000})
    assert row_dict == expected_dict


def test_limit_calls_to_backend_on_upload_task(controller: ProjectsController) -> None:
    task_uuid = uuid4()
    api_base_uri = controller.config.api_base_uri.value
    with requests_mock.Mocker() as mocked_project_page:
        pr1_mock = mocked_project_page.get(
            f"{api_base_uri}/projects/1/rows/bulk", json={"tasks": [], "status": ""}
        )
        pr2_mock = mocked_project_page.get(
            f"{api_base_uri}/projects/2/rows/bulk", json={"tasks": [], "status": ""}
        )
        task_mock = mocked_project_page.get(
            f"{api_base_uri}/projects/1/rows/bulk/{task_uuid}",
            json={"tasks": [], "status": ""},
        )
        controller.get_append_status(project_id="1")
        assert pr1_mock.call_count == 1
        controller.get_append_status(project_id="1")
        controller.get_append_status(project_id="1")
        controller.get_append_status(project_id="1")
        assert pr1_mock.call_count == 1

        controller.get_append_status(project_id="2")
        assert pr2_mock.call_count == 1

        time.sleep(10)
        controller.get_append_status(project_id="1")
        assert pr1_mock.call_count == 2
        controller.get_append_status(project_id="1", task_id=task_uuid)
        assert task_mock.call_count == 1
