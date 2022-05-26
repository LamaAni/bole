import os
import click
from typing import Union
from bole.config.cascading import CascadingConfig
from bole.consts import is_show_full_errors, mark_show_full_errors
from bole.format import PrintFormat, get_print_formatted


class CliFormatOptions(dict):
    """Holds cli print format options."""

    @property
    def no_quote(self) -> bool:
        return self.get("no_quote", False)

    @property
    def format(self) -> PrintFormat:
        return self.get("format", PrintFormat.cli)

    def print(self, val: Union[list, dict], quote: bool = None):
        quote = not self.no_quote if quote is None else quote
        return get_print_formatted(self.format, val, quote)

    @classmethod
    def decorator(cls, default_format: PrintFormat = PrintFormat.cli, allow_quote: bool = True):
        def apply(*args):
            opts = [
                click.option(
                    "--format",
                    help=f"The document formate to print in ({', '.join(k.value for k in PrintFormat)})",
                    type=PrintFormat,
                    default=default_format,
                ),
            ]

            if allow_quote:
                opts.append(click.option("--no-quote", help="Do not quote cli arguments", is_flag=True, default=False))

            for opt in opts:
                fn = opt(*args)
            return fn

        return apply


class CliConfigOptions(dict):
    """Holds cli config loading options."""

    SHOW_FULL_ERRORS = None

    @property
    def cwd(self) -> str:
        return self.get("cwd", None)

    @property
    def environment(self) -> str:
        return self.get("env", None)

    @property
    def inherit_depth(self) -> int:
        return self.get("inherit_depth", -1)

    @property
    def full_errors(self) -> str:
        return self.get("full_errors", None)

    def load(
        self,
        ignore_environment: bool = False,
        inherit_depth: int = None,
    ) -> CascadingConfig:
        mark_show_full_errors(self.full_errors)
        inherit_depth = inherit_depth if inherit_depth is not None else self.inherit_depth
        inherit_depth = inherit_depth if inherit_depth is not None else -1

        config = CascadingConfig.load(
            self.cwd,
            environment=None if ignore_environment else self.environment,
            max_inherit_depth=inherit_depth,
        )

        return config

    @classmethod
    def decorator(cls, long_args_only=False):
        def apply(fn):
            opts = []
            opts += [
                click.option(
                    "--cwd",
                    "--source-path",
                    help="Execute bole from this path (Current working directory)",
                    default=os.curdir,
                ),
                click.option(
                    "-e",
                    "--env",
                    "--environment",
                    help="Name of the extra environment config to load",
                    default=None,
                ),
                click.option(
                    "--inherit-depth",
                    help="Max number of config parents to inherit (0 to disable, -1 inf)",
                    default=None,
                    type=int,
                ),
                click.option(
                    "--full-errors",
                    help="Show full python errors",
                    is_flag=True,
                    default=is_show_full_errors(),
                ),
            ]
            for opt in opts:
                fn = opt(fn)
            return fn

        return apply
