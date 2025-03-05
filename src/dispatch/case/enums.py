from dispatch.enums import DispatchEnum


class CaseStatus(DispatchEnum):
    new = "New"
    triage = "Triage"
    escalated = "Escalated"
    closed = "Closed"


class CaseResolutionReason(DispatchEnum):
    false_positive = "False Positive"
    user_acknowledge = "User Acknowledged"
    mitigated = "Mitigated"
    escalated = "Escalated"


class CostModelType(DispatchEnum):
    """Type of cost model used to calculate costs."""

    new = "new"
    classic = "classic"
