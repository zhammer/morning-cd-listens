from datetime import datetime
from typing import List, Optional

from listens.context import Context
from listens.definitions import Listen, ListenInput, SortOrder
from listens.definitions.exceptions import (
    InvalidSongError,
    SunlightError
)
from listens.entities import day as day_entity


def get_listen(context: Context, listen_id: str) -> Listen:
    return context.db_gateway.fetch_listen(listen_id)


def get_listens(context: Context,
                limit: int,
                sort_order: SortOrder,
                before_utc: Optional[datetime] = None,
                after_utc: Optional[datetime] = None) -> List[Listen]:
    return context.db_gateway.fetch_listens(
        before_utc=before_utc,
        after_utc=after_utc,
        sort_time=sort_order,
        limit=limit
    )


def submit_listen(context: Context, listen_input: ListenInput) -> Listen:
    """Submit a Listen to the database."""
    if not context.music_gateway.song_exists(listen_input.song_id, listen_input.song_provider):
        raise InvalidSongError(f'Song {listen_input.song_id} doesnt exist.')

    sunlight_window = context.sunlight_gateway.fetch_sunlight_window(
        iana_timezone=listen_input.iana_timezone,
        on_date=day_entity.local_date(listen_input.listen_time_utc, listen_input.iana_timezone)
    )

    if not day_entity.is_day(listen_input.listen_time_utc, sunlight_window):
        raise SunlightError('Listens can only be submitted during the day.')

    listen = context.db_gateway.add_listen(listen_input)

    context.notification_gateway.announce_listen_added(listen)

    return listen
