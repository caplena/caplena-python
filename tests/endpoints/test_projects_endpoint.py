import unittest
from datetime import datetime

from caplena.controllers.projects_controller import ProjectsController
from caplena.endpoints.projects_endpoint import ProjectsEndpoint
from tests.common import common_config


class ProjectsEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.controller = ProjectsController(config=common_config)
        cls.endpoint = ProjectsEndpoint(controller=cls.controller)

    def test_creating_a_project_succeeds(self):
        project = self.endpoint.create(
            name="Project Name",
            tags=["my-tag"],
            language="en",
            translation_engine=None,
            columns=[
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
        )

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
