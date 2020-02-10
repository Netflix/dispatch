from enum import Enum


class IncidentVisibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class IncidentStatus(str, Enum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"
