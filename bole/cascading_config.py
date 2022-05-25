import json
import os
import yaml
import glob
from typing import Any, Callable, Dict, List, Union
from bole.consts import CONFIG_SEARCH_PATHS
from bole.exceptions import BoleException
from bole.utils import clean_data_types, deep_merge, find_in_collection


def config_file_parser(fpath: str, default_format: str = "yaml") -> dict:
    _, format = os.path.splitext(fpath)
    if format.startswith("."):
        format = format[1:]
    if format not in ["yaml", "json"]:
        format = default_format

    assert format in ["yaml", "json"], ValueError("Could not find a supported format type for " + fpath)

    with open(fpath, "r") as config_file:
        config_file_text = config_file.read()

    if format == "yaml":
        as_dict = yaml.safe_load(config_file_text)
    elif format == "json":
        as_dict = json.loads(config_file_text)
    else:
        raise ValueError("Could not find a supported format type for " + fpath)

    assert isinstance(as_dict, dict), BoleException("Configuration files must represent a dictionary @ " + fpath)
    return as_dict


class CascadingConfigDictionary(dict):
    def find(
        self,
        *paths: str,
        action: Callable[[Any, Any], Any] = None,
    ) -> List[Any]:
        """Search the config for specific dictionary paths.
        Paths is a list of string representations of dictionary paths.
        Ex: paths = ['a.b[0].c']
        """
        found = []
        for p in paths:
            val, was_found = find_in_collection(self, p, action=action)
            if not was_found:
                continue
            found.append(val)
        return found

    def to_dictionary(self) -> dict:
        """Convert this config to a dictionary"""
        return clean_data_types(self)

    @classmethod
    def parse_dictionary(
        cls,
        val: Dict[str, Union[str, dict]],
        in_place: bool = True,
    ):
        rslt: Dict[str, cls] = val
        if not in_place:
            rslt = {}
        for k, v in val.items():
            rslt[k] = cls.parse(v)
        return rslt

    @classmethod
    def parse_list(
        cls,
        val: List[Union[str, dict]],
        in_place: bool = True,
    ):
        rslt: List[cls] = val
        if not in_place:
            rslt = []
        rslt: List[cls] = []

        for i in range(len(val)):
            rslt[i] = cls.parse(val[i])

        return rslt

    @classmethod
    def parse(
        cls,
        val: Union[dict, List[dict]],
    ):
        """Parse the dict and return the a class"""
        if isinstance(val, cls):
            return val
        if isinstance(val, dict):
            return cls(**val)

        raise ValueError("Invalid value when trying to parse dictionary item")


class CascadingConfigImport(CascadingConfigDictionary):
    """Implements a config import."""

    @property
    def path(self) -> str:
        return self.get("path", None)

    @property
    def recursive(self) -> bool:
        return self.get("recursive", False)

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


class CascadingConfig(CascadingConfigDictionary):
    def __init__(self, *args, **kwargs):
        """Implements a directory cascading config which allows
        inheritance between a source config file and a parent config
        in a parent directory.

        Inherits dict initializer:
            CascadingConfig() -> new empty dictionary dict(mapping) -> new dictionary initialized from
                a mapping object's (key, value) pairs
            CascadingConfig(iterable) -> new dictionary initialized as if via:
                d = {} for k, v in iterable:
                    d[k] = v
            CascadingConfig(**kwargs) -> new dictionary initialized with the name=value pairs
                in the keyword argument list. For example: dict(one=1, two=2)
        """
        super(CascadingConfigDictionary, self).__init__(*args, **kwargs)
        self._source_path: str = None
        self._source_directory: str = None
        self._environment_loaded: bool = False

    @property
    def config_imports(self) -> List[CascadingConfigImport]:
        return CascadingConfigImport.parse_list(self.get("import", []))

    @property
    def environments(self) -> Dict[str, "CascadingConfig"]:
        return CascadingConfig.parse_dictionary(self.get("import", {}))

    @property
    def inherit(self) -> str:
        """If true, this config can inherit parent folder configurations.
        Used in 'load' function after initialization"""
        return self.get("inherit", None)

    @property
    def inherit_siblings(self) -> str:
        """If true, this config can inherit sibling configurations (same dir)"""
        return self.get("inherit_siblings", True)

    def initialize(self, environment: str = None):
        """Call to initialize the configuration. Overridable."""
        pass

    @classmethod
    def __get_config_search_groups(cls, src: str, search_paths: List[str]):
        search_groups = []
        cur_path = src
        while True:
            group: List[str] = []
            for fn in search_paths:
                if not os.path.isabs(fn):
                    fn = os.path.abspath(os.path.join(cur_path, fn))
                group.append(fn)

            search_groups.append(group)

            # moving to parent
            parent_path = os.path.dirname(cur_path)
            if parent_path is None or parent_path == cur_path:
                break
            cur_path = parent_path

        return search_groups

    @classmethod
    def __load_siblings(
        cls,
        *search_path: str,
        parse_config=config_file_parser,
    ) -> List["CascadingConfig"]:
        # Mapping to imports
        config_imports: List[CascadingConfigImport] = [
            CascadingConfigImport.parse(
                c,
                defaults={
                    "recursive": False,
                    "required": False,
                },
            )
            for c in search_path
        ]

        configs: List[cls] = []

        # Processing imports
        while len(config_imports) > 0:
            config_import = config_imports.pop(0)
            config_files = config_import.find_files()

            # If no imports
            if len(config_files) == 0:
                continue
            if len(config_files) > 1:
                # More then one file. That would mean that it was a glob.
                # Adding to the imports
                config_imports = [
                    CascadingConfigImport.parse(
                        c,
                        defaults={
                            "recursive": False,
                            "required": False,
                        },
                    )
                    for c in config_files
                ] + config_imports
                continue

            # Loading the config
            config: cls = cls.parse(parse_config(config_files[0]))
            config.initialize()
            configs.append(config)

            if not config.inherit_siblings:
                break

            # Insert any imports on top
            config_imports = config.config_imports + config_imports

        return configs

    @classmethod
    def load(
        cls,
        src: str,
        environment: str = None,
        initialize: bool = True,
        max_inherit_depth: int = -1,
        concatenate_lists: bool = True,
        search_paths: List[str] = CONFIG_SEARCH_PATHS,
        parse_config=config_file_parser,
    ):
        """Loads a configuration given a source path to look in.

        Args:
            src (str): The path to configuration source. If a file, would load the file first,
                And then continue to load the configuration from the directory.
            initialize (bool, optional): Call the initialize function for each config before merging. Defaults to True.
            max_inherit_depth (int, optional): The max number of inherited configs. <0 means INF. Defaults to -1
            concatenate_lists (bool, optional): If true, concatenate the lists, otherwise try and merge them.
            default_format (str, optional): The default format type to use when no extention is not matched.
                If None will throw an error when file extension is not (yaml, json). Can be: yaml, json.
        """

        # mapping configuration filepaths
        src = os.path.abspath(src)
        config_src_groups: List[List[str]] = []
        if os.path.isfile(src):
            config_src_groups.append([src])
            src = os.path.dirname(src)

        # Finding all search groups from which to load the config
        config_src_groups += cls.__get_config_search_groups(src, search_paths)

        # Loading configuration from groups.
        for src_group in config_src_groups:
            pass

        # Reading configurations as a cascading config.
        configurations: List[CascadingConfig] = []
        for src_group in config_src_groups:
            siblings = cls.__load_siblings(*src_group, parse_config=parse_config)
            siblings.reverse()
            grp_config = cls.parse(deep_merge({}, *siblings))
            configurations.append(grp_config)

            if not grp_config.inherit:
                break

        if max_inherit_depth > -1:
            configurations = configurations[0 : max_inherit_depth + 1]  # noqa E203

        # Merging the configuration into a new config.
        config = cls.parse(deep_merge({}, *configurations, concatenate_lists=concatenate_lists))

        if environment in config.environments:
            config.update(config.environments[environment])

        if initialize:
            config.initialize()

        return config
