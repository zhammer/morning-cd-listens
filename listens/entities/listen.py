from typing import Optional

from listens.definitions import InvalidReason, ListenInput


MAX_NOTE_LENGTH = 100
MAX_NAME_LENGTH = 30


def check_invalid(listen_input: ListenInput) -> Optional[InvalidReason]:
    error_message_by_field = {}
    if listen_input.note and len(listen_input.note) > MAX_NOTE_LENGTH:
        error_message_by_field['note'] = (
            f'note length {len(listen_input.note)} exceeds max: '
            f'{MAX_NOTE_LENGTH}.'
        )
    if len(listen_input.listener_name) > MAX_NAME_LENGTH:
        error_message_by_field['listener_name'] = (
            f'listener_name length {len(listen_input.listener_name)} exceeds max: '
            f'{MAX_NAME_LENGTH}.'
        )

    if error_message_by_field:
        return InvalidReason(error_message_by_field=error_message_by_field)

    return None
