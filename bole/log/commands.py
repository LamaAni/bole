import os
import logging
from typing import Union
from bole.log.logger import BoleLogger
from bole.utils import create_random_string, resolve_log_level
from bole.log.formatter import BoleLogFormatter


def create_logger(
    logger_name: str = None,
    log_level: Union[str, int] = None,
):
    """Create a new bole logger, given a logger name.

    Args:
        logger_name (str, optional): The name of the new logger. Defaults to None.
        log_level (Union[str, int], optional): Logger log level. Defaults to None.

    Returns:
        Logger: The new logger
    """
    logger_name = logger_name or "bole-log-" + create_random_string()
    log = BoleLogger(logger_name)

    log_level = resolve_log_level(log_level or os.environ.get("LOG_LEVEL", "INFO"))
    log.setLevel(log_level)

    formatter = BoleLogFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log
