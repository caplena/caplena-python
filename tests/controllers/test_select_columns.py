from typing import Any, Dict, List

import pytest
import requests_mock

from caplena.api import ApiVersion
from caplena.controllers import ProjectsController
from caplena.endpoints.projects_endpoint import ProjectDetail, Row
from caplena.filters.projects_filter import RowsFilter
from tests.common import common_config

PROJECT_ID = "pj_test"
ROW_ID = "ro_test"


@pytest.fixture
def controller() -> ProjectsController:
    return ProjectsController(config=common_config)


@pytest.fixture
def api_base_uri(controller: ProjectsController) -> str:
    return str(controller.config.api_base_uri.value)


def _select_column_response(**overrides: Any) -> Dict[str, Any]:
    payload = {
        "ref": "channel",
        "name": "Support channel",
        "type": "single_select",
        "summary": None,
        "is_favorite": False,
        "is_sensitive": False,
        "smart_column_config_id": None,
        "enum": ["Phone", "E-Mail"],
    }
    payload.update(overrides)
    return payload


def _project_response(columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": PROJECT_ID,
        "name": "Project Name",
        "owner": "us_test",
        "tags": [],
        "upload_status": "succeeded",
        "language": "en",
        "columns": columns,
        "created": "2026-09-18T10:00:00Z",
        "last_modified": "2026-09-18T10:00:00Z",
        "translation_status": None,
        "translation_engine": None,
    }


def _row_response(columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": ROW_ID,
        "upload_index": 0,
        "created": "2026-09-18T10:00:00Z",
        "last_modified": "2026-09-18T10:00:00Z",
        "columns": columns,
    }


def test_default_api_version_supports_select_columns() -> None:
    assert ApiVersion.VER_2026_09_18.version == "2026-09-18"
    assert common_config.api_version == ApiVersion.VER_2026_09_18


def test_retrieving_project_parses_select_columns(
    controller: ProjectsController, api_base_uri: str
) -> None:
    with requests_mock.Mocker() as mocked:
        mocked.get(
            f"{api_base_uri}/projects/{PROJECT_ID}",
            json=_project_response(
                [
                    _select_column_response(),
                    _select_column_response(
                        ref="topics_of_interest",
                        name="Topics of interest",
                        type="multi_select",
                        enum=["Pricing"],
                    ),
                    {
                        "ref": "text_col",
                        "name": "Some text",
                        "type": "text",
                        "summary": None,
                        "is_favorite": False,
                        "is_sensitive": False,
                        "smart_column_config_id": None,
                        "enum": None,
                    },
                ]
            ),
        )
        project = controller.retrieve(id=PROJECT_ID)

    single, multi, text = project.columns

    assert isinstance(single, ProjectDetail.Select)
    assert single.type == "single_select"
    assert single.enum == ["Phone", "E-Mail"]

    assert isinstance(multi, ProjectDetail.Select)
    assert multi.type == "multi_select"
    assert multi.enum == ["Pricing"]

    assert isinstance(text, ProjectDetail.Auxiliary)
    assert not isinstance(text, ProjectDetail.Select)

    assert mocked.last_request is not None
    assert mocked.last_request.headers["Caplena-API-Version"] == "2026-09-18"


def test_retrieving_row_parses_select_columns(
    controller: ProjectsController, api_base_uri: str
) -> None:
    with requests_mock.Mocker() as mocked:
        mocked.get(
            f"{api_base_uri}/projects/{PROJECT_ID}/rows/{ROW_ID}",
            json=_row_response(
                [
                    {"ref": "channel", "type": "single_select", "value": "E-Mail"},
                    {
                        "ref": "topics_of_interest",
                        "type": "multi_select",
                        "value": ["Pricing", "Support"],
                    },
                ]
            ),
        )
        row = controller.retrieve_row(p_id=PROJECT_ID, r_id=ROW_ID)

    single, multi = row.columns

    assert isinstance(single, Row.SingleSelectColumn)
    assert single.value == "E-Mail"

    assert isinstance(multi, Row.MultiSelectColumn)
    assert multi.value == ["Pricing", "Support"]


def test_retrieving_row_parses_empty_select_columns(
    controller: ProjectsController, api_base_uri: str
) -> None:
    with requests_mock.Mocker() as mocked:
        mocked.get(
            f"{api_base_uri}/projects/{PROJECT_ID}/rows/{ROW_ID}",
            json=_row_response(
                [
                    {"ref": "channel", "type": "single_select"},
                    {"ref": "topics_of_interest", "type": "multi_select"},
                ]
            ),
        )
        row = controller.retrieve_row(p_id=PROJECT_ID, r_id=ROW_ID)

    single, multi = row.columns

    assert single.value is None
    assert multi.value is None


def test_saving_modified_select_columns_sends_labels(
    controller: ProjectsController, api_base_uri: str
) -> None:
    columns: List[Dict[str, Any]] = [
        {"ref": "channel", "type": "single_select", "value": "E-Mail"},
        {"ref": "topics_of_interest", "type": "multi_select", "value": ["Pricing"]},
    ]

    with requests_mock.Mocker() as mocked:
        mocked.get(
            f"{api_base_uri}/projects/{PROJECT_ID}/rows/{ROW_ID}",
            json=_row_response(columns),
        )
        mocked.patch(
            f"{api_base_uri}/projects/{PROJECT_ID}/rows/{ROW_ID}",
            json=_row_response(columns),
        )
        row = controller.retrieve_row(p_id=PROJECT_ID, r_id=ROW_ID)
        row.columns[0].value = "Phone"
        row.columns[1].value = ["Pricing", "Support"]
        row.save()

        patch_request = mocked.request_history[-1]

    assert patch_request.method == "PATCH"
    assert patch_request.json() == {
        "columns": [
            {"ref": "channel", "value": "Phone"},
            {"ref": "topics_of_interest", "value": ["Pricing", "Support"]},
        ]
    }


@pytest.mark.parametrize(
    "filter, expected",
    [
        (
            RowsFilter.Columns.single_select(ref="channel", exact=["Phone", "E-Mail"]),
            "channel[single_select]:Phone,channel[single_select]:E-Mail",
        ),
        (
            RowsFilter.Columns.single_select(ref="channel", is_non_existent=True),
            "channel[single_select].is_non_existent:True",
        ),
        (
            RowsFilter.Columns.multi_select(ref="topics", contains="Pricing", is_empty=False),
            "topics[multi_select]:Pricing;topics[multi_select].is_empty:False",
        ),
        (
            # the separators of the filter grammar are escaped in a label
            RowsFilter.Columns.single_select(ref="channel", exact="Price: high, urgent"),
            r"channel[single_select]:Price\: high\, urgent",
        ),
    ],
    ids=["single_select_labels", "single_select_non_existent", "multi_select", "escaping"],
)
def test_select_filters_build_query_params(filter: RowsFilter, expected: str) -> None:
    assert filter.to_query_params() == {"columns": expected}
