import unittest
from datetime import datetime, timezone
from typing import Any, ClassVar, List, Tuple

from caplena.api import ApiBaseUri, ApiFilter, ApiRequestor, ApiVersion, ZeroOrMany
from caplena.http.http_client import HttpClient
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging.default_logger import DefaultLogger
from caplena.logging.logger import Logger


class Pf(ApiFilter):
    @classmethod
    def created(
        cls,
        *,
        year: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
    ) -> "Pf":
        return cls.construct(
            name="created",
            filters={
                "year": year,
                "year.gt": year__gt,
                "year.lt": year__lt,
                "month": month,
                "day": day,
            },
        )

    @classmethod
    def last_modified(
        cls,
        *,
        gte: ZeroOrMany[datetime] = None,
        year: ZeroOrMany[int] = None,
        year__gt: ZeroOrMany[int] = None,
        year__lt: ZeroOrMany[int] = None,
        month: ZeroOrMany[int] = None,
        day: ZeroOrMany[int] = None,
    ) -> "Pf":
        return cls.construct(
            name="last_modified",
            filters={
                "gte": gte,
                "year": year,
                "year.gt": year__gt,
                "year.lt": year__lt,
                "month": month,
                "day": day,
            },
        )

    @classmethod
    def tags(cls, tag: ZeroOrMany[str]) -> "Pf":
        return cls.construct(
            name="tags",
            filters={
                cls.DEFAULT: tag,
            },
        )


class ApiVersionTests(unittest.TestCase):
    def test_api_version_string_for_default_fails(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "Cannot convert `DEFAULT` to a valid version string."
        ):
            ApiVersion.DEFAULT.version

    def test_api_version_string_succeeds(self) -> None:
        self.assertEqual("2022-01-01", ApiVersion.VER_2022_01_01.version)


class ApiRequestorTests(unittest.TestCase):
    http_client: ClassVar[HttpClient]
    logger: ClassVar[Logger]
    api_requestor: ClassVar[ApiRequestor]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.http_client = RequestsHttpClient()
        cls.logger = DefaultLogger(name="test-logger")
        cls.api_requestor = ApiRequestor(http_client=cls.http_client, logger=cls.logger)

    def assertAbsoluteUriListEqual(
        self,
        expected: List[str],
        actual: List[Tuple[Any, str, Any, Any]],
    ) -> None:
        results = [
            self.api_requestor.build_uri(
                base_uri=a[0],
                path=a[1],
                path_params=a[2],
                query_params=a[3],
            )
            for a in actual
        ]
        self.assertListEqual(expected, results)

    def test_building_absolute_uri_fails(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "Path requires `hello` parameter, but none is given."
        ):
            self.api_requestor.build_uri(
                base_uri="https://abc.xyz/", path="/{hello}/there/", path_params=None
            )

        with self.assertRaisesRegex(
            ValueError, "Path requires `other` parameter, but none is given."
        ):
            self.api_requestor.build_uri(
                base_uri="https://abc.xyz/",
                path="{param}/hello/{other}/missing/{yeah}",
                path_params={"param": "good_param"},
            )

        with self.assertRaisesRegex(
            ValueError,
            "Path specifies an invalid path parameter. Parameter name must not be empty.",
        ):
            self.api_requestor.build_uri(base_uri="https://abc.xyz/", path="/{}", path_params=None)

    def test_building_absolute_uri_from_api_base_succeeds(self) -> None:
        absolute_uris = [
            (ApiBaseUri.LOCAL, "", None, None),
            (ApiBaseUri.LOCAL, "/{id}", {"id": "12"}, None),
            (ApiBaseUri.PRODUCTION, "/some/simple/path", None, None),
            (
                ApiBaseUri.PRODUCTION,
                "/some/more/{complex}/id/{path}",
                {"complex": "abc_123", "path": "_292_"},
                {"query_a": "1234", "query_b": "abcdefghi_klmo", "12": "34"},
            ),
        ]
        expected = [
            "http://localhost:8000/v2",
            "http://localhost:8000/v2/12",
            "https://api.caplena.com/v2/some/simple/path",
            "https://api.caplena.com/v2/some/more/abc_123/id/_292_?query_a=1234&query_b=abcdefghi_klmo&12=34",
        ]

        self.assertAbsoluteUriListEqual(expected, absolute_uris)

    def test_building_absolute_uri_from_string_succeeds(self) -> None:
        absolute_uris = [
            ("http://abc.de", "", None, None),
            ("https://abc.xyz", "/{id}", {"id": "some_param"}, None),
            (
                "https://caplena.com",
                "/some/simple/path",
                None,
                {"query_a": "1234", "query_b": "abcdefghi_klmo", "12": "34"},
            ),
            (
                "https://nest.js",
                "/some/more/{complex}/id/{path}",
                {"complex": "abc_123", "path": "_292_"},
                None,
            ),
        ]
        expected = [
            "http://abc.de",
            "https://abc.xyz/some_param",
            "https://caplena.com/some/simple/path?query_a=1234&query_b=abcdefghi_klmo&12=34",
            "https://nest.js/some/more/abc_123/id/_292_",
        ]

        self.assertAbsoluteUriListEqual(expected, absolute_uris)

    def test_building_absolute_uri_from_path_parameters_succeeds(self) -> None:
        absolute_uris = [
            ("https://abc.xyz", "/hello/there/", None, None),
            ("https://abc.xyz", "{param}/hello/there/", {"param": "good_param"}, None),
            ("https://abc.xyz", "/{xyz}", {"xyz": "other_param"}, None),
            ("https://abc.xyz/", "/{abc}/", {"abc": "double_slash"}, None),
        ]
        expected = [
            "https://abc.xyz/hello/there/",
            "https://abc.xyz/good_param/hello/there/",
            "https://abc.xyz/other_param",
            "https://abc.xyz/double_slash/",
        ]

        self.assertAbsoluteUriListEqual(expected, absolute_uris)

    def test_building_absolute_uri_from_query_parameters_succeeds(self) -> None:
        absolute_uris = [
            ("https://abc.xyz", "/hello/there/", None, None),
            (
                "https://abc.xyz",
                "param/hello/there/",
                None,
                {"q1": "abc_def", "q2": "123", "4": "5"},
            ),
            ("https://abc.xyz", "/xyz", None, {"_123": "Interesting.Choice/ Ok!"}),
            ("https://abc.xyz/", "/abc_", None, {" ! not sure ": "we can even have spaces"}),
        ]
        expected = [
            "https://abc.xyz/hello/there/",
            "https://abc.xyz/param/hello/there/?q1=abc_def&q2=123&4=5",
            "https://abc.xyz/xyz?_123=Interesting.Choice%2F+Ok%21",
            "https://abc.xyz/abc_?+%21+not+sure+=we+can+even+have+spaces",
        ]

        self.assertAbsoluteUriListEqual(expected, absolute_uris)


class ApiFilterTests(unittest.TestCase):
    def test_constructing_filter_succeeds(self) -> None:
        filters = [
            Pf(),
            Pf.created(),
            Pf.created(year__gt=[10, 20], year__lt=[20]),
        ]
        expected = [
            "ApiFilter()",
            "ApiFilter()",
            "ApiFilter((created.year.gt={10,20}) & (created.year.lt={20}))",
        ]

        self.assertListEqual(expected, [str(filt) for filt in filters])

    def test_or_filter_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "disjunction of already conjuncted filters"):
            (Pf.created(year__lt=[2000, 1990]) & Pf.created(month=20)) | Pf.created(month=1)

        with self.assertRaisesRegex(ValueError, "disjunction of already conjuncted filters"):
            Pf.created(year__lt=[2000, 1990], month=20) | Pf.created(month=1)

        with self.assertRaisesRegex(ValueError, "as there is already a different filter"):
            Pf.created(year__lt=[2000, 1990]) | Pf.last_modified(day=20)

    def test_or_filter_succeeds(self) -> None:
        filters = [
            Pf.created(year__gt=2020) | Pf(),
            Pf() | Pf.created(year__gt=[10, 20], year__lt=[20]),
            Pf.created(year__gt=10) | Pf.created(),
            Pf.created(year__gt=10) | Pf.created(year__lt=[2, 4, 8]) | Pf.created(day=4),
            Pf.created(year__gt=10) | Pf.created(year__gt=None) | Pf.created(year__gt=12),
        ]
        expected = [
            "ApiFilter((created.year.gt={2020}))",
            "ApiFilter((created.year.gt={10,20}) & (created.year.lt={20}))",
            "ApiFilter((created.year.gt={10}))",
            "ApiFilter((created.year.gt={10} | created.year.lt={2,4,8} | created.day={4}))",
            "ApiFilter((created.year.gt={10,12}))",
        ]

        self.assertListEqual(expected, [str(filt) for filt in filters])

    def test_and_filter_succeeds(self) -> None:
        filters = [
            Pf.created(year__gt=2020) & Pf(),
            Pf() & Pf.created(year__gt=[10, 20], year__lt=[20]),
            Pf.created(year__gt=10) & Pf.created(),
            Pf.created(year__gt=10) & Pf.created(year__lt=[2, 4, 8]) & Pf.created(day=4),
            Pf.created(year__gt=10) & Pf.created(year__gt=None) & Pf.created(year__gt=12),
            Pf.created(year__gt=[10, 20, 30], month=[1, 2, 3], day=[4, 5, 6])
            & Pf.last_modified(year=2021, month=[4, 5, 6], day=None)  # noqa: W503
            & Pf.created(year__lt=[120, 130], year__gt=[1000, 2000]),  # noqa: W503
        ]
        expected = [
            "ApiFilter((created.year.gt={2020}))",
            "ApiFilter((created.year.gt={10,20}) & (created.year.lt={20}))",
            "ApiFilter((created.year.gt={10}))",
            "ApiFilter((created.year.gt={10}) & (created.year.lt={2,4,8}) & (created.day={4}))",
            "ApiFilter((created.year.gt={10}) & (created.year.gt={12}))",
            "ApiFilter((created.year.gt={10,20,30}) & (created.month={1,2,3}) & (created.day={4,5,6}) & (created.year.gt={1000,2000}) "
            "& (created.year.lt={120,130}) & (last_modified.year={2021}) & (last_modified.month={4,5,6}))",
        ]

        self.assertListEqual(expected, [str(filt) for filt in filters])

    def test_default_filter_succeeds(self) -> None:
        filters = [
            Pf.tags("one-tag"),
            Pf.tags(["one-tag", "other-tag"]),
            Pf.tags(["one-tag", "other-tag"]) | Pf.tags(None) | Pf.tags("third-tag"),
        ]
        expected = [
            "ApiFilter((tags={one-tag}))",
            "ApiFilter((tags={one-tag,other-tag}))",
            "ApiFilter((tags={one-tag,other-tag,third-tag}))",
        ]

        self.assertListEqual(expected, [str(filt) for filt in filters])


class ApiFilterQueryParamTests(unittest.TestCase):
    def test_encoding_query_parameters_succeeds(self) -> None:
        filters = [
            Pf.created(year=[2020, 2021, 2022], year__gt=[20, 30, 40], day=[10, 20, 30])
            & (Pf.tags("a") | Pf.tags("b") | Pf.tags("c")),  # noqa: W503
            Pf.created(year__gt=2020, year__lt=2040)
            & Pf.last_modified(day=None, month=12)  # noqa: W503
            & Pf.tags(["a", "b", "c"]),  # noqa: W503
            Pf(),
            Pf.created(),
        ]
        expected = [
            {
                "created": "year:2020,year:2021,year:2022;year.gt:20,year.gt:30,year.gt:40;day:10,day:20,day:30",
                "tags": "a,b,c",
            },
            {
                "created": "year.gt:2020;year.lt:2040",
                "last_modified": "month:12",
                "tags": "a,b,c",
            },
            {},
            {},
        ]

        self.assertListEqual(expected, [filt.to_query_params() for filt in filters])

    def test_encoding_datetime_succeeds(self) -> None:
        filt = Pf.last_modified(
            gte=[
                datetime(2022, 1, 1, tzinfo=timezone.utc),
                datetime(2000, 3, 31, 18, tzinfo=timezone.utc),
            ]
        ) & Pf.last_modified(
            gte=datetime(2021, 5, 17, 12, 10, 50, 500000, tzinfo=timezone.utc)
        )  # noqa: W503
        expected = {
            "last_modified": "gte:2022-01-01T00\\:00\\:00.000Z,gte:2000-03-31T18\\:00\\:00.000Z;gte:2021-05-17T12\\:10\\:50.500Z"
        }

        self.assertEqual(expected, filt.to_query_params())

    def test_escaping_special_characters_succeeds(self) -> None:
        filt = (
            Pf.tags("abc cdef \\ \n ghj xyz") | Pf.tags("th:is;is;just,a,ve:ry;lo:ng;tag")
        ) & Pf.tags("just\\some\\\nmany\\\\\\backslashes\\n")
        expected = {
            "tags": "abc cdef \\\\ \n ghj xyz,th\\:is\\;is\\;just\\,a\\,ve\\:ry\\;lo\\:ng\\;tag;just\\\\some\\\\\nmany\\\\\\\\\\\\backslashes\\\\n"
        }

        self.assertEqual(expected, filt.to_query_params())
