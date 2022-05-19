import click

from bole.log import log
from bole.consts import is_show_full_errors


@click.group("bole")
def bole():
    """Easy logger and cascading configuration manager for python (yaml, json)"""
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
