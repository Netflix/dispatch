from enum import Enum


class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"

    def __str__(self) -> str:
        return str.__str__(self)


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

    def __str__(self) -> str:
        return str.__str__(self)


class UserRoles(str, Enum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"

    def __str__(self) -> str:
        return str.__str__(self)


class DocumentResourceTypes(str, Enum):
    executive = "dispatch-executive-report-document"
    review = "dispatch-incident-review-document"
    tracking = "dispatch-incident-sheet"
    incident = "dispatch-incident-document"

    def __str__(self) -> str:
        return str.__str__(self)


class DocumentResourceReferenceTypes(str, Enum):
    faq = "dispatch-incident-reference-faq-document"
    conversation = "dispatch-conversation-reference-document"

    def __str__(self) -> str:
        return str.__str__(self)


class DocumentResourceTemplateTypes(str, Enum):
    executive = "dispatch-executive-report-document-template"
    review = "dispatch-incident-review-document-template"
    tracking = "dispatch-incident-sheet-template"
    incident = "dispatch-incident-document-template"

    def __str__(self) -> str:
        return str.__str__(self)
