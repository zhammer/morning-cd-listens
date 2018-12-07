class ListensServiceException(Exception):
    """Base exception for listens service exceptions."""


class InvalidIanaTimezoneError(ListensServiceException):
    """Exception raised upon encountering an invalid iana timezone."""


class InvalidSongError(ListensServiceException):
    """Exception raised upon attempting to submit a listen with an invalid song."""


class SunlightError(ListensServiceException):
    """Exception raised upon encountering a day action attempted at night."""


class SunlightServiceError(ListensServiceException):
    """Exception raised upon encountering an error with the sunlight service."""


class ListenDoesntExistError(ListensServiceException):
    """Exception raised upon attempting to query a listen that doesnt exist."""
