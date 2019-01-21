from datetime import datetime
from typing import NamedTuple, Optional

from listens.definitions import MusicProvider


class Listen(NamedTuple):
    id: str
    song_id: str
    song_provider: MusicProvider
    listener_name: str
    listen_time_utc: datetime
    note: Optional[str]
    iana_timezone: str
