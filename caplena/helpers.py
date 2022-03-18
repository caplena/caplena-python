import platform
import re
import sys
from datetime import datetime
from typing import Any, Dict, Iterable
from urllib.parse import urlencode

from caplena.constants import NOT_SET
from caplena.version import __version__


class Helpers:
    @staticmethod
    def get_user_agent(identifier: str) -> str:
        client_info = f"{identifier}/{__version__}"
        python_info = "python/{ver.major}.{ver.minor}.{ver.micro}".format(ver=sys.version_info)
        system_info = f"{platform.system()}/{platform.release()}"
        return " ".join([client_info, python_info, system_info])

    @staticmethod
    def append_path(base_uri: str, path: str) -> str:
        absolute_uri = base_uri
        if path:
            base_uri = base_uri if base_uri[-1] != "/" else base_uri[:-1]
            path = path if path[0] != "/" else path[1:]
            absolute_uri = f"{base_uri}/{path}"

        return absolute_uri

    @staticmethod
    def partial_dict(dict: Dict[str, Any], attrs: Iterable[str]) -> Dict[str, Any]:
        partial: Dict[str, Any] = {}
        for attr in attrs:
            partial[attr] = dict[attr]
        return partial

    @staticmethod
    def from_rfc3339_datetime(value: str) -> datetime:
        iso_8601 = value.replace("Z", "+00:00")
        return datetime.fromisoformat(iso_8601)

    @staticmethod
    def to_rfc3339_datetime(dt: datetime) -> str:
        rfc3339 = dt.strftime("%Y-%m-%dT%H:%M:%S.")
        rfc3339 += dt.strftime("%f")[:3]

        tz = dt.strftime("%z")
        if tz == "+0000":
            tz = "Z"
        elif tz != "":
            tz = tz[:3] + ":" + tz[3:]
        return rfc3339 + tz

    @staticmethod
    def build_qualified_uri(
        uri: str, *, path_params: Dict[str, str], query_params: Dict[str, str]
    ) -> str:
        # constructing path parameters
        for param_key, param_value in path_params.items():
            uri = uri.replace("{" + param_key + "}", str(param_value))
        has_remaining_path_params = re.search(r"{(.*?)}", uri)
        if has_remaining_path_params:
            found_param = has_remaining_path_params.group(1)
            if found_param == "":
                raise ValueError(
                    "Path specifies an invalid path parameter. Parameter name must not be empty."
                )
            else:
                raise ValueError(
                    f"Path requires `{has_remaining_path_params.group(1)}` parameter, but none is given."
                )

        # constructing query parameters
        query_string = urlencode(query_params)
        if query_string:
            uri += "?" + query_string

        return uri

    @staticmethod
    def build_escaped_filter_str(value: str) -> str:
        escaped = value.replace("\\", "\\\\")
        return re.sub(r"(:|,|;)", r"\\\1", escaped)

    @staticmethod
    def build_dict(**kwargs: Any) -> Dict[str, Any]:
        constructed_dict: Dict[str, Any] = {}
        for field_name, field in kwargs.items():
            if field != NOT_SET:
                constructed_dict[field_name] = field
        return constructed_dict
