from enum import Enum


class DispatchEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class Visibility(DispatchEnum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(DispatchEnum):
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
    source = "Source"
    query = "Query"
    team_contact = "TeamContact"
    term = "Term"


class UserRoles(DispatchEnum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"


class DocumentResourceTypes(DispatchEnum):
    executive = "dispatch-executive-report-document"
    review = "dispatch-incident-review-document"
    tracking = "dispatch-incident-sheet"
    incident = "dispatch-incident-document"


class DocumentResourceReferenceTypes(DispatchEnum):
    faq = "dispatch-incident-reference-faq-document"
    conversation = "dispatch-conversation-reference-document"


class DocumentResourceTemplateTypes(DispatchEnum):
    executive = "dispatch-executive-report-document-template"
    review = "dispatch-incident-review-document-template"
    tracking = "dispatch-incident-sheet-template"
    incident = "dispatch-incident-document-template"
