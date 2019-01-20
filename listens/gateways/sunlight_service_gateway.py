from datetime import date, datetime
from typing import Dict

import requests

from listens.abc import SunlightGateway as SunlightGatewayABC
from listens.definitions import SunlightWindow, exceptions


class SunlightServiceGateway(SunlightGatewayABC):
    endpoint = 'https://micro.morningcd.com/sunlight'

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch_sunlight_window(self, iana_timezone: str, on_date: date) -> SunlightWindow:
        r = requests.get(
            self.endpoint,
            params={
                'iana_timezone': iana_timezone,
                'on_date': on_date.isoformat()
            },
            headers={'x-api-key': self.api_key}
        )

        if not r.status_code == requests.codes.ok:
            try:
                message = r.json()['message']
            except (KeyError, ValueError):
                message = ''
            raise exceptions.SunlightServiceError(message)

        return _pluck_sunlight_window(r.json())


def _pluck_sunlight_window(raw_sunlight_window: Dict) -> SunlightWindow:
    return SunlightWindow(
        sunrise_utc=_pluck_datetime(raw_sunlight_window['sunrise_utc']),
        sunset_utc=_pluck_datetime(raw_sunlight_window['sunset_utc'])
    )


def _pluck_datetime(raw_datetime: str) -> datetime:
    return datetime.fromisoformat(raw_datetime).replace(tzinfo=None)
