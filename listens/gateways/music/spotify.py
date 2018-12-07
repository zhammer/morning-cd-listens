from typing import cast

import requests

from listens.definitions import MusicProvider
from listens.gateways.music import MusicGatewayABC


class SpotifyGateway(MusicGatewayABC):
    base_url = 'https://api.spotify.com/v1'
    auth_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.bearer_token = SpotifyGateway.fetch_bearer_token(client_id, client_secret)

    def song_exists(self,
                    song_id: str,
                    song_provider: MusicProvider = MusicProvider.SPOTIFY) -> bool:
        r = requests.get(f'{self.base_url}/tracks/{song_id}',
                         headers={'Authorization': f'Bearer {self.bearer_token}'})

        if r.status_code == requests.codes.ok:
            return True

        elif r.status_code in (requests.codes.bad_request, requests.codes.not_found):
            return False

        else:
            raise RuntimeError(f'Unexpected error code from spotify. "{r.status_code}: {r.text}"')

    @staticmethod
    def fetch_bearer_token(client_id: str, client_secret: str) -> str:
        r = requests.post(
            SpotifyGateway.auth_url,
            auth=(client_id, client_secret),
            data={'grant_type': 'client_credentials'}
        )

        return cast(str, r.json()['access_token'])
