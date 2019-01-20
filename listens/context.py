from typing import NamedTuple


from listens.abc import (
    DbGateway as DbGatewayABC,
    MusicGateway as MusicGatewayABC,
    NotificationGateway as NotificationGatewayABC,
    SunlightGateway as SunlightGatewayABC
)


class Context(NamedTuple):
    db_gateway: DbGatewayABC
    music_gateway: MusicGatewayABC
    notification_gateway: NotificationGatewayABC
    sunlight_gateway: SunlightGatewayABC
