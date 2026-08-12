import time
from uuid import uuid4

import requests_mock

from caplena.controllers import ProjectsController
from caplena.endpoints.projects_endpoint import TTL_STATUS_CACHE_EXPIRE
from tests.common import common_config


def test_limit_calls_to_backend_on_upload_task() -> None:
    controller = ProjectsController(config=common_config)
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

        time.sleep(TTL_STATUS_CACHE_EXPIRE)
        controller.get_append_status(project_id="1")
        assert pr1_mock.call_count == 2
        controller.get_append_status(project_id="1", task_id=task_uuid)
        assert task_mock.call_count == 1
