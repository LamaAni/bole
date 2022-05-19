from typing import List
import click

from bole.log import log
from bole.utils import resolve_log_level
from bole.consts import is_show_full_errors
from bole.cli_options import CliConfigOptions


@click.group("bole")
def bole():
    """Easy logger and cascading configuration manager for python (yaml, json)"""
    pass


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
def config_get(*kwargs):
    pass


@config.command("view")
@CliConfigOptions.decorator()
def config_view(*kwargs):
    pass


@config.command("set")
@CliConfigOptions.decorator()
def config_set(*kwargs):
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
