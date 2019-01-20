from typing import Dict

from mypy_extensions import TypedDict


class InvalidReason(TypedDict):
    error_message_by_field: Dict[str, str]
