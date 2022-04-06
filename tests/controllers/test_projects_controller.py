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
            {"type": "boolean", "ref": "boolean_col", "name": "Some example boolean"},
            {"type": "text", "ref": "text_col", "name": "Some auxiliary text"},
            {"type": "date", "ref": "date_col", "name": "Some date time values."},
        ],
    }


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

    # ---- General Functionality ---- #

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

        self.assertEqual(5, len(project.columns))
        self.assertIsInstance(project.columns[0], ProjectDetail.TextToAnalyze)
        self.assertIsInstance(project.columns[1], ProjectDetail.Auxiliary)
        self.assertIsInstance(project.columns[2], ProjectDetail.Auxiliary)
        self.assertIsInstance(project.columns[3], ProjectDetail.Auxiliary)
        self.assertIsInstance(project.columns[4], ProjectDetail.Auxiliary)
        our_strengths = cast(ProjectDetail.TextToAnalyze, project.columns[0])
        customer_age = cast(ProjectDetail.Auxiliary, project.columns[1])
        boolean_col = cast(ProjectDetail.Auxiliary, project.columns[2])
        text_col = cast(ProjectDetail.Auxiliary, project.columns[3])
        date_col = cast(ProjectDetail.Auxiliary, project.columns[4])

        self.assertEqual("our_strengths", our_strengths.ref)
        self.assertEqual("Do you like us?", our_strengths.name)
        self.assertEqual("text_to_analyze", our_strengths.type)
        self.assertEqual("Please explain what our strengths are.", our_strengths.description)
        self.assertDictEqual(
            {
                "reviewed_count": 0,
                "learns_from": None,
            },
            our_strengths.metadata.dict(),
        )
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

        self.assertEqual("boolean_col", boolean_col.ref)
        self.assertEqual("Some example boolean", boolean_col.name)
        self.assertEqual("boolean", boolean_col.type)

        self.assertEqual("text_col", text_col.ref)
        self.assertEqual("Some auxiliary text", text_col.name)
        self.assertEqual("text", text_col.type)

        self.assertEqual("date_col", date_col.ref)
        self.assertEqual("Some date time values.", date_col.name)
        self.assertEqual("date", date_col.type)

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

    def test_updating_a_project_succeeds(self) -> None:
        project_to_learn_from = self.create_project()
        project = self.create_project()

        # test: updating properties succeeds
        expected_dict = project.dict()
        project.name = "MY SUPER NOVEL PROJECT NAME"
        project.tags = ["new", "tags", "are", "cool"]
        our_strengths: ProjectDetail.TextToAnalyze = project.columns[0]  # type: ignore
        our_strengths.name = "Do you still like us?"
        our_strengths.description = "Please explain."
        our_strengths.metadata.learns_from = self.controller.build(
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
        self.assertDictEqual(project.dict(), expected_dict)

        # test: resetting learns_from succeeds
        our_strengths: ProjectDetail.TextToAnalyze = project.columns[0]  # type: ignore
        our_strengths.metadata.learns_from = None
        project.save()
        expected_dict["columns"][0]["metadata"]["learns_from"] = None
        self.assertDictEqual(project.dict(), expected_dict)

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
            {"ref": "boolean_col", "value": False},
            {"ref": "text_col", "value": None},
            {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
        ]
        row = self.controller.append_row(id=project.id, columns=columns)

        self.assertIsInstance(row.id, str)
        self.assertIsInstance(row.created, datetime)
        self.assertIsInstance(row.last_modified, datetime)

        self.assertEqual(5, len(row.columns))
        self.assertIsInstance(row.columns[0], Row.TextToAnalyzeColumn)
        self.assertIsInstance(row.columns[1], Row.NumericalColumn)
        our_strengths = cast(Row.TextToAnalyzeColumn, row.columns[0])
        customer_age = cast(Row.NumericalColumn, row.columns[1])
        boolean_col = cast(Row.BooleanColumn, row.columns[2])
        text_col = cast(Row.TextColumn, row.columns[3])
        date_col = cast(Row.DateColumn, row.columns[4])

        self.assertEqual("our_strengths", our_strengths.ref)
        self.assertEqual("text_to_analyze", our_strengths.type)
        self.assertEqual("Some other text.", our_strengths.value)
        self.assertEqual(False, our_strengths.was_reviewed)
        self.assertEqual(None, our_strengths.source_language)
        self.assertEqual(None, our_strengths.translated_value)
        self.assertEqual(1, len(our_strengths.topics))
        topic = our_strengths.topics[0]
        self.assertRegex(topic.id, r"^cd_")
        self.assertEqual(topic.label, "Another Code Label")
        self.assertEqual(topic.category, "ANOTHER_CATEGORY")
        self.assertEqual(topic.code, 1)
        self.assertEqual(topic.sentiment_label, "")
        self.assertEqual(topic.sentiment, "neutral")

        self.assertEqual("customer_age", customer_age.ref)
        self.assertEqual("numerical", customer_age.type)
        self.assertEqual(None, customer_age.value)

        self.assertEqual("boolean_col", boolean_col.ref)
        self.assertEqual("boolean", boolean_col.type)
        self.assertEqual(False, boolean_col.value)

        self.assertEqual("text_col", text_col.ref)
        self.assertEqual("text", text_col.type)
        self.assertEqual("", text_col.value)

        self.assertEqual("date_col", date_col.ref)
        self.assertEqual("date", date_col.type)
        self.assertEqual(datetime(year=2020, month=10, day=10, hour=17), date_col.value)

    def test_listing_all_rows_succeeds(self) -> None:
        project = self.create_project()
        row1 = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": None},
                {"ref": "our_strengths", "value": "Some other text."},
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
            ],
        )
        row2 = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 12},
                {"ref": "our_strengths", "value": "This is my review. Very nice."},
                {"ref": "boolean_col", "value": True},
                {"ref": "text_col", "value": "samsung"},
                {"ref": "date_col", "value": datetime(year=2000, month=4, day=4, hour=4)},
            ],
        )
        rows = [row1.dict(), row2.dict()]
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
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
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

    def test_retrieving_a_row_succeeds(self) -> None:
        project = self.create_project()
        row = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 400},
                {"ref": "our_strengths", "value": "Some other text."},
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
            ],
        )
        retrieved = self.controller.retrieve_row(p_id=project.id, r_id=row.id)

        self.assertDictEqual(row.dict(), retrieved.dict())

    def test_removing_a_row_succeeds(self) -> None:
        project = self.create_project()

        old_num_rows = self.controller.list_rows(id=project.id, limit=1).count
        row = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 400},
                {"ref": "our_strengths", "value": "Some other text."},
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
            ],
        )
        interim_num_rows = self.controller.list_rows(id=project.id, limit=1).count
        self.controller.remove_row(p_id=project.id, r_id=row.id)
        new_num_rows = self.controller.list_rows(id=project.id, limit=1).count

        self.assertEqual(old_num_rows, new_num_rows)
        self.assertEqual(old_num_rows + 1, interim_num_rows)

    def test_updating_a_row_succeeds(self) -> None:
        project = self.create_project()
        row = self.controller.append_row(
            id=project.id,
            columns=[
                {"ref": "customer_age", "value": 400},
                {"ref": "our_strengths", "value": "Some other text."},
                {"ref": "boolean_col", "value": False},
                {"ref": "text_col", "value": "iphone"},
                {"ref": "date_col", "value": datetime(year=2020, month=10, day=10, hour=17)},
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
        expected_dict["columns"][0].update(
            {"value": "this is a new text value.", "was_reviewed": True}
        )
        # computed fields are updated when the value is changed, so don't compare them
        computed_fields = {"sentiment_overall", "translated_value", "topics"}
        for computed_field in computed_fields:
            expected_dict["columns"][0].pop(computed_field)
            row_dict["columns"][0].pop(computed_field)
        expected_dict["columns"][1].update({"value": 100000})
        self.assertDictEqual(row_dict, expected_dict)
