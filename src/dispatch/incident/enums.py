from enum import Enum


class IncidentStatus(str, Enum):
    active = "Active"
    stable = "Stable"
    closed = "Closed"


class IncidentSlackViewBlockId(str, Enum):
    title = "title_field"
    description = "description_field"
    type = "incident_type_field"
    priority = "incident_priority_field"


class NewIncidentSubmission(str, Enum):
    form_slack_view = "submit-new-incident-form-from-slack"
