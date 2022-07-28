from dispatch.enums import DispatchEnum


class CaseStatus(DispatchEnum):
    new = "New"
    triage = "Triage"
    active = "Active"
    stable = "Stable"
    closed = "Closed"
