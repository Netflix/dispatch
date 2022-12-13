from typing import List
from blockkit import (
    PlainTextInput,
    StaticSelect,
    PlainOption,
    Input,
    DatePicker,
    MultiExternalSelect,
)

from dispatch.enums import DispatchEnum
from dispatch.database.core import SessionLocal
from dispatch.project import service as project_service
from dispatch.participant.models import Participant
from dispatch.case.enums import CaseStatus
from dispatch.case.type import service as case_type_service
from dispatch.case.priority import service as case_priority_service
from dispatch.case.severity import service as case_severity_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.type import service as incident_type_service
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.severity import service as incident_severity_service


class DefaultBlockIds(DispatchEnum):
    title_input = "title-input"
    project_select = "project-select"
    description_input = "description-input"
    resolution_input = "resolution-input"
    datetime_picker_input = "datetime-picker-input"
    date_picker_input = "date-picker-input"
    minute_picker_input = "minute-picker-input"
    hour_picker_input = "hour-picker-input"
    timezone_picker_input = "timezone-picker-input"

    # incidents
    incident_priority_select = "incident-priority-select"
    incident_status_select = "incident-status-select"
    incident_severity_select = "incident-severity-select"
    incident_type_select = "incident-type-select"

    # cases
    case_priority_select = "case-priority-select"
    case_status_select = "case-status-select"
    case_severity_select = "case-severity-select"
    case_type_select = "case-type-select"

    participant_select = "participant-select"
    tags_multi_select = "tag-multi-select"


class DefaultActionIds(DispatchEnum):
    title_input = "title-input"
    project_select = "project-select"
    description_input = "description-input"
    resolution_input = "resolution-input"
    datetime_picker_input = "datetime-picker-input"
    date_picker_input = "date-picker-input"
    minute_picker_input = "minute-picker-input"
    hour_picker_input = "hour-picker-input"
    timezone_picker_input = "timezone-picker-input"

    # incidents
    incident_priority_select = "incident-priority-select"
    incident_status_select = "incident-status-select"
    incident_severity_select = "incident-severity-select"
    incident_type_select = "incident-type-select"

    # cases
    case_priority_select = "case-priority-select"
    case_status_select = "case-status-select"
    case_severity_select = "case-severity-select"
    case_type_select = "case-type-select"

    participant_select = "participant-select"
    tags_multi_select = "tag-multi-select"


class TimezoneOptions(DispatchEnum):
    local = "Local Time (based on your slack profile)"
    utc = "Coordinated Universal Time (UTC)"


def date_picker_input(
    action_id: str = DefaultActionIds.date_picker_input,
    block_id: str = DefaultBlockIds.date_picker_input,
    initial_date: str = None,
    label: str = "Date",
    **kwargs,
):
    """Builds a date picker input."""
    return Input(
        element=DatePicker(
            action_id=action_id, initial_date=initial_date, placeholder="Select Date"
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


def hour_picker_input(
    action_id: str = DefaultActionIds.hour_picker_input,
    block_id: str = DefaultBlockIds.hour_picker_input,
    initial_option: dict = None,
    label: str = "Hour",
    **kwargs,
):
    """Builds a hour picker input."""
    hours = [{"text": str(h).zfill(2), "value": str(h).zfill(2)} for h in range(0, 24)]
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        options=hours,
        label=label,
        placeholder="Hour",
    )


def minute_picker_input(
    action_id: str = DefaultActionIds.minute_picker_input,
    block_id: str = DefaultBlockIds.minute_picker_input,
    initial_option: dict = None,
    label: str = "Minute",
    **kwargs,
):
    """Builds a minute picker input."""
    minutes = [{"text": str(m).zfill(2), "value": str(m).zfill(2)} for m in range(0, 60)]
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        options=minutes,
        label=label,
        placeholder="Minute",
    )


def timezone_picker_input(
    action_id: str = DefaultActionIds.timezone_picker_input,
    block_id: str = DefaultBlockIds.timezone_picker_input,
    initial_option: dict = {
        "text": TimezoneOptions.local.value,
        "value": TimezoneOptions.local.value,
    },
    label: str = "Timezone",
    **kwargs,
):
    """Builds a timezone picker input."""
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        options=[{"text": tz.value, "value": tz.value} for tz in TimezoneOptions],
        label=label,
        placeholder="Timezone",
    )


def datetime_picker_block(
    action_id: str = None,
    block_id: str = None,
    initial_option: str = None,
    label: str = None,
    **kwargs,
):
    """Builds a datetime picker block"""
    return [
        date_picker_input(),
        hour_picker_input(),
        minute_picker_input(),
        timezone_picker_input(),
    ]


def static_select_block(
    options: List[str],
    placeholder: str,
    action_id: str = None,
    block_id: str = None,
    initial_option: dict = None,
    label: str = None,
    **kwargs,
):
    """Builds a static select block."""
    return Input(
        element=StaticSelect(
            placeholder=placeholder,
            options=[PlainOption(**x) for x in options],
            initial_option=PlainOption(**initial_option) if initial_option else None,
            action_id=action_id,
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


def project_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.project_select,
    block_id: str = DefaultBlockIds.project_select,
    label: str = "Project",
    initial_option: dict = None,
    **kwargs,
):
    """Creates a project select."""
    projects = [
        {"text": p.name, "value": p.id} for p in project_service.get_all(db_session=db_session)
    ]
    return static_select_block(
        placeholder="Select Project",
        options=projects,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def title_input(
    label: str = "Title",
    action_id: str = DefaultActionIds.title_input,
    block_id: str = DefaultBlockIds.title_input,
    initial_value: str = None,
    **kwargs,
):
    """Builds a title input."""
    return Input(
        element=PlainTextInput(
            placeholder="A brief explanatory title. You can change this later.",
            initial_value=initial_value,
            action_id=action_id,
        ),
        label=label,
        block_id=block_id,
        **kwargs,
    )


def description_input(
    label: str = "Description",
    action_id: str = DefaultActionIds.description_input,
    block_id: str = DefaultBlockIds.description_input,
    initial_value: str = None,
    **kwargs,
):
    """Builds a description input."""
    return Input(
        element=PlainTextInput(
            placeholder="A summary of what you know so far. It's okay if this is incomplete.",
            initial_value=initial_value,
            multiline=True,
            action_id=action_id,
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


def resolution_input(
    label: str = "Resolution",
    action_id: str = DefaultActionIds.resolution_input,
    block_id: str = DefaultBlockIds.resolution_input,
    initial_value: str = None,
    **kwargs,
):
    """Builds a resolution input."""
    return Input(
        element=PlainTextInput(
            placeholder="A description of the actions you have taken toward resolution.",
            initial_value=initial_value,
            multiline=True,
            action_id=action_id,
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


def incident_priority_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.incident_priority_select,
    block_id: str = DefaultBlockIds.incident_priority_select,
    label: str = "Incident Priority",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates a incident priority select."""
    priorities = [
        {"text": p.name, "value": p.id}
        for p in incident_priority_service.get_all_enabled(
            db_session=db_session, project_id=project_id
        )
    ]
    return static_select_block(
        placeholder="Select Priority",
        options=priorities,
        initial_option=initial_option,
        block_id=block_id,
        action_id=action_id,
        label=label,
        **kwargs,
    )


def incident_status_select(
    block_id: str = DefaultActionIds.incident_status_select,
    action_id: str = DefaultBlockIds.incident_status_select,
    label: str = "Incident Status",
    initial_option: dict = None,
    **kwargs,
):
    """Creates an incident status select."""
    statuses = [{"text": s.value, "value": s.value} for s in IncidentStatus]
    return static_select_block(
        placeholder="Select Status",
        options=statuses,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def incident_severity_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.incident_severity_select,
    block_id: str = DefaultBlockIds.incident_severity_select,
    label="Incident Severity",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates an incident severity select."""
    severities = [
        {"text": s.name, "value": s.id}
        for s in incident_severity_service.get_all_enabled(
            db_session=db_session, project_id=project_id
        )
    ]
    return static_select_block(
        placeholder="Select Severity",
        options=severities,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def incident_type_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.incident_type_select,
    block_id: str = DefaultBlockIds.incident_type_select,
    label="Incident Type",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates an incident type select."""
    types = [
        {"text": t.name, "value": t.id}
        for t in incident_type_service.get_all_enabled(db_session=db_session, project_id=project_id)
    ]
    return static_select_block(
        placeholder="Select Type",
        options=types,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def tag_multi_select(
    action_id: str = DefaultActionIds.tags_multi_select,
    block_id: str = DefaultBlockIds.tags_multi_select,
    label="Tags",
    initial_options: str = None,
    **kwargs,
):
    """Creates an incident tag select."""
    return Input(
        element=MultiExternalSelect(
            placeholder="Select Tag(s)", action_id=action_id, initial_options=initial_options
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


def case_priority_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.case_priority_select,
    block_id: str = DefaultBlockIds.case_priority_select,
    label="Case Priority",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates a case priority select."""
    priorities = [
        {"text": p.name, "value": p.id}
        for p in case_priority_service.get_all_enabled(db_session=db_session, project_id=project_id)
    ]
    return static_select_block(
        placeholder="Select Priority",
        options=priorities,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def case_status_select(
    action_id: str = DefaultActionIds.case_status_select,
    block_id: str = DefaultBlockIds.case_status_select,
    label: str = "Status",
    initial_option: dict = None,
    **kwargs,
):
    """Creates a case status select."""
    statuses = [{"text": str(s), "value": str(s)} for s in CaseStatus]
    return static_select_block(
        placeholder="Select Status",
        options=statuses,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def case_severity_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.case_severity_select,
    block_id: str = DefaultBlockIds.case_severity_select,
    label: str = "Case Severity",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates an case severity select."""
    severities = [
        {"text": s.name, "value": s.id}
        for s in case_severity_service.get_all_enabled(db_session=db_session, project_id=project_id)
    ]
    return static_select_block(
        placeholder="Select Severity",
        options=severities,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def case_type_select(
    db_session: SessionLocal,
    action_id: str = DefaultActionIds.case_type_select,
    block_id: str = DefaultBlockIds.case_type_select,
    label: str = "Case Type",
    initial_option: dict = None,
    project_id: int = None,
    **kwargs,
):
    """Creates an case type select."""
    types = [
        {"text": t.name, "value": t.id}
        for t in case_type_service.get_all_enabled(db_session=db_session, project_id=project_id)
    ]
    return static_select_block(
        placeholder="Select Type",
        options=types,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )


def participant_select(
    participants: List[Participant],
    action_id: str = DefaultActionIds.participant_select,
    block_id: str = DefaultBlockIds.participant_select,
    label: str = "Participant",
    initial_option: Participant = None,
    **kwargs,
):
    """Creates a static select of available participants."""
    participants = [{"text": p.individual.name, "value": p.individual.id} for p in participants]
    return static_select_block(
        placeholder="Select Participant",
        options=participants,
        initial_option=initial_option,
        action_id=action_id,
        block_id=block_id,
        label=label,
        **kwargs,
    )
