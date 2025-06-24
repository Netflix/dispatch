from dispatch.enums import DispatchEnum


class CaseStatus(DispatchEnum):
    new = "New"
    triage = "Triage"
    escalated = "Escalated"
    stable = "Stable"
    closed = "Closed"


class CaseResolutionReason(DispatchEnum):
    benign = "Benign"
    contained = "Contained"
    escalated = "Escalated"
    false_positive = "False Positive"
    information_gathered = "Information Gathered"
    insufficient_information = "Insufficient Information"
    mitigated = "Mitigated"
    operational_error = "Operational Error"
    policy_violation = "Policy Violation"
    user_acknowledged = "User Acknowledged"


class CaseResolutionReasonDescription(DispatchEnum):
    """Descriptions for case resolution reasons."""

    benign = (
        "The event was legitimate but posed no security threat, such as expected behavior "
        "from a known application or user."
    )
    contained = (
        "(True positive) The event was a legitimate threat but was contained to prevent "
        "further spread or damage."
    )
    escalated = "There was enough information to create an incident based on the security event."
    false_positive = "The event was incorrectly flagged as a security event."
    information_gathered = (
        "Used when a case was opened with the primary purpose of collecting information."
    )
    insufficient_information = (
        "There was not enough information to determine the nature of the event conclusively."
    )
    mitigated = (
        "(True Positive) The event was a legitimate security threat and was successfully "
        "mitigated before causing harm."
    )
    operational_error = (
        "The event was caused by a mistake in system configuration or user operation, "
        "not malicious activity."
    )
    policy_violation = (
        "The event was a breach of internal security policies but did not result in a "
        "security incident."
    )
    user_acknowledged = (
        "While the event was suspicious it was confirmed by the actor to be intentional."
    )


class CostModelType(DispatchEnum):
    """Type of cost model used to calculate costs."""

    new = "New"
    classic = "Classic"
