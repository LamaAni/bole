import os
import re
from typing import List

CONFIG_SEARCH_PATHS: List[str] = re.split(r"[\s,]+", os.environ.get("CONFIG_SEARCH_PATHS", "config.yaml config.json"))
"""A collection of default config search paths (comma or space separated) where the configuration
may exist. Can be an absolute or relative path. If multiple configuration file
names exist, the first file will be taken.
"""


def is_show_full_errors():
    return os.environ.get("SHOW_FULL_ERRORS", "false").strip().lower() == "true"


def mark_show_full_errors(val: bool = True):
    assert val is not None
    os.environ["SHOW_FULL_ERRORS"] = str(val).lower()
