from typing import NamedTuple

from listens.gateways.db import DbGatewayABC
from listens.gateways.music import MusicGatewayABC
from listens.gateways.notification_gateway_abc import NotificationGateway as NotificationGatewayABC
from listens.gateways.sunlight import SunlightGatewayABC


class Context(NamedTuple):
    db_gateway: DbGatewayABC
    music_gateway: MusicGatewayABC
    notification_gateway: NotificationGatewayABC
    sunlight_gateway: SunlightGatewayABC
