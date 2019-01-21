from datetime import datetime
from typing import List, Optional

import pytest

from listens.definitions import ListenInput, MusicProvider
from listens.entities.listen import check_invalid


class TestCheckInvalid:

    @pytest.mark.parametrize('listener_name, invalid_fields', [  # type: ignore
        pytest.param('a' * 31, ['listener_name'], id='one over max'),
        pytest.param('a' * 30, None, id='at max'),
        pytest.param('a' * 29, None, id='one under max')
    ])
    def test_checks_name_length(self,
                                listener_name: str,
                                invalid_fields: Optional[List[str]]) -> None:
        # Given
        listen_input = listen_input_factory(listener_name=listener_name)

        # When
        invalid_reason = check_invalid(listen_input)

        # Then
        if invalid_fields:
            assert invalid_reason
            assert invalid_fields == list(invalid_reason['error_message_by_field'].keys())
        else:
            assert invalid_fields is None

    @pytest.mark.parametrize('note, invalid_fields', [  # type: ignore
        pytest.param('a' * 101, ['note'], id='one over max'),
        pytest.param('a' * 100, None, id='at max'),
        pytest.param('a' * 99, None, id='one under max')
    ])
    def test_checks_note_length(self,
                                note: str,
                                invalid_fields: Optional[List[str]]) -> None:
        # Given
        listen_input = listen_input_factory(note=note)

        # When
        invalid_reason = check_invalid(listen_input)

        # Then
        if invalid_fields:
            assert invalid_reason
            assert invalid_fields == list(invalid_reason['error_message_by_field'].keys())
        else:
            assert invalid_fields is None

    def test_invalidates_multiple_fields_in_one_pass(self) -> None:
        # Given `listener_name` _and_ `note` are too long
        listener_name = 'a' * 31
        note = 'a' * 101
        listen_input = listen_input_factory(note=note, listener_name=listener_name)

        # When
        invalid_reason = check_invalid(listen_input)

        # Then `listener_name` and `note` are returned as invalid fields.
        assert invalid_reason
        assert ['note', 'listener_name'] == list(invalid_reason['error_message_by_field'].keys())


def listen_input_factory(*,
                         listener_name: Optional[str] = None,
                         note: Optional[str] = None) -> ListenInput:
    return ListenInput(
        song_id='0aq7ohTG6VDYQvsnAYtA5e',
        song_provider=MusicProvider.SPOTIFY,
        listener_name=listener_name if listener_name is not None else 'geez',
        listen_time_utc=datetime(2018, 11, 12, 5, 53, 38),
        note=note,
        iana_timezone='Asia/Tokyo'
    )
