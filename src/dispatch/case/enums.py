from dispatch.enums import DispatchEnum


class CaseStatus(DispatchEnum):
    new = "New"
    triage = "Triage"
    escalated = "Escalated"
    closed = "Closed"
