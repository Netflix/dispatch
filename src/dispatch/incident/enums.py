from dispatch.enums import DispatchEnum


class IncidentStatus(DispatchEnum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"
