from abc import ABC, abstractmethod
from datetime import date

from listens.definitions import SunlightWindow


class SunlightGateway(ABC):

    @abstractmethod
    def fetch_sunlight_window(self, iana_timezone: str, on_date: date) -> SunlightWindow:
        ...
