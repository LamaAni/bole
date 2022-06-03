import os
import logging
from typing import Dict, Union, Any
from bole.utils import create_random_string, datetime_to_iso, resolve_log_level
from collections import defaultdict

NO_COLOR = os.environ.get("NO_COLOR", "false").lower() == "true"
BOLE_LOG_FORMAT_EXTRA_INFO = ""
BOLE_LOG_FORMAT = os.environ.get("BOLE_LOG_FORMAT", None) or (
    "[%(gray)s%(timestamp)s%(end_color)s][%(levelcolor)s%(levelname)5s%(end_color)s]"
    + BOLE_LOG_FORMAT_EXTRA_INFO
    + " %(msg)s"
)

COLORS = {
    "red": "\033[0;31m",
    "green": "\033[0;32m",
    "yellow": "\033[0;33m",
    "blue": "\033[0;34m",
    "magenta": "\033[0;35m",
    "cyan": "\033[0;36m",
    "gray": "\033[0;90m",
    "end_color": "\033[0m",
}

LEVEL_COLORS = {
    logging.DEBUG: "gray",
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "red",
}

ALT_LEVEL_NAMES = {
    "WARNING": "WARN",
    "CRITICAL": "CRIT",
}


class BoleLogFormatter(logging.Formatter):
    def __init__(
        self,
        log_format: str = BOLE_LOG_FORMAT,
        colors: Dict[str, str] = COLORS,
        level_colors: Dict[int, str] = LEVEL_COLORS,
        use_colors: bool = not NO_COLOR,
        alt_level_names: Dict[str, str] = ALT_LEVEL_NAMES,
        allow_missing_values: bool = True,
    ) -> None:
        """Bole log formatter. Used to create consistent logs

        Args:
            log_format (str, optional): The log format. Defaults to BOLE_LOG_FORMAT.
            colors (Dict[str, str], optional): The log format colors. Defaults to COLORS.
            level_colors (Dict[int, str], optional): The log level colors mapping. Defaults to LEVEL_COLORS.
            use_colors (bool, optional): If ture, use colors. Defaults to [not NO_COLOR].
            alt_level_names (Dict[str, str], optional): Replace log level names with other names.
                Defaults to ALT_LEVEL_NAMES.
        """
        super().__init__()
        self.log_format = log_format
        self.colors = colors or {}
        self.level_colors = level_colors or {}
        self.use_colors = use_colors is True
        self.alt_level_names = alt_level_names or {}
        self.allow_missing_values = allow_missing_values is True

    def get_log_values_dictionary(self, data: Union[str, dict, Any]):
        if isinstance(data, str):
            data = {"msg": data}
        elif not isinstance(data, dict):
            # Must have a dict attribute
            data = data.__dict__

        if "timestamp" not in data:
            data["timestamp"] = datetime_to_iso()

        levelname = data.get("levelname", None)

        if levelname is not None and levelname in self.alt_level_names:
            data["levelname"] = self.alt_level_names[levelname]

        if self.use_colors:
            data.update(self.colors)
            levelno = data.get("levelno")
            if levelno in self.level_colors:
                levelcolor = self.level_colors[levelno]
                if levelcolor in self.colors:
                    levelcolor = self.colors[levelcolor]
                data["levelcolor"] = levelcolor

        return data

    def format_log_message(
        self,
        data: Union[str, dict, Any],
        log_format: str = None,
    ):
        format_map = self.get_log_values_dictionary(data)
        if self.allow_missing_values:
            format_map = defaultdict(lambda: "", format_map)

        log_format = log_format if log_format is not None else self.log_format

        return log_format % format_map

    def format(
        self,
        record: logging.LogRecord,
        log_format: str = None,
    ):
        return self.format_log_message(
            record,
            log_format=log_format,
        )


def create_logger(logger_name: str = None, log_level: Union[str, int] = None):
    """Create a new bole logger, given a logger name.

    Args:
        logger_name (str, optional): The name of the new logger. Defaults to None.
        log_level (Union[str, int], optional): Logger log level. Defaults to None.

    Returns:
        Logger: The new logger
    """
    logger_name = logger_name or "bole-log-" + create_random_string()
    log = logging.Logger(logger_name)

    log_level = resolve_log_level(log_level or os.environ.get("LOG_LEVEL", "INFO"))
    log.setLevel(log_level)

    formatter = BoleLogFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log


log = create_logger("bole-log-core")

if __name__ == "__main__":
    formatter = BoleLogFormatter()
    print(formatter.format_log_message("lasd"))
    log.debug("aadsad")
    log.critical("asd")
    log.warning("Lama")
    log.error("asdsad")
    log.info("Test ")
