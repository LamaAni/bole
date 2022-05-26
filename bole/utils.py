import json
import logging
import os
import re
import string
import random
from datetime import datetime
from typing import Any, Callable, List, Type, Union

DEFAULT_RANDOM_STRING_CHARS = string.ascii_letters + string.digits


def clean_data_types(val):
    return json.loads(json.dumps(val))


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


def deep_merge(
    target: Union[dict, list],
    *sources: Union[dict, list],
    append_lists: bool = True,
    insert_lists: bool = False,
):
    """Merge dictionaries and lists into a single object.

    Args:
        target (Union[dict, list]): The target to merge into.
    """
    if isinstance(target, list):
        assert all(isinstance(src, list) for src in sources), (
            "Merge target and source must be of the same type (list)",
        )
        # List merges as concat, and dose not merge the internal values.
        if append_lists:
            for src in sources:
                target += src
        elif insert_lists:
            sources: list = list(sources)
            sources.reverse()
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
                        target[i] = deep_merge(
                            merge_type(),
                            target[i],
                            src[i],
                            append_lists=append_lists,
                            insert_lists=insert_lists,
                        )

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
                merge_type = get_same_type(src[key], target[key], list, dict)
                if merge_type is not None:
                    target[key] = deep_merge(
                        merge_type(),
                        target[key],
                        src[key],
                        append_lists=append_lists,
                        insert_lists=insert_lists,
                    )
                else:
                    target[key] = src[key]
    return target


COLLECTION_ITEM_PART_REGEX = r"^(.*?)(\[([0-9]*)\]|)$"


def find_in_collection(
    parent: Union[dict, list],
    path: Union[str, List[str]],
    action: Callable[[Any, Any], Any] = None,
):
    """Returns a path within a data collection (list, dict)

    Args:
        val (Union[dict, list]): The value to search
        path (Union[str, List[str]]): The path, parts seperated by '.', eg,
            [22].a.b[33].
            empty parts are ignored '..'
            If a list then . is ignored.
        action((value, parent)=>any, optional): The action to take when found

    Returns:
        (any: The value found, bool: true if the value was found)

    """
    # Path defined as a.b[2].c
    if isinstance(path, str):
        path = path.split(".")

    was_found = False
    item = None

    if len(path) == 0:
        return item, was_found

    cur_item = path[0]
    item_parts = re.match(COLLECTION_ITEM_PART_REGEX, cur_item)
    assert item_parts is not None, f"item parts must match the regex '{COLLECTION_ITEM_PART_REGEX}'"

    item_name = item_parts[1] if len(item_parts[1]) > 0 else None
    list_number = int(item_parts[2][1]) if len(item_parts[2]) > 0 else None

    if item_name is None and list_number is None:
        return find_in_collection(parent, path[1:])

    assert item_name is not None or list_number is not None, "Invalid item path part " + cur_item

    if item_name is not None:
        assert isinstance(parent, dict), f"{cur_item} references a dict value but parent is not a dict"
        if item_name not in parent:
            return None, False
        item = parent.get(item_name)
        was_found = True
    if list_number is not None:
        assert isinstance(parent, list), f"{cur_item} references a list value but parent is not a list"
        if len(parent) <= list_number:
            return None, False
        item = parent[list_number]
        was_found = True

    path = path[1:]
    if len(path) > 0:
        return find_in_collection(item, path)

    if was_found and action is not None:
        item = action(item, parent)

    return item, was_found
