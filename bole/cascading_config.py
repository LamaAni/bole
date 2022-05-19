import json
import os
import yaml
from typing import List
from bole.utils import deep_merge


class CascadingConfig(dict):
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
        super(*args, **kwargs)
        self._source_path: str = None
        self._source_directory: str = None

    @property
    def inherit(self) -> str:
        """If true, this config can inherit parent folder configurations.
        Used in 'load' function after initialization"""
        return self.get("inherit", None)

    @property
    def inherit_siblings(self) -> str:
        """If true, this config can inherit parent folder configurations.
        Used in 'load' function after initialization"""
        return self.get("inherit_siblings", None)

    def initialize(self):
        """Call to initialize the configuration. Overridable."""
        pass

    CONFIG_FILEPATHS: List[str] = ["config.yaml", "config.json"]
    """A collection of config file paths where the configuration
    may exist. Can be an absolute or relative path. If multiple configuration file
    names exist, the first file will be taken.

    class Overridable
    """

    @classmethod
    def load(
        cls,
        src: str,
        initialize: bool = True,
        max_inherit_depth: int = -1,
        concatenate_lists: bool = True,
        default_format: str = "yaml",
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
        config_filepaths: List[List[str]] = []
        if os.path.isfile(src):
            config_filepaths.append([src])
            src = os.path.dirname(src)

        cur_path = src
        while True:
            group: List[str] = []
            for fn in cls.CONFIG_FILEPATHS:
                if not os.path.isabs(fn):
                    fn = os.path.abspath(os.path.join(cur_path, fn))
                group.append(fn)

            config_filepaths.append(group)

            # moving to parent
            parent_path = os.path.dirname(cur_path)
            if parent_path is None or parent_path == cur_path:
                break
            cur_path = parent_path

        # Reading configurations as a cascading config.
        configurations: List[CascadingConfig] = []
        for fp_group in config_filepaths:
            config: CascadingConfig = None
            for fp in fp_group:
                if os.path.isfile(fp):
                    # Load config
                    config_file_text = ""
                    with open(fp, "r") as config_file:
                        config_file_text = config_file.read(fp)

                    _, format = os.path.splitext(fp)
                    if format.startswith("."):
                        format = format[1:]
                    if format not in ["yaml", "json"]:
                        format = default_format

                    if format == "yaml":
                        as_dict = yaml.safe_load(config_file_text)
                    elif format == "json":
                        as_dict = json.loads(config_file_text)
                    else:
                        raise ValueError("Could not find a supported format type for " + fp)

                    config = cls(as_dict)
                    if initialize:
                        config.initialize()

                    config._source_path = fp
                    configurations.append(config)

            if config is not None and not config.inherit:
                break

        if max_inherit_depth > -1:
            configurations = configurations[0 : max_inherit_depth + 1]  # noqa E203

        # Merging the configuration into a new config.
        if len(configurations) == 1:
            config = configurations[0]
        else:
            config = cls(deep_merge({}, *configurations, concatenate_lists=concatenate_lists))
            if initialize:
                config.initialize()

        return config
