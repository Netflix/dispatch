from enum import Enum


class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(str, Enum):
    definition = "Definition"
    document = "Document"
    incident = "Incident"
    incident_priority = "IncidentPriority"
    incident_type = "IncidentType"
    individual_contact = "IndividualContact"
    plugin = "Plugin"
    search_filter = "SearchFilter"
    service = "Service"
    tag = "Tag"
    task = "Task"
    team_contact = "TeamContact"
    term = "Term"


class UserRoles(str, Enum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"


class DocumentResourceTypes(str, Enum):
    faq = "dispatch-incident-faq-document"
    conversation = "dispatch-conversation-reference-document"


class DocumentResourceTemplateTypes(str, Enum):
    executive = "dispatch-executive-report-document-template"
    review = "dispatch-incident-review-document-template"
    tracking = "dispatch-incident-sheet-template"
    incident = "dispatch-incident-document-template"
