from enum import Enum


class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(str, Enum):
    term = "Term"
    definition = "Definition"
    individual_contact = "IndividualContact"
    team_contact = "TeamContact"
    service = "Service"
    policy = "Policy"
    tag = "Tag"
    task = "Task"
    document = "Document"
    plugin = "Plugin"
    incident_priority = "IncidentPriority"
    incident_type = "IncidentType"
    incident = "Incident"


class UserRoles(str, Enum):
    user = "User"
    poweruser = "Poweruser"
    admin = "Admin"
