import glob
import os
from typing import Union
from bole.config.dict import CascadingConfigDictionary
from bole.exceptions import BoleException
from bole.utils import resolve_path


class CascadingConfigImport(CascadingConfigDictionary):
    """Implements a config import."""

    @property
    def path(self) -> str:
        """The import path"""
        return self.get("path", None)

    @property
    def recursive(self) -> bool:
        """If true, this import is recursive. Defaults to True if ** in path"""
        return self.get("recursive", "**" in (self.path or ""))

    @property
    def required(self) -> bool:
        """If true, this import is required (Ignored on glob search)"""
        return self.get("required", False)

    def find_files(self, search_from_directory: str):
        """Find files that match this import. (Glob search)

        Args:
            search_from_directory (str): For imports with partial paths,
            start searching for the import from this directory. Required since
            most imports are relative.

        Returns:
            List[str]: The list of absolute paths to load the config from.
        """
        assert isinstance(self.path, str) and len(self.path) > 0, BoleException(
            "Invalid import, src cannot be none or empty"
        )

        import_path = resolve_path(self.path, root_directory=search_from_directory)

        if "*" in import_path or "?" in import_path:
            return glob.glob(import_path, recursive=self.recursive is True)

        if self.required:
            assert os.path.exists(import_path), BoleException(f"Invalid import, source path {import_path} not found")
        return [import_path] if os.path.isfile(import_path) else []

    @classmethod
    def parse(
        cls,
        val: Union[dict, str],
        defaults: dict = {},
    ):
        """Create a new object of type CascadingConfigImport by parsing a value.

        Args:
            val (Union[dict, str]): The value import
            defaults (dict, optional): Override default values with this dictionary. Defaults to {}.
        """
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
        """If true, use deep merge when joining configurations otherwise just overwrite"""
        return self.get("use_deep_merge", True)

    @property
    def concatenate_lists(self) -> bool:
        """If true, merged lists will be appended"""
        return self.get("concatenate_lists", True)

    @property
    def allow_imports(self) -> bool:
        return self.get("allow_imports", True)
