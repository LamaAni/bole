import glob
import os
from typing import Union
from bole.config.dict import CascadingConfigDictionary
from bole.exceptions import BoleException


class CascadingConfigImport(CascadingConfigDictionary):
    """Implements a config import."""

    @property
    def path(self) -> str:
        return self.get("path", None)

    @property
    def recursive(self) -> bool:
        return self.get("recursive", "**" in (self.path or ""))

    @property
    def required(self) -> bool:
        return self.get("required", True)

    def find_files(self):
        assert self.path is not None, BoleException("Invalid import, src cannot be none")

        if "*" in self.path or "?" in self.path:
            return glob.glob(self.path, recursive=self.recursive is True)

        if self.required:
            assert os.path.exists(self.path), BoleException(f"Invalid import, source path {self.path} not found")
        return [self.path] if os.path.isfile(self.path) else []

    @classmethod
    def parse(
        cls,
        val: Union[dict, str],
        defaults: dict = {},
    ):
        if isinstance(val, str):
            path = val
            val = defaults.copy()
            val.update({"path": path})

        assert isinstance(val, dict), ValueError("The parsed value must be a dictionary, got " + str(type(val)))

        return super().parse(val)


class CascadingConfigSettings(CascadingConfigDictionary):
    @property
    def inherit(self) -> str:
        """If true, this config can inherit parent folder configurations.
        Used in 'load' function after initialization"""
        return self.get("inherit", None)

    @property
    def inherit_siblings(self) -> str:
        """If true, this config can inherit sibling configurations (same dir)"""
        return self.get("inherit_siblings", True)

    @property
    def use_deep_merge(self) -> bool:
        return self.get("use_deep_merge", True)

    @property
    def concatenate_lists(self) -> bool:
        return self.get("concatenate_lists", True)
