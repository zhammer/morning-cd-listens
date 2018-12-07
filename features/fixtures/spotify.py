from responses import Response


def make_post_client_credentials() -> Response:
    return Response(
        method='POST',
        url='https://accounts.spotify.com/api/token',
        json={
            'access_token': 'MockSpotifyAccessToken',
            'token_type': 'bearer',
            'expires_in': 3600
        }
    )


def make_get_track_whispers_request() -> Response:
    return Response(
        method='GET',
        url='https://api.spotify.com/v1/tracks/4rNGLh1y5Kkvr4bT28yfHU'
    )
