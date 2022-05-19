from typing import Type, Union


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
