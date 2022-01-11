import unittest
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, cast

from caplena.api.api_exception import ApiException
from caplena.controllers import ProjectsController
from caplena.filters.projects_filter import ProjectsFilter, RowsFilter
from caplena.resources import ProjectDetail, Row
from tests.common import common_config


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
                "description": "Please explain what our strengths are.",
                "topics": [
                    {
                        "label": "Some Code Label",
                        "sentiment_enabled": False,
                        "category": "SOME_CATEGORY",
                    },
                    {
                        "label": "Another Code Label",
                        "sentiment_enabled": False,
                        "category": "ANOTHER_CATEGORY",
                    },
                ],
            },
        ],
    }


def project_rows_create_payload() -> List[Dict[str, Any]]:
    return [
        {
            "columns": [
                {"ref": "customer_age", "value": 120},
                {"ref": "our_strengths", "value": "This is nice."},
            ]
        },
        {
            "columns": [
                {"ref": "customer_age", "value": None},
                {"ref": "our_strengths", "value": "Some other text."},
            ]
        },
    ]


class ProjectsControllerTests(unittest.TestCase):
    controller: ClassVar[ProjectsController]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.controller = ProjectsController(config=common_config)

    def setUp(self) -> None:
        self.created_projects: List[str] = []

    def tearDown(self) -> None:
        for project_id in self.created_projects:
            try:
                self.controller.remove(id=project_id)
            except ApiException:
                print("Could not remove project with id:", project_id)

    def create_project(self, *, payload: Optional[Dict[str, Any]] = None) -> ProjectDetail:
        if payload is None:
            payload = project_create_payload()

        project = self.controller.create(**payload)
        self.created_projects.append(project.id)

        return project

    def test_creating_a_project_succeeds(self) -> None:
        project = self.create_project()

        self.assertIsInstance(project.id, str)
        self.assertEqual("Project Name", project.name)
        self.assertIsInstance(project.owner, str)
        self.assertListEqual(["my-tag"], project.tags)
        self.assertEqual("pending", project.upload_status)
        self.assertEqual("en", project.language)
        self.assertEqual(None, project.translation_status)
        self.assertEqual(None, project.translation_engine)
        self.assertIsInstance(project.created, datetime)
        self.assertIsInstance(project.last_modified, datetime)

        self.assertEqual(2, len(project.columns))
        self.assertIsInstance(project.columns[0], ProjectDetail.TextToAnalyze)
        self.assertIsInstance(project.columns[1], ProjectDetail.Auxiliary)
        our_strengths = cast(ProjectDetail.TextToAnalyze, project.columns[0])
        customer_age = cast(ProjectDetail.Auxiliary, project.columns[1])

        self.assertEqual("our_strengths", our_strengths.ref)
        self.assertEqual("Do you like us?", our_strengths.name)
        self.assertEqual("text_to_analyze", our_strengths.type)
        self.assertEqual("Please explain what our strengths are.", our_strengths.description)
        self.assertDictEqual({"reviewed_count": 0}, our_strengths.metadata.dict())
        self.assertEqual(2, len(our_strengths.topics))

        topic1, topic2 = our_strengths.topics[0], our_strengths.topics[1]
        self.assertRegex(topic1.id, r"^cd_")
        self.assertEqual("Some Code Label", topic1.label)
        self.assertEqual("SOME_CATEGORY", topic1.category)
        self.assertEqual("", topic1.color)
        self.assertEqual("", topic1.description)
        self.assertEqual(False, topic1.sentiment_enabled)
        self.assertDictEqual({"code": 0, "label": ""}, topic1.sentiment_neutral.dict())
        self.assertDictEqual({"code": -1, "label": ""}, topic1.sentiment_negative.dict())
        self.assertDictEqual({"code": -1, "label": ""}, topic1.sentiment_positive.dict())

        self.assertRegex(topic2.id, r"^cd_")
        self.assertEqual("Another Code Label", topic2.label)
        self.assertEqual("ANOTHER_CATEGORY", topic2.category)
        self.assertEqual("", topic2.color)
        self.assertEqual("", topic2.description)
        self.assertEqual(False, topic2.sentiment_enabled)
        self.assertDictEqual({"code": 1, "label": ""}, topic2.sentiment_neutral.dict())
        self.assertDictEqual({"code": -1, "label": ""}, topic2.sentiment_negative.dict())
        self.assertDictEqual({"code": -1, "label": ""}, topic2.sentiment_positive.dict())

        self.assertEqual("customer_age", customer_age.ref)
        self.assertEqual("Age of the customer", customer_age.name)
        self.assertEqual("numerical", customer_age.type)

    def test_retrieving_a_project_succeeds(self) -> None:
        project = self.create_project()
        retrieved = self.controller.retrieve(id=project.id)

        self.assertDictEqual(project.dict(), retrieved.dict())

    def test_removing_a_project_succeeds(self) -> None:
        old_num_projects = self.controller.list(limit=1).count
        project = self.create_project()
        interim_num_projects = self.controller.list(limit=1).count
        self.controller.remove(id=project.id)
        new_num_projects = self.controller.list(limit=1).count

        self.assertEqual(old_num_projects, new_num_projects)
        self.assertEqual(old_num_projects + 1, interim_num_projects)

    def test_listing_all_projects_succeeds(self) -> None:
        project = self.create_project()
        projects = self.controller.list(limit=1)

        self.assertIsInstance(projects.count, int)
        self.assertGreaterEqual(projects.count, 0)
        self.assertEqual(len(projects), 1)
        retrieved = (list(projects))[0]

        project_dict = project.dict()
        project_dict.pop("columns")
        self.assertDictEqual(project_dict, retrieved.dict())

    def test_filtering_projects_succeeds(self) -> None:
        filt = ProjectsFilter.language("tr")
        projects = self.controller.list(filter=filt)

        self.assertEqual(0, len(projects))
        self.assertEqual(0, projects.count)

    def test_appending_multiple_rows_succeeds(self) -> None:
        project = self.create_project()
        result = self.controller.append_rows(id=project.id, rows=project_rows_create_payload())

        self.assertEqual("pending", result.status)
        self.assertEqual(2, result.queued_rows_count)
        self.assertEqual(1.02, result.estimated_minutes)

    def test_appending_single_row_succeeds(self) -> None:
        project = self.create_project()
        columns: List[Dict[str, Any]] = [
            {"ref": "customer_age", "value": None},
            {"ref": "our_strengths", "value": "Some other text."},
        ]
        row = self.controller.append_row(id=project.id, columns=columns)

        self.assertIsInstance(row.id, str)
        self.assertIsInstance(row.created, datetime)
        self.assertIsInstance(row.last_modified, datetime)

        self.assertEqual(2, len(row.columns))
        self.assertIsInstance(row.columns[0], Row.TextToAnalyzeColumn)
        self.assertIsInstance(row.columns[1], Row.NumericalColumn)
        our_strengths = cast(Row.TextToAnalyzeColumn, row.columns[0])
        customer_age = cast(Row.NumericalColumn, row.columns[1])

        self.assertEqual("our_strengths", our_strengths.ref)
        self.assertEqual("text_to_analyze", our_strengths.type)
        self.assertEqual("Some other text.", our_strengths.value)
        self.assertEqual(False, our_strengths.was_reviewed)
        self.assertEqual(None, our_strengths.source_language)
        self.assertEqual(None, our_strengths.translated_value)
        self.assertEqual(1, len(our_strengths.topics))
        topic = our_strengths.topics[0]
        self.assertRegex(topic.id, r"^cd_")
        # TODO: what should be returned here?

        self.assertEqual("customer_age", customer_age.ref)
        self.assertEqual("numerical", customer_age.type)
        self.assertEqual(None, customer_age.value)

    def test_listing_all_rows_succeeds(self) -> None:
        project = self.create_project()
        row1 = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": None},
                {"ref": "our_strengths", "value": "Some other text."},
            ],
        )
        row2 = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 12},
                {"ref": "our_strengths", "value": "This is my review. Very nice."},
            ],
        )
        rows = [row2.dict(), row1.dict()]
        retrieved = self.controller.list_rows(id=project.id, limit=2)

        self.assertEqual(2, retrieved.count)
        self.assertEqual(2, len(retrieved))

        retrieved_dict = [row.dict() for row in retrieved]
        self.assertListEqual(rows, retrieved_dict)

    def test_filtering_rows_succeeds(self) -> None:
        project = self.create_project()
        self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": None},
                {"ref": "our_strengths", "value": "Some other text."},
            ],
        )

        with_results = self.controller.list_rows(id=project.id)
        self.assertEqual(1, with_results.count)

        filt = RowsFilter.Columns.text_to_analyze(ref="our_strengths", contains__i=["some"])
        filtered_results = self.controller.list_rows(id=project.id, filter=filt)
        self.assertEqual(1, filtered_results.count)

        filt = RowsFilter.Columns.text_to_analyze(ref="our_strengths", was_reviewed=True)
        no_results = self.controller.list_rows(id=project.id, filter=filt)
        self.assertEqual(0, no_results.count)

    def test_retreiving_a_row_succeeds(self) -> None:
        project = self.create_project()
        row = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 400},
                {"ref": "our_strengths", "value": "Some other text."},
            ],
        )
        retrieved = self.controller.retrieve_row(p_id=project.id, r_id=row.id)

        self.assertDictEqual(row.dict(), retrieved.dict())
