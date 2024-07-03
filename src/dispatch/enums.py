from enum import Enum


class DispatchEnum(str, Enum):
    """
    A custom Enum class that extends str and Enum.

    This class provides additional functionality to standard Enums,
    including string representation and containment checking.

    Attributes:
        Inherits all attributes from str and Enum.

    Example:
        class MyEnum(DispatchEnum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        assert str(MyEnum.VALUE1) == "value1"
        assert "value1" in MyEnum
    """

    def __str__(self) -> str:
        """
        Returns the string representation of the enum value.

        This method allows the enum values to be used as strings directly.

        Returns:
            str: The string value of the enum member.

        Example:
            >>> class MyEnum(DispatchEnum):
            ...     VALUE = "some_value"
            >>> str(MyEnum.VALUE)
            'some_value'
        """
        return str.__str__(self)

    @classmethod
    def __contains__(cls, item: str) -> bool:
        """
        Checks if a string value is present in the enum.

        This method allows for easy checking if a string is a valid enum value.

        Args:
            item (str): The string to check for presence in the enum.

        Returns:
            bool: True if the string is a value in the enum, False otherwise.

        Example:
            >>> class MyEnum(DispatchEnum):
            ...     VALUE = "some_value"
            >>> "some_value" in MyEnum
            True
            >>> "other_value" in MyEnum
            False
        """
        return item in cls.__members__.values()


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
    query = "Query"
    search_filter = "SearchFilter"
    case = "Case"
    service = "Service"
    source = "Source"
    tag = "Tag"
    task = "Task"
    team_contact = "TeamContact"
    term = "Term"


class UserRoles(DispatchEnum):
    owner = "Owner"
    manager = "Manager"
    admin = "Admin"
    member = "Member"


class DocumentResourceTypes(DispatchEnum):
    case = "dispatch-case-document"
    executive = "dispatch-executive-report-document"
    incident = "dispatch-incident-document"
    review = "dispatch-incident-review-document"
    tracking = "dispatch-incident-sheet"


class DocumentResourceReferenceTypes(DispatchEnum):
    conversation = "dispatch-conversation-reference-document"
    faq = "dispatch-incident-reference-faq-document"


class DocumentResourceTemplateTypes(DispatchEnum):
    case = "dispatch-case-document-template"
    executive = "dispatch-executive-report-document-template"
    incident = "dispatch-incident-document-template"
    review = "dispatch-incident-review-document-template"
    tracking = "dispatch-incident-sheet-template"


class EventType(DispatchEnum):
    other = "Other"  # default and catch-all (x resource created/updated, etc.)
    field_updated = "Field updated"  # for fields like title, description, tags, type, etc.
    assessment_updated = "Assessment updated"  # for priority, status, or severity changes
    participant_updated = "Participant updated"  # for added/removed users and role changes
    imported_message = "Imported message"  # for stopwatch-reacted messages from Slack
    custom_event = "Custom event"  # for user-added events (new feature)


class SubjectNames(DispatchEnum):
    CASE = "Case"
    INCIDENT = "Incident"
    SIGNAL = "Signal"
