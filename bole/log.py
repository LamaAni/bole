import os
import logging
from typing import Dict, Union
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
    ) -> None:
        super().__init__()
        self.log_format = log_format
        self.colors = colors or {}
        self.level_colors = level_colors or {}
        self.use_colors = use_colors is True
        self.alt_level_names = alt_level_names or {}

    def get_format_values_dictionary(self, record: logging.LogRecord):
        data = {
            "timestamp": datetime_to_iso(),  # Take now.
        }
        data.update(record.__dict__)

        if record.levelname in self.alt_level_names:
            data["levelname"] = self.alt_level_names[record.levelname]

        if self.use_colors:
            data.update(self.colors)
            if record.levelno in self.level_colors:
                levelcolor = self.level_colors[record.levelno]
                if levelcolor in self.colors:
                    levelcolor = self.colors[levelcolor]
                data["levelcolor"] = levelcolor

        return data

    def format(self, record: logging.LogRecord):
        format_map = defaultdict()
        format_map.update(self.get_format_values_dictionary(record))

        return self.log_format % format_map


def create_logger(logger_name: str = None, log_level: Union[str, int] = None):
    logger_name = logger_name or "bole-log-" + create_random_string()
    log = logging.getLogger(logger_name)

    log_level = resolve_log_level(log_level or os.environ.get("LOG_LEVEL", "INFO"))
    log.setLevel(log_level)

    formatter = BoleLogFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log


log = create_logger("bole-log-core")

if __name__ == "__main__":
    log.debug("aadsad")
    log.critical("asd")
    log.warning("Lama")
    log.error("asdsad")
    log.info("Test ")
