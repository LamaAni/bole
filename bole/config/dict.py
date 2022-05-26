from typing import Any, Callable, Dict, List, Union
from bole.utils import clean_data_types, find_in_collection


class CascadingConfigDictionary(dict):
    def find(
        self,
        *paths: str,
        action: Callable[[Any, Any], Any] = None,
    ) -> List[Any]:
        """Search the config for specific dictionary paths.
        Paths is a list of string representations of dictionary paths.
        Ex: paths = ['a.b[0].c']

        Args:
            action ((value, parent)=>Any, optional): Action to take when the value is found. Defaults to None.

        Returns:
            List[Any]: The values that were found.
        """
        found = []
        for p in paths:
            val, was_found = find_in_collection(self, path=p, action=action)
            if not was_found:
                continue
            found.append(val)
        return found

    def to_dictionary(self) -> dict:
        """Convert this config to a dictionary"""
        return clean_data_types(self)

    @classmethod
    def parse_dictionary(
        cls,
        val: Dict[str, Union[str, dict]],
        in_place: bool = True,
    ):
        """Helper. Parse value as a Dict[str,cls] were cls is this class.

        Args:
            val (Dict[str, Union[str, dict]]): The value to parse.
            in_place (bool, optional): Replace the items in val. Defaults to True.

        Returns:
            Dict[str,cls]: The parsed dictionary.
        """
        rslt: Dict[str, cls] = val
        if not in_place:
            rslt = {}
        for k, v in val.items():
            rslt[k] = cls.parse(v)
        return rslt

    @classmethod
    def parse_list(
        cls,
        val: List[Union[str, dict]],
        in_place: bool = True,
    ):
        """Helper. Parse value as a List[cls] where cls is this class.

        Args:
            val (List[Union[str, dict]]): The value to parse.
            in_place (bool, optional): Replace the items in the list. Defaults to True.

        Returns:
            List[cls]: The list of items.
        """
        rslt: List[cls] = val
        if not in_place:
            rslt = []
        rslt: List[cls] = []

        for i in range(len(val)):
            v = cls.parse(val[i])
            if len(rslt) <= i:
                rslt.append(v)
            else:
                rslt[i] = cls.parse(v)

        return rslt

    @classmethod
    def parse(
        cls,
        val: Union[dict, List[dict]],
    ):
        """Parse the dict and return the a class"""
        if isinstance(val, cls):
            return val
        if isinstance(val, dict):
            return cls(**val)

        raise ValueError("Invalid value when trying to parse dictionary item")
