import platform
import re
import sys
from typing import Dict
from urllib.parse import urlencode

from caplena import version


class Helpers:
    @staticmethod
    def get_user_agent(identifier: str):
        client_info = f"{identifier}/{version.__version__}"
        python_info = "python/{ver.major}.{ver.minor}.{ver.micro}".format(ver=sys.version_info)
        system_info = f"{platform.system()}/{platform.release()}"
        return " ".join([client_info, python_info, system_info])

    @staticmethod
    def append_path(base_uri: str, path: str):
        absolute_uri = base_uri
        if path:
            base_uri = base_uri if base_uri[-1] != "/" else base_uri[:-1]
            path = path if path[0] != "/" else path[1:]
            absolute_uri = f"{base_uri}/{path}"

        return absolute_uri

    @staticmethod
    def build_qualified_uri(uri: str, *, path_params: Dict[str, str], query_params: Dict[str, str]):
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
