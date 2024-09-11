class MfaException(Exception):
    """Base exception for MFA-related errors."""

    pass


class InvalidChallengeError(MfaException):
    """Raised when the challenge is invalid."""

    pass


class UserMismatchError(MfaException):
    """Raised when the challenge doesn't belong to the current user."""

    pass


class ActionMismatchError(MfaException):
    """Raised when the action doesn't match the challenge."""

    pass


class ExpiredChallengeError(MfaException):
    """Raised when the challenge is no longer valid."""

    pass


class InvalidChallengeStateError(MfaException):
    """Raised when the challenge is in an invalid state."""

    pass
