from typing import Any, Dict

import requests_mock

from caplena.controllers import ProjectsController
from caplena.endpoints.projects_endpoint import ProjectDetail
from tests.common import common_config


def _aux_column_response(**overrides: Any) -> Dict[str, Any]:
    payload = {
        "ref": "new_date_col",
        "name": "New date column",
        "type": "date",
        "summary": None,
        "is_favorite": False,
        "is_sensitive": False,
        "smart_column_config_id": None,
    }
    payload.update(overrides)
    return payload


def _tta_column_response(**overrides: Any) -> Dict[str, Any]:
    payload = {
        "ref": "new_tta_col",
        "name": "New TTA column",
        "type": "text_to_analyze",
        "summary": None,
        "is_favorite": False,
        "is_sensitive": False,
        "smart_column_config_id": None,
        "description": "",
        "topics": None,
        "metadata": None,
    }
    payload.update(overrides)
    return payload


def test_create_empty_auxiliary_column_succeeds() -> None:
    controller = ProjectsController(config=common_config)
    api_base_uri = controller.config.api_base_uri.value
    project_id = "pj_test"

    with requests_mock.Mocker() as mocked:
        mocked.post(
            f"{api_base_uri}/projects/{project_id}/columns",
            json=_aux_column_response(),
            status_code=200,
        )
        column = controller.create_empty_column(
            id=project_id,
            name="New date column",
            column_type="date",
            ref="new_date_col",
        )

    assert isinstance(column, ProjectDetail.Auxiliary)
    assert column.ref == "new_date_col"
    assert column.name == "New date column"
    assert column.type == "date"
    assert mocked.last_request is not None
    assert mocked.last_request.json() == {
        "name": "New date column",
        "column_type": "date",
        "ref": "new_date_col",
    }


def test_create_empty_column_omits_ref_when_unset() -> None:
    controller = ProjectsController(config=common_config)
    api_base_uri = controller.config.api_base_uri.value
    project_id = "pj_test"

    with requests_mock.Mocker() as mocked:
        mocked.post(
            f"{api_base_uri}/projects/{project_id}/columns",
            json=_aux_column_response(ref="generated_ref"),
            status_code=200,
        )
        column = controller.create_empty_column(
            id=project_id,
            name="New date column",
            column_type="date",
        )

    assert column.ref == "generated_ref"
    assert mocked.last_request is not None
    assert mocked.last_request.json() == {
        "name": "New date column",
        "column_type": "date",
    }


def test_create_empty_tta_column_succeeds() -> None:
    controller = ProjectsController(config=common_config)
    api_base_uri = controller.config.api_base_uri.value
    project_id = "pj_test"

    with requests_mock.Mocker() as mocked:
        mocked.post(
            f"{api_base_uri}/projects/{project_id}/columns",
            json=_tta_column_response(),
            status_code=200,
        )
        column = controller.create_empty_column(
            id=project_id,
            name="New TTA column",
            column_type="text_to_analyze",
            ref="new_tta_col",
        )

    assert isinstance(column, ProjectDetail.TextToAnalyze)
    assert column.ref == "new_tta_col"
    assert column.name == "New TTA column"
    assert column.type == "text_to_analyze"
    assert column.description == ""
    assert len(column.topics) == 0
    assert column.metadata.reviewed_count == 0
    assert column.metadata.learns_from is None
