import unittest
from datetime import datetime, timedelta, timezone

from caplena.helpers import Helpers


class HelperTests(unittest.TestCase):
    def test_user_agent_succeeds(self) -> None:
        user_agent = Helpers.get_user_agent(identifier="requests")
        self.assertRegex(user_agent, r"requests/0\.0\.\d python/3\.\d\.\d")

    def test_from_rfc3339_datetime_succeeds(self) -> None:
        dates = [
            "2023-12-30",
            "2023-12-30T15:00:28",
            "2023-12-30T23:12:58.637000",
            "2023-12-30T23:12:58.798000Z",
            "2023-12-30T23:12:58.798000-04:00",
            "2021-12-29T14:46:55.787Z",
            "2021-09-01T11:43:49.508Z",
            "2021-09-01T11:43:49.500+04:00",
            "2021-12-31T08:43:49.444-07:00",
        ]
        expected = [
            datetime(2023, 12, 30).timestamp(),
            datetime(2023, 12, 30, 15, 00, 28).timestamp(),
            datetime(2023, 12, 30, 23, 12, 58, 637000).timestamp(),
            datetime(2023, 12, 30, 23, 12, 58, 798000, tzinfo=timezone.utc).timestamp(),
            datetime(
                2023, 12, 30, 23, 12, 58, 798000, tzinfo=timezone(timedelta(hours=-4))
            ).timestamp(),
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
            datetime(2021, 5, 30),
            datetime(2021, 5, 15, 8),
            datetime(2021, 5, 4, 12, 59),
            datetime(2021, 9, 25, 23, 59, 42),
            datetime(2021, 12, 29, 14, 46, 55, 456000),
            datetime(2021, 12, 29, 14, 46, 55, 787000, tzinfo=timezone.utc),
            datetime(2021, 9, 1, 11, 43, 49, 508000, tzinfo=timezone.utc),
            datetime(2021, 9, 1, 11, 43, 49, 500000, tzinfo=timezone(timedelta(hours=4))),
            datetime(2021, 12, 31, 8, 43, 49, 444000, tzinfo=timezone(timedelta(hours=-7))),
        ]
        expected = [
            "2021-05-30T00:00:00.000",
            "2021-05-15T08:00:00.000",
            "2021-05-04T12:59:00.000",
            "2021-09-25T23:59:42.000",
            "2021-12-29T14:46:55.456",
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
