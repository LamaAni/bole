import logging
import os
import string
import random
from datetime import datetime
from typing import Type, Union

DEFAULT_RANDOM_STRING_CHARS = string.ascii_letters + string.digits


def resolve_log_level(level_name: Union[str, int]):
    if isinstance(level_name, int):
        return level_name
    level = logging.getLevelName(level_name)
    if isinstance(level, str):
        level = logging.DEBUG
    return level


def create_random_string(count: int = 5, charset: str = DEFAULT_RANDOM_STRING_CHARS):
    return "".join(random.choice(DEFAULT_RANDOM_STRING_CHARS) for i in range(count))


def datetime_to_iso(val: datetime = None):
    val = val or datetime.now()
    as_iso = val.astimezone().replace(microsecond=0).isoformat()
    as_iso = as_iso[:-3] + as_iso[-2:]
    return as_iso


def resolve_path(*path_parts: str, root_directory: str = None):
    """Resolve a path given a root directory"""
    path_parts = [p.strip() for p in path_parts if p is not None and len(p.strip()) > 0]
    assert len(path_parts) > 0, ValueError("You must provide at least one path part")
    root_directory = root_directory or os.curdir
    if not path_parts[0].startswith("/"):
        path_parts = [root_directory] + path_parts
    return os.path.abspath(os.path.join(*path_parts))


def get_same_type(a, b, *types: Type):
    """Returns true of both objects are of the same type

    Args:
        a (Any): First
        b (Any): Second

    Returns:
        bool: True if objects are of the same type.
    """
    for t in types:
        if isinstance(a, t) and isinstance(b, t):
            return t
    return None


def deep_merge(target: Union[dict, list], *sources: Union[dict, list], concatenate_lists: bool = True):
    """Merge dictionaries and lists into a single object.

    Args:
        target (Union[dict, list]): The target to merge into.
    """
    if isinstance(target, list):
        assert all(isinstance(src, list) for src in sources), (
            "Merge target and source must be of the same type (list)",
        )
        # List merges as concat, and dose not merge the internal values.
        if concatenate_lists:
            for src in sources:
                target += src
        else:
            # Attempting to merge list items.
            for src in sources:
                src_len = len(src)
                target_len = len(target)
                max_len = target_len if target_len > src_len else src_len

                for i in range(max_len):
                    if i >= target_len:
                        target[i] = src[i]
                    if i >= src_len:
                        continue
                    merge_type: Type = get_same_type(src[i], target[i], list, dict)
                    if merge_type is None:
                        target[i] = src[i]
                    else:
                        target[i] = deep_merge(merge_type(), target[i], src[i])

        return target

    if isinstance(target, dict):
        assert all(isinstance(src, dict) for src in sources), (
            "Merge target and source must be of the same type (dict)",
        )

        for src in sources:
            for key in src.keys():
                if key not in target:
                    target[key] = src[key]
                    continue
                merge_type = get_same_type(src[i], target[i], list, dict)
                if merge_type is not None:
                    target[key] = deep_merge(merge_type(), target[key], src[key])
                else:
                    target[key] = src[key]
    return target
