import logging
import traceback
from collections import defaultdict
from typing import Dict, List, Union, Any
from bole.utils import datetime_to_iso
from bole.log.consts import (
    NO_COLOR,
    BOLE_LOG_FORMAT,
    EXCEPTION_FIELDS,
    COLORS,
    LEVEL_COLORS,
    ALT_LEVEL_NAMES,
)


class BoleLogFormatter(logging.Formatter):
    def __init__(
        self,
        log_format: str = BOLE_LOG_FORMAT,
        colors: Dict[str, str] = COLORS,
        level_colors: Dict[int, str] = LEVEL_COLORS,
        use_colors: bool = not NO_COLOR,
        alt_level_names: Dict[str, str] = ALT_LEVEL_NAMES,
        exception_fields: List[str] = EXCEPTION_FIELDS,
        allow_missing_values: bool = True,
    ) -> None:
        """Bole log formatter. Used to create consistent logs

        Args:
            log_format (str, optional): The log format. Defaults to BOLE_LOG_FORMAT.
            colors (Dict[str, str], optional): The log format colors. Defaults to COLORS.
            level_colors (Dict[int, str], optional): The log level colors mapping. Defaults to LEVEL_COLORS.
            use_colors (bool, optional): If ture, use colors. Defaults to [not NO_COLOR].
            alt_level_names (Dict[str, str], optional): Replace log level names with other names.
                Defaults to ALT_LEVEL_NAMES.
            exception_fields (List[str], optional): Add the exception text, if provided, to the message.
                (will not add logging context)
        """
        super().__init__()
        self.log_format = log_format
        self.colors = colors or {}
        self.level_colors = level_colors or {}
        self.use_colors = use_colors is True
        self.alt_level_names = alt_level_names or {}
        self.exception_fields = exception_fields or []
        self.allow_missing_values = allow_missing_values is True

    def get_log_values_dictionary(self, data: Union[str, dict, Any]):
        if isinstance(data, str):
            data = {"msg": data}
        elif not isinstance(data, dict):
            # Must have a dict attribute
            data = data.__dict__

        if "timestamp" not in data:
            data["timestamp"] = datetime_to_iso()

        levelname = data.get("levelname", None)

        if levelname is not None and levelname in self.alt_level_names:
            data["levelname"] = self.alt_level_names[levelname]

        if self.use_colors:
            data.update(self.colors)
            levelno = data.get("levelno")
            if levelno in self.level_colors:
                levelcolor = self.level_colors[levelno]
                if levelcolor in self.colors:
                    levelcolor = self.colors[levelcolor]
                data["levelcolor"] = levelcolor

        return data

    def format_log_message(
        self,
        data: Union[str, dict, Any],
        log_format: str = None,
    ):
        format_map = self.get_log_values_dictionary(data)
        if self.allow_missing_values:
            format_map = defaultdict(lambda: "", format_map)

        log_format = log_format if log_format is not None else self.log_format

        exception_lines = []

        # Adding exception info

        if self.exception_fields is not None and len(self.exception_fields) > 0:
            for ef in self.exception_fields:
                try:
                    ef_val = format_map.get(ef, None)
                    if ef_val is None:
                        continue

                    if isinstance(ef_val, tuple):
                        ef_val = ef_val[1]
                        if isinstance(ef_val, TypeError):
                            ef_val = f"(Skipped) Error info was skipped: {ef_val}"
                        if isinstance(ef_val, Exception):
                            ef_val = "\n".join(
                                traceback.format_exception(type(ef_val), value=ef_val, tb=ef_val.__traceback__)
                            )

                    exception_lines.append(str(ef_val))
                except TypeError as ex:
                    exception_lines.append(str(ex))

            if len(exception_lines) > 0:
                if "%(exc_text)s" not in log_format:
                    log_format += "\n%(exc_text)s"
                format_map["exc_text"] = "\n".join(exception_lines)

        return log_format % format_map

    def format(
        self,
        record: logging.LogRecord,
        log_format: str = None,
    ):
        return self.format_log_message(
            record,
            log_format=log_format,
        )
