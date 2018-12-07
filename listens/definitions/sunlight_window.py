from datetime import datetime
from typing import NamedTuple


class SunlightWindow(NamedTuple):
    sunrise_utc: datetime
    sunset_utc: datetime
