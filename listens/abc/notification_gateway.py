from abc import ABC, abstractmethod

from listens.definitions import Listen


class NotificationGateway(ABC):

    @abstractmethod
    def announce_listen_added(self, listen: Listen) -> None:
        ...
