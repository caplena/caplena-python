import unittest

from caplena.configuration import Configuration
from caplena.controllers.projects_controller import ProjectsController


class ProjectsControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.config = Configuration(api_key="")
        cls.controller = ProjectsController(cls.config)

    def test_list_projects(self):
        assert 1 == 2
