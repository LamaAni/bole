import os


def is_show_full_errors():
    return os.environ.get("SHOW_FULL_ERRORS", "false").strip().lower() == "true"


def mark_show_full_errors(val: bool = True):
    assert val is not None
    os.environ["SHOW_FULL_ERRORS"] = str(val).lower()
