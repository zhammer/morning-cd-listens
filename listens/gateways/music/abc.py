from abc import ABC, abstractmethod

from listens.definitions import MusicProvider


class MusicGatewayABC(ABC):

    @abstractmethod
    def song_exists(self, song_id: str, song_provider: MusicProvider) -> bool:
        ...
