from dispatch.enums import DispatchEnum

# NOTE: IncidentStatus and CaseStatus could be moved to enums.py and called Status


class CaseStatus(DispatchEnum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"
