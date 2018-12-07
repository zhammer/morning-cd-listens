from typing import NamedTuple

from listens.gateways.db import DbGatewayABC
from listens.gateways.music import MusicGatewayABC
from listens.gateways.sunlight import SunlightGatewayABC


class Context(NamedTuple):
    db_gateway: DbGatewayABC
    music_gateway: MusicGatewayABC
    sunlight_gateway: SunlightGatewayABC
