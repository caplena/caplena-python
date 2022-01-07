import unittest
from datetime import datetime, timedelta, timezone

from caplena.helpers import Helpers


class HelperTests(unittest.TestCase):
    def test_user_agent_succeeds(self) -> None:
        user_agent = Helpers.get_user_agent(identifier="requests")
        self.assertRegex(user_agent, r"requests/0\.0\.\d python/3\.\d\.\d")

    def test_from_rfc3339_datetime_succeeds(self) -> None:
        dates = [
            "2021-12-29T14:46:55.787Z",
            "2021-09-01T11:43:49.508Z",
            "2021-09-01T11:43:49.500+04:00",
            "2021-12-31T08:43:49.444-07:00",
        ]
        expected = [
            datetime(2021, 12, 29, 14, 46, 55, 787000, tzinfo=timezone.utc).timestamp(),
            datetime(2021, 9, 1, 11, 43, 49, 508000, tzinfo=timezone.utc).timestamp(),
            datetime(
                2021, 9, 1, 11, 43, 49, 500000, tzinfo=timezone(timedelta(hours=4))
            ).timestamp(),
            datetime(
                2021, 12, 31, 8, 43, 49, 444000, tzinfo=timezone(timedelta(hours=-7))
            ).timestamp(),
        ]

        self.assertListEqual(
            expected, [Helpers.from_rfc3339_datetime(date).timestamp() for date in dates]
        )

    def test_to_rfc3339_datetime_succeeds(self) -> None:
        dates = [
            datetime(2021, 12, 29, 14, 46, 55, 787000, tzinfo=timezone.utc),
            datetime(2021, 9, 1, 11, 43, 49, 508000, tzinfo=timezone.utc),
            datetime(2021, 9, 1, 11, 43, 49, 500000, tzinfo=timezone(timedelta(hours=4))),
            datetime(2021, 12, 31, 8, 43, 49, 444000, tzinfo=timezone(timedelta(hours=-7))),
        ]
        expected = [
            "2021-12-29T14:46:55.787Z",
            "2021-09-01T11:43:49.508Z",
            "2021-09-01T11:43:49.500+04:00",
            "2021-12-31T08:43:49.444-07:00",
        ]

        self.assertListEqual(expected, [Helpers.to_rfc3339_datetime(date) for date in dates])

    def test_escaping_filter_string_succeeds(self) -> None:
        unescaped = [
            "abc cdef \\ \n ghj xyz",
            "th:is;is;just,a,ve:ry;lo:ng;tag",
            "just\\some\\\nmany\\\\\\backslashes\\n",
        ]
        escaped = [
            "abc cdef \\\\ \n ghj xyz",
            "th\\:is\\;is\\;just\\,a\\,ve\\:ry\\;lo\\:ng\\;tag",
            "just\\\\some\\\\\nmany\\\\\\\\\\\\backslashes\\\\n",
        ]

        self.assertListEqual(escaped, [Helpers.build_escaped_filter_str(un) for un in unescaped])
