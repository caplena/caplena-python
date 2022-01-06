from enum import Enum


class ApiVersion(Enum):
    DEFAULT = 0
    VER_2022_01_01 = 1

    @property
    def version(self) -> str:
        if self.name != ApiVersion.DEFAULT.name:
            return self.name.replace("VER_", "").replace("_", "-")
        else:
            raise ValueError(f"Cannot convert `{self.name}` to a valid version string.")
