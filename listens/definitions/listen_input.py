from datetime import datetime
from typing import NamedTuple

from listens.definitions import MusicProvider


class ListenInput(NamedTuple):
    song_id: str
    song_provider: MusicProvider
    listener_name: str
    listen_time_utc: datetime
    note: str
    iana_timezone: str
