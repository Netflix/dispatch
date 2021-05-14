from enum import Enum


class IncidentStatus(str, Enum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"
