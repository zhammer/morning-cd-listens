import json
import os
from datetime import datetime
from typing import Dict, Generator
from unittest.mock import patch

from faaspact_verifier import always, faasport, provider_state
from faaspact_verifier.definitions import Request, Response

import responses

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from listens.definitions import MusicProvider
from listens.delivery.aws_lambda.rest import handler
from listens.gateways.db.sqlalchemy import models


DATABASE_CONNECTION_STRING = os.environ.get(
    'TEST_DATABASE_CONNECTION_STRING',
    'sqlite:///morning_cd_behave_tests.db'
)


@always
def always_() -> Generator:
    engine = create_engine(DATABASE_CONNECTION_STRING)
    session = sessionmaker(bind=engine)()
    session.close_all()
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)

    mock_env = {
        'DATABASE_CONNECTION_STRING': DATABASE_CONNECTION_STRING,
        'SUNLIGHT_SERVICE_API_KEY': 'mock sunlight service api key',
        'SPOTIFY_CLIENT_ID': 'mock spotify client id',
        'SPOTIFY_CLIENT_SECRET': 'mock spotify_client_secret'
    }
    with patch.dict(os.environ, mock_env):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, 'https://accounts.spotify.com/api/token',
                     json={'access_token': 'fake access token'})
            yield


@provider_state('there are no listens in the database')
def no_listens_in_db() -> Generator:
    yield


@provider_state('a listen exists with the fields')
def a_listen_exists(fields: Dict) -> Generator:
    default_listen_fields = {
        'song_id': '3DnZfpfe8wLeJgzc00gKeW',
        'song_provider': 'SPOTIFY',
        'listener_name': 'geez',
        'listen_time_utc': '2018-12-02T10:27:47',
        'note': 'this album isnt bad',
        'iana_timezone': 'Europe/Moscow'
    }
    merged_fields = {**default_listen_fields, **fields}
    merged_fields['listen_time_utc'] = datetime.fromisoformat(  # type: ignore
        merged_fields['listen_time_utc']
    ).replace(tzinfo=None)
    merged_fields['song_vendor'] = MusicProvider[merged_fields.pop('song_provider')]  # type: ignore

    sql_listen = models.SqlListen(**merged_fields)

    engine = create_engine(DATABASE_CONNECTION_STRING)
    session = sessionmaker(bind=engine)()
    session.add(sql_listen)
    session.commit()
    session.close()

    yield


@faasport
def port(request: Request) -> Response:
    event = _build_aws_event(request)
    aws_response = handler(event, {})
    return _pluck_response(aws_response)


def _build_aws_event(request: Request) -> Dict:
    query_params = ({field: value[0] for field, value in request.query.items()}
                    if request.query else {})
    return {
        'headers': request.headers,
        'path': request.path,
        'httpMethod': request.method,
        'body': request.body,
        'pathParameters': {'id': request.path.split('/')[-1]},
        'queryStringParameters': query_params
    }


def _pluck_response(aws_response: Dict) -> Response:
    if 'body' in aws_response:
        body = json.loads(aws_response['body'])
    else:
        body = None

    return Response(
        headers=aws_response.get('headers', {}),
        status=aws_response['statusCode'],
        body=body
    )
