import platform
import sys

from caplena import version


class Helpers:
    @staticmethod
    def get_user_agent(identifier: str):
        client_info = f"{identifier}/{version.__version__}"
        python_info = "python/{ver.major}.{ver.minor}.{ver.micro}".format(ver=sys.version_info)
        system_info = f"{platform.system()}/{platform.release()}"
        return " ".join([client_info, python_info, system_info])
