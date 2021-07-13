from enum import Enum


class IncidentStatus(str, Enum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"

    def __str__(self) -> str:
        return str.__str__(self)
