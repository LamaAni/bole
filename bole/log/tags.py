import json
import logging
from typing import Callable, Union
from bole.utils import datetime_to_iso


class BoleLogFormatterTag:
    def __init__(
        self,
        key: str,
        value: Union[str, list, dict, int, float],
        color: str = None,
    ) -> None:
        self.key = key
        self.value = value
        self.color = color

    def get_value_string(self):
        value = self.value
        if value is None:
            value = ""
        elif isinstance(value, (dict, list)):
            value = json.dumps(value)
        return value

    def get_value_from_record(self, record: logging.LogRecord, default=None):
        return getattr(record, self.key) if hasattr(record, self.key) else default

    def get_color(self, record: logging.LogRecord):
        return self.color

    def render(self, record: logging.LogRecord):
        return f"{self.key}={self.get_value_string()}"


class BoleLogFormatterTimestampTag(BoleLogFormatterTag):
    def __init__(self, key: str = "timestamp", color: str = None) -> None:
        super().__init__(key, None, color)

    def render(self, record: logging.LogRecord):
        return self.get_value_from_record(record, datetime_to_iso())


class BoleLogFormatterLevelTag(BoleLogFormatterTag):
    def __init__(self, key: str = "loglevel", override_color: str = None) -> None:
        super().__init__(key, None, None)
        self.override_color = override_color

    def get_color(self, record: logging.LogRecord):
        return super().get_color(record)

    def render(self, record: logging.LogRecord):
        return super().render(record)
