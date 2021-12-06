import unittest
from typing import Any, List, Tuple

from caplena.api import ApiBaseUri, ApiRequestor, ApiVersion
from caplena.http.requests_http_client import RequestsHttpClient
from caplena.logging.default_logger import DefaultLogger


class ApiVersionTests(unittest.TestCase):
    def test_api_version_string_for_default_fails(self):
        with self.assertRaisesRegex(
            ValueError, "Cannot convert `DEFAULT` to a valid version string."
        ):
            ApiVersion.DEFAULT.version

    def test_api_version_string_succeeds(self):
        self.assertEqual("2021-12-01", ApiVersion.VER_2021_12_01.version)


class ApiRequestorTests(unittest.TestCase):
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
    ):
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

    def test_building_absolute_uri_fails(self):
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

    def test_building_absolute_uri_from_api_base_succeeds(self):
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

    def test_building_absolute_uri_from_string_succeeds(self):
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

    def test_building_absolute_uri_from_path_parameters_succeeds(self):
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

    def test_building_absolute_uri_from_query_parameters_succeeds(self):
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
