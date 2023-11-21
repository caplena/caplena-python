from enum import Enum


class ApiVersion(Enum):
    DEFAULT = 0
    VER_2022_11_22 = 3

    @property
    def version(self) -> str:
        if self.name != ApiVersion.DEFAULT.name:
            return self.name.replace("VER_", "").replace("_", "-")
        else:
            raise ValueError(f"Cannot convert `{self.name}` to a valid version string.")
