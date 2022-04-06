from datetime import datetime
from json import JSONEncoder
from typing import Any

from caplena.helpers import Helpers


class JsonDateEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return Helpers.to_rfc3339_datetime(o)
        return JSONEncoder.default(self, o)
