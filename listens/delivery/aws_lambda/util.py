import json
from datetime import datetime
from functools import wraps
from typing import Dict, NamedTuple, Optional

from listens.context import Context
from listens.definitions import Listen, ListenInput, MusicProvider, SortOrder, exceptions
from listens.delivery.aws_lambda.types import AwsHandler
from listens.gateways.db import SqlAlchemyDbGateway
from listens.gateways.music import SpotifyGateway
from listens.gateways.notification_gateway import NotificationGateway
from listens.gateways.sunlight import SunlightServiceGateway


class GetListensParams(NamedTuple):
    limit: int
    sort_order: SortOrder
    before_utc: Optional[datetime] = None
    after_utc: Optional[datetime] = None


def create_default_context(db_connection_string: str,
                           sunlight_service_api_key: str,
                           spotify_client_id: str,
                           spotify_client_secret: str,
                           listen_added_topic_arn: str) -> Context:
    return Context(
        db_gateway=SqlAlchemyDbGateway(db_connection_string),
        music_gateway=SpotifyGateway(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        ),
        notification_gateway=NotificationGateway(listen_added_topic_arn),
        sunlight_gateway=SunlightServiceGateway(sunlight_service_api_key)
    )


def pluck_get_listens_params(query_string_parameters: Dict[str, str]) -> GetListensParams:
    limit = int(query_string_parameters.get('limit', 20))
    sort_order = SortOrder[query_string_parameters.get('sort_order', 'ascending').upper()]
    before_utc: Optional[datetime] = None
    if 'before_utc' in query_string_parameters:
        before_utc = _pluck_datetime(query_string_parameters['before_utc'])
    after_utc: Optional[datetime] = None
    if 'after_utc' in query_string_parameters:
        after_utc = _pluck_datetime(query_string_parameters['after_utc'])
    return GetListensParams(limit, sort_order, before_utc, after_utc)


def _pluck_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str).replace(tzinfo=None)


def build_listen(listen: Listen) -> Dict:
    return {
        'id': listen.id,
        'song_id': listen.song_id,
        'song_provider': listen.song_provider.name,
        'listener_name': listen.listener_name,
        'listen_time_utc': listen.listen_time_utc.isoformat(),
        'note': listen.note,
        'iana_timezone': listen.iana_timezone
    }


def pluck_listen_input(raw_listen_input: Dict, current_time_utc: datetime) -> ListenInput:
    return ListenInput(
        song_id=raw_listen_input['song_id'],
        song_provider=MusicProvider[raw_listen_input['song_provider']],
        listener_name=raw_listen_input['listener_name'],
        note=raw_listen_input['note'],
        iana_timezone=raw_listen_input['iana_timezone'],
        listen_time_utc=current_time_utc
    )


def catch_listens_service_errors(func: AwsHandler) -> AwsHandler:

    @wraps(func)
    def inner(event: Dict, context: Dict) -> Dict:
        try:
            return func(event, context)
        except (exceptions.InvalidIanaTimezoneError, exceptions.InvalidSongError) as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': str(e)})
            }
        except exceptions.SunlightError as e:
            return {
                'statusCode': 428,
                'body': json.dumps({'message': str(e)})
            }
        except exceptions.ListenDoesntExistError as e:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': str(e)})
            }
        except Exception:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(traceback.format_exc())
            raise

    return inner
