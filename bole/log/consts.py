import logging
import os

NO_COLOR = (
    os.environ.get("NO_COLOR", "false").lower() == "true" or os.environ.get("NO_COLORS", "false").lower() == "true"
)
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

EXCEPTION_FIELDS = [
    "exc_info",
    "exc_text",
    "exception",
]

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
