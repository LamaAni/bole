import os
import click
from bole.cascading_config import CascadingConfig


class CliConfigOptions(dict):
    SHOW_FULL_ERRORS = None

    @property
    def cwd(self) -> str:
        return self.get("cwd", None)

    @property
    def environment(self) -> str:
        return self.get("env", None)

    @property
    def inherit_depth(self) -> int:
        return self.get("inherit_depth", None)

    def load(
        self,
        ignore_environment: bool = False,
        inherit_depth: int = None,
    ) -> CascadingConfig:
        config = CascadingConfig.load(
            self.cwd,
            environment=None if ignore_environment else self.environment,
            inherit_depth=inherit_depth if inherit_depth is not None else self.inherit_depth,
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
                    help="Execute yapenv from this path (Current working directory)",
                    default=os.curdir,
                ),
                click.option(
                    *(
                        [
                            "-e",
                            "--env",
                            "--environment",
                        ]
                        if not long_args_only
                        else ["--environment"]
                    ),
                    help="Name of the extra environment config to load",
                    default=None,
                ),
                click.option(
                    "--inherit-depth",
                    help="Max number of config parents to inherit (0 to disable, -1 inf)",
                    default=None,
                    type=int,
                ),
                click.option("--full-errors", help="Show full python errors", is_flag=True),
                click.option(
                    "--ignore-missing-env",
                    help="Do not throw error if environment was not found",
                    is_flag=True,
                    default=False,
                ),
            ]
            for opt in opts:
                fn = opt(fn)
            return fn

        return apply
