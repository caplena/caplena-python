import unittest

from caplena.helpers import Helpers


class HelperTests(unittest.TestCase):
    def test_user_agent_succeeds(self):
        user_agent = Helpers.get_user_agent(identifier="requests")
        self.assertRegex(user_agent, r"requests/0\.0\.\d python/3\.\d\.\d")
