from typing import List
import click
from bole.config.cascading import CascadingConfig
from bole.format import PrintFormat

from bole.log import log
from bole.utils import clean_data_types, resolve_log_level
from bole.consts import is_show_full_errors, __version__
from bole.cli_options import CliConfigOptions, CliFormatOptions


def __get_config_value(
    config: CascadingConfig,
    dict_paths: List[str],
    allow_null: bool = False,
    allow_missing: bool = False,
):
    """Helper method to print config value"""
    rslt = None
    was_found = False
    if len(dict_paths) == 0:
        # If no paths specified, display the entire config.
        rslt = [config.to_dictionary()]
        was_found = True
    else:
        # Search for paths in the config
        rslt = config.find(*dict_paths)
        # Clean the values from custom python types
        rslt = [clean_data_types(v) for v in rslt]
        was_found = len(rslt) > 0

    if not was_found:
        if allow_missing:
            return ""
        # Nothing was found. Throw error.
        raise ValueError(f"The dictionary path(s) were not found in the config, searched: {', '.join(dict_paths)}")

    if not allow_null and any(v is None for v in rslt):
        raise ValueError("Found null values in path(s): " + ", ".join(dict_paths))

    rslt = ["null" if v is None else v for v in rslt]

    if len(dict_paths) < 2:
        # If a single value requested, just display that value.
        rslt = rslt[0]

    return rslt


@click.group("bole")
def bole():
    """Easy logger and cascading configuration manager for python (yaml, json)"""
    pass


@bole.command("version", help="Show the bole version")
def version():
    print(__version__)


@bole.command("log")
@click.argument("level")
@click.argument("message", nargs=-1)
def cli_log(level: str, message: List[str]):
    """Log commands
    level - the level of the log (CRITICAL, ERROR, WARNING, INFO, DEBUG),
    message - the message(s) to display.
    """
    for msg in message:
        log.log(
            level=resolve_log_level(level.upper()),
            msg=msg,
        )


@bole.group("config")
def config():
    """Config command options"""
    pass


@config.command("get")
@CliConfigOptions.decorator()
@CliFormatOptions.decorator(default_format=PrintFormat.yaml)
@click.argument("dict-paths", nargs=-1)
@click.option("--allow-null", help="Return null values", is_flag=True, default=False)
@click.option("--allow-missing", help="Don't error on missing values, print nothing", is_flag=True, default=False)
def config_get(
    dict_paths: List[str],
    allow_null: bool = False,
    allow_missing: bool = False,
    **kwargs,
):
    """Print the bole computed configuration.
    DICT_PATHS (array) is a value to search, e.g. 'a.b[0].c'. If no paths provided
    will print the entire config (same as view).
    """
    config = CliConfigOptions(kwargs).load()
    to_display = __get_config_value(
        config,
        dict_paths=dict_paths,
        allow_null=allow_null,
        allow_missing=allow_missing,
    )

    if not isinstance(to_display, list) and not isinstance(to_display, dict):
        print(str(to_display))  # Not a list or dict, don't format output.
    else:
        print(CliFormatOptions(kwargs).print(to_display))


@config.command("view")
@CliConfigOptions.decorator()
@CliFormatOptions.decorator(default_format=PrintFormat.yaml)
def config_view(**kwargs):
    config = CliConfigOptions(kwargs).load()
    to_display = config.to_dictionary()

    if not isinstance(to_display, list) and not isinstance(to_display, dict):
        print(str(to_display))  # Not a list or dict, don't format output.
    else:
        print(CliFormatOptions(kwargs).print(to_display))
    pass


def run_cli_main():
    try:
        bole()
    except Exception as ex:
        if is_show_full_errors():
            raise ex
        else:
            log.error(ex)
            exit(1)
