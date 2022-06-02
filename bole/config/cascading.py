import json
import os
import yaml
from typing import List, Union
from bole.consts import CONFIG_SEARCH_PATHS
from bole.exceptions import BoleException
from bole.utils import deep_merge

from bole.config.dict import CascadingConfigDictionary
from bole.config.built_in import CascadingConfigImport, CascadingConfigSettings


def config_file_parser(fpath: str, default_format: str = "yaml") -> dict:
    """Default configuration file parser.

    Args:
        fpath (str): The path to the config file.
        default_format (str, optional): The default format if cannot be identified by ext. Defaults to "yaml".

    Returns:
        dict: The loaded config file.
    """
    _, format = os.path.splitext(fpath)
    if format.startswith("."):
        format = format[1:]
    if format not in ["yaml", "json"]:
        format = default_format

    assert format in ["yaml", "json"], ValueError("Could not find a supported format type for " + fpath)

    with open(fpath, "r") as config_file:
        config_file_text = config_file.read()

    if config_file_text.strip() == "":
        as_dict = {}
    elif format == "yaml":
        as_dict = yaml.safe_load(config_file_text)
    elif format == "json":
        as_dict = json.loads(config_file_text)
    else:
        raise ValueError("Could not find a supported format type for " + fpath)

    assert isinstance(as_dict, dict), BoleException("Configuration files must represent a dictionary @ " + fpath)
    return as_dict


CASCADING_CONFIG_IMPORT_KEY = "import"


def merge_cascading_dicts(
    target: Union[dict, "CascadingConfig"],
    *sources: List[dict],
    merge_source: "CascadingConfig" = None,
):
    """Internal. Merge cascading config using the config settings.

    Args:
        target (Union[dict, &quot;CascadingConfig&quot;]): The target of the merge.
        merge_source (CascadingConfig, optional): The source for settings. Defaults to None.

    Returns:
        dict: Merged target.
    """
    merge_source = merge_source or target
    if not isinstance(merge_source, CascadingConfig):
        merge_source = CascadingConfig.parse(target)

    if merge_source.settings.use_deep_merge:
        target = deep_merge(
            target,
            *sources,
            append_lists=merge_source.settings.concatenate_lists,
        )
    else:
        for v in sources:
            target.update(v)

    return target


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
        self.__source_path: str = None
        self.__source_directory: str = None

    @property
    def source_directory(self) -> str:
        """The directory of the source path this config was loaded from. Equals source_path if its a directory"""
        return self.__source_directory

    @property
    def source_path(self) -> str:
        """The source path this config was loaded from"""
        return self.__source_path

    @property
    def config_imports(self) -> List[CascadingConfigImport]:
        return CascadingConfigImport.parse_list(self.get(CASCADING_CONFIG_IMPORT_KEY, []))

    @property
    def environments(self):
        return self.parse_dictionary(self.get("environments", {}))

    @property
    def settings(self) -> CascadingConfigSettings:
        return CascadingConfigSettings.parse(self.get("settings", {}))

    def initialize(self, environment: str = None):
        """Call to initialize the configuration. Overridable."""

    def __merge_environment(self, environment: str = None):
        """Overrideable. Merge the environment config into this config.

        Args:
            environment (str, optional): The name of the environment to merge. Defaults to None.
        """
        if environment is not None and environment in self.environments:
            environment_dict = self.environments[environment].copy()

            # Environment imports before src imports.
            all_imports = environment_dict.get(CASCADING_CONFIG_IMPORT_KEY, []) + self.get(
                CASCADING_CONFIG_IMPORT_KEY, []
            )

            if CASCADING_CONFIG_IMPORT_KEY in environment_dict:
                del environment_dict[CASCADING_CONFIG_IMPORT_KEY]

            if len(all_imports) > 0:
                self[CASCADING_CONFIG_IMPORT_KEY] = all_imports

            # Environment should take precedent on self
            merge_cascading_dicts(
                self,
                self.environments[environment],
                merge_source=self,
            )

    @classmethod
    def __get_config_sibling_search_groups(cls, src: str, search_paths: List[str]):
        """Internal returns the siblings search paths (as groups)"""
        sibling_search_groups = []
        cur_path = src
        while True:
            group: List[str] = []
            for fn in search_paths:
                if not os.path.isabs(fn):
                    fn = os.path.abspath(os.path.join(cur_path, fn))
                group.append(fn)

            sibling_search_groups.append(group)

            # moving to parent
            parent_path = os.path.dirname(cur_path)
            if parent_path is None or parent_path == cur_path:
                break
            cur_path = parent_path

        return sibling_search_groups

    @classmethod
    def __load_siblings(
        cls,
        imports: List[CascadingConfigImport],
        environment: str = None,
        parse_config=config_file_parser,
        already_imported: set = None,
        load_imports: bool = True,
        search_from_directory: str = None,
    ) -> List["CascadingConfig"]:
        """Internal. Loads the configuration siblings by searching in the sibling source path"""
        # Recreate the list to allow multiple files.
        imports = list(imports)
        already_imported = already_imported or set()

        # The resulting configs.
        configs: List[cls] = []

        # Processing imports
        while len(imports) > 0:
            config_import = imports.pop(0)
            config_files = config_import.find_files(search_from_directory=search_from_directory)

            # If no imports
            if len(config_files) == 0:
                continue
            if len(config_files) > 1:
                # More then one file. That would mean that it was a glob.
                # Adding to the imports
                imports = [
                    CascadingConfigImport.parse(
                        c,
                        defaults={
                            "recursive": False,
                            "required": False,
                        },
                    )
                    for c in config_files
                ] + imports
                continue

            config_filepath = config_files[0]
            if config_filepath in already_imported:
                # Skipped. Already imported (circular)
                continue

            # Loading the config
            config: cls = cls.parse(parse_config(config_filepath))
            config.__merge_environment(environment=environment)
            config.__source_directory = os.path.dirname(config_filepath)
            config.__source_path = config_filepath
            config.initialize()

            if load_imports:
                if config.settings.allow_imports:
                    # if the config has imports they should come before it.
                    configs += cls.__load_siblings(
                        imports=config.config_imports,
                        environment=environment,
                        parse_config=parse_config,
                        already_imported=already_imported,
                        search_from_directory=config.source_directory,
                    )

                if CASCADING_CONFIG_IMPORT_KEY in config:
                    del config[CASCADING_CONFIG_IMPORT_KEY]

            configs.append(config)

            if not config.settings.inherit_siblings:
                break

        return configs

    @classmethod
    def load(
        cls,
        src: str,
        environment: str = None,
        max_inherit_depth: int = -1,
        load_imports: bool = True,
        search_paths: List[str] = CONFIG_SEARCH_PATHS,
        parse_config=config_file_parser,
    ):
        """Loads a configuration from a source path.

        Args:
            src (str): The path (file or directory) to load from.
            environment (str, optional): The environment name to load for. Defaults to None.
            max_inherit_depth (int, optional): The max number of inherited parents. Defaults to -1.
            load_imports (bool, optional): Load imports when inheriting. Defaults to True.
            search_paths (List[str], optional): The paths/sub-paths where to look for config giles.
                Defaults to CONFIG_SEARCH_PATHS.
            parse_config ((fpath)=>dict, optional): Parses the config file into a dictionary.
                Defaults to config_file_parser.

        Returns:
            CascadingConfig: The merged/collected config.
        """

        # mapping configuration filepaths
        src = os.path.abspath(src)
        sibling_search_groups: List[List[str]] = []
        if os.path.isfile(src):
            sibling_search_groups.append([src])
            src = os.path.dirname(src)

        src_directory = src

        # Finding all search groups from which to load the config
        sibling_search_groups += cls.__get_config_sibling_search_groups(src, search_paths)

        # Reading configurations as a cascading config.
        configurations: List[CascadingConfig] = []

        for grp in sibling_search_groups:
            grp = list(grp)
            imports: List[CascadingConfigImport] = []
            for filepath in grp:
                imports.append(
                    CascadingConfigImport.parse(
                        filepath,
                        defaults={
                            "recursive": False,
                            "required": False,
                        },
                    )
                )

            siblings = cls.__load_siblings(
                imports,
                environment=environment,
                parse_config=parse_config,
                load_imports=load_imports,
            )
            siblings.reverse()
            grp_config = cls.parse(
                {}
                if len(siblings) == 0
                else merge_cascading_dicts(
                    {},
                    *siblings,
                    merge_source=siblings[-1],
                ),
            )
            configurations.append(grp_config)

            if not grp_config.settings.inherit:
                break

        if len(configurations) == 0:
            config = cls.parse({})
        else:
            merge_source = configurations[0]

            if max_inherit_depth > -1:
                configurations = configurations[0 : max_inherit_depth + 1]  # noqa E203

            # Order of merging is reversed
            configurations.reverse()

            # Merging the configuration into a new config.
            config = cls.parse(
                merge_cascading_dicts(
                    {},
                    *configurations,
                    merge_source=merge_source,
                )
            )

        config.__source_path = src
        config.__source_directory = src_directory

        return config
