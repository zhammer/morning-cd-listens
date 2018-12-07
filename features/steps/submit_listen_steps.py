import json
import os
from contextlib import contextmanager
from datetime import datetime

from behave import given, then, when

from faaspact_maker import Interaction, PactMaker, RequestWithMatchers, ResponseWithMatchers

from freezegun import freeze_time

import responses

from features.fixtures.spotify import make_get_track_whispers_request, make_post_client_credentials

from listens.definitions import MusicProvider
from listens.delivery.aws_lambda.rest import handler as listens_handler
from listens.gateways.db.sqlalchemy.models import SqlListen


@given('my name is "{name}"')  # noqa: F811
def step_impl(context, name):
    context.name = name


@given('I live in new york')  # noqa: F811
def step_impl(context):
    context.iana_timezone = "America/New_York"


@given('it\'s daytime at 10:30am on November 12th 2018')  # noqa: F811
def step_impl(context):
    context.current_time_utc = datetime(2018, 11, 12, 15, 30)  # utc
    context.is_day = True


@given('it\'s nighttime at 6pm on November 12th 2018')  # noqa: F811
def step_impl(context):
    context.current_time_utc = datetime(2018, 11, 12, 23, 0)  # utc time
    context.is_day = False


@given('the first song I listened to today was \'Whispers\' by DAP The Contract')  # noqa: F811
def step_impl(context):
    context.song_id = '4rNGLh1y5Kkvr4bT28yfHU'


@given('I write the note "{note}"')  # noqa: F811
def step_impl(context, note):
    context.note = note


@when('I submit my listen to morning.cd')  # noqa: F811
def step_impl(context):

    listen_input = {
        'song_id': context.song_id,
        'song_provider': 'SPOTIFY',
        'listener_name': context.name,
        'note': context.note,
        'iana_timezone': context.iana_timezone
    }
    event = {
        'httpMethod': 'POST',
        'path': '/listens',
        'body': json.dumps(listen_input)
    }

    with freeze_time(context.current_time_utc):
        with submit_listen_mock_network(context):
            response = listens_handler(event, {})

    context.response = response


@then('I get a response with my listen from morning.cd')  # noqa: F811
def step_impl(context):
    body = json.loads(context.response['body'])

    expected_body = {
        'id': '1',
        'song_id': context.song_id,
        'song_provider': 'SPOTIFY',
        'listener_name': context.name,
        'listen_time_utc': context.current_time_utc.isoformat(),
        'note': context.note,
        'iana_timezone': context.iana_timezone
    }

    assert body == expected_body


@then('I get an error response that says "{error_message}"')  # noqa: F811
def step_impl(context, error_message):
    body = json.loads(context.response['body'])

    assert error_message in body['message']


@then('I am able to find my listen on morning.cd')  # noqa: F811
def step_impl(context):
    sql_listen = context.session.query(SqlListen).one()

    assert sql_listen.id == 1
    assert sql_listen.song_id == context.song_id
    assert sql_listen.song_vendor == MusicProvider.SPOTIFY
    assert sql_listen.listener_name == context.name
    assert sql_listen.note == context.note
    assert sql_listen.listen_time_utc == context.current_time_utc
    assert sql_listen.iana_timezone == context.iana_timezone


@then('I am NOT able to find my listen on morning.cd')  # noqa: F811
def step_impl(context):
    sql_listens = context.session.query(SqlListen).all()
    assert sql_listens == []


@contextmanager
def submit_listen_mock_network(context):
    pact_dir = os.environ.get('PACT_DIRECTORY', 'pacts')
    pact = PactMaker('listens', 'sunlight', 'https://micro.morningcd.com', pact_directory=pact_dir)
    pact.add_interaction(Interaction(
        description='a request for ga sunlight window',
        request=RequestWithMatchers(
            method='GET',
            path='/sunlight',
            query={
                'iana_timezone': ['America/New_York'],
                'on_date': ['2018-11-12']
            }
        ),
        response=ResponseWithMatchers(
            status=200,
            body={
                'sunrise_utc': '2018-11-12T11:40:04',
                'sunset_utc': '2018-11-12T21:40:26'
            }
        )
    ))

    with responses.RequestsMock() as mock_responses:

        # spotify gateway eagerly fetches client credentials on creation
        mock_responses.add(make_post_client_credentials())

        # we check if the song is valid
        mock_responses.add(make_get_track_whispers_request())

        # we check if it's daytime
        with pact.start_mocking(outer=mock_responses):

            yield mock_responses
