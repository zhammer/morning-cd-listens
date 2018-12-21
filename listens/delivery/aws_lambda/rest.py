import json
import os
import re
from datetime import datetime
from typing import Dict, cast

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from listens.delivery.aws_lambda import util
from listens.use_listens import get_listen, get_listens, submit_listen


if os.environ.get('AWS_EXECUTION_ENV'):
    sentry_sdk.init(
        dsn="https://aaf4d2452f84464cafdc6004d89c1724@sentry.io/1357179",
        integrations=[AwsLambdaIntegration()]
    )


@util.intercept_warmup_events
def handler(event: Dict, context: Dict) -> Dict:
    """Routing all handlers through one aws function means we only have to keep one lambda 'warm'.
    """
    return router(event)(event, context)


@util.catch_listens_service_errors
def submit_listen_handler(event: Dict, context: Dict) -> Dict:
    database_connection_string = os.environ['DATABASE_CONNECTION_STRING']
    sunlight_service_api_key = os.environ['SUNLIGHT_SERVICE_API_KEY']
    spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
    spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    current_time_utc = datetime.utcnow()
    listen_input = util.pluck_listen_input(json.loads(event['body']), current_time_utc)
    listens_context = util.create_default_context(
        database_connection_string,
        sunlight_service_api_key,
        spotify_client_id,
        spotify_client_secret
    )

    submitted_listen = submit_listen(listens_context, listen_input)

    return {
        'statusCode': 200,
        'body': json.dumps(util.build_listen(submitted_listen))
    }


@util.catch_listens_service_errors
def get_listen_handler(event: Dict, context: Dict) -> Dict:
    database_connection_string = os.environ['DATABASE_CONNECTION_STRING']
    sunlight_service_api_key = os.environ['SUNLIGHT_SERVICE_API_KEY']
    spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
    spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    listen_id = cast(str, event['pathParameters']['id'])
    listens_context = util.create_default_context(
        database_connection_string,
        sunlight_service_api_key,
        spotify_client_id,
        spotify_client_secret
    )

    listen = get_listen(listens_context, listen_id)
    return {
        'statusCode': 200,
        'body': json.dumps(util.build_listen(listen))
    }


@util.catch_listens_service_errors
def get_listens_handler(event: Dict, context: Dict) -> Dict:
    database_connection_string = os.environ['DATABASE_CONNECTION_STRING']
    sunlight_service_api_key = os.environ['SUNLIGHT_SERVICE_API_KEY']
    spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
    spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    get_listens_parameters = util.pluck_get_listens_params(event['queryStringParameters'] or {})
    listens_context = util.create_default_context(
        database_connection_string,
        sunlight_service_api_key,
        spotify_client_id,
        spotify_client_secret
    )

    listens = get_listens(listens_context, **get_listens_parameters._asdict())
    return {
        'statusCode': 200,
        'body': json.dumps({'items': [util.build_listen(listen) for listen in listens]})
    }


def router(event: Dict) -> util.AwsHandler:
    """Routes an http event to the correct aws handler based on the event's http method and path.

    >>> router({'httpMethod': 'POST', 'path': '/listens'})
    <function submit_listen_handler at 0x...>

    >>> router({'httpMethod': 'GET', 'path': '/listens'})
    <function get_listens_handler at 0x...>

    >>> router({'httpMethod': 'GET', 'path': '/listens/1b23d'})
    <function get_listen_handler at 0x...>
    """
    if event['httpMethod'] == 'POST' and event['path'] == '/listens':
        return submit_listen_handler

    elif event['httpMethod'] == 'GET' and event['path'] == '/listens':
        return get_listens_handler

    elif event['httpMethod'] == 'GET' and re.match(r'/listens/[\d\w]+', event['path']):
        return get_listen_handler

    else:
        raise RuntimeError('Unexpected event route')
