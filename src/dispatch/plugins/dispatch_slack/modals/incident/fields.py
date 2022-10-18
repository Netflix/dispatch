import logging
from typing import List

from sqlalchemy.orm import Session

from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import Incident
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.priority.models import IncidentPriority
from dispatch.incident.severity import service as incident_severity_service
from dispatch.incident.severity.models import IncidentSeverity
from dispatch.incident.type import service as incident_type_service
from dispatch.incident.type.models import IncidentType
from dispatch.participant.models import Participant
from dispatch.project import service as project_service
from dispatch.tag.models import Tag

from .enums import (
    IncidentBlockId,
    ReportIncidentCallbackId,
    UpdateParticipantBlockId,
    UpdateParticipantCallbackId,
)


log = logging.getLogger(__name__)


def option_from_template(text: str, value: str):
    """Helper function which generates the option block for modals / views"""
    return {"text": {"type": "plain_text", "text": str(text), "emoji": True}, "value": str(value)}


def status_select_block(initial_option: str = None):
    """Builds the incident status select block"""
    status_options = [option_from_template(text=x.value, value=x.value) for x in IncidentStatus]
    block = {
        "block_id": IncidentBlockId.status,
        "type": "input",
        "label": {"type": "plain_text", "text": "Status"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Status"},
            "options": status_options,
        },
    }
    if initial_option:
        block["element"].update(
            {"initial_option": option_from_template(text=initial_option, value=initial_option)}
        )

    return block


def incident_type_select_block(
    db_session: Session, initial_option: IncidentType = None, project_id: int = None
):
    """Builds the incident type select block."""
    incident_type_options = []
    for incident_type in incident_type_service.get_all_enabled(
        db_session=db_session, project_id=project_id
    ):
        incident_type_options.append(
            option_from_template(text=incident_type.name, value=incident_type.name)
        )
    block = {
        "block_id": IncidentBlockId.type,
        "type": "input",
        "label": {"type": "plain_text", "text": "Type"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Type"},
            "options": incident_type_options,
        },
    }

    if initial_option:
        block["element"].update(
            {
                "initial_option": option_from_template(
                    text=initial_option.name, value=initial_option.name
                )
            }
        )

    return block


def incident_severity_select_block(
    db_session: Session, initial_option: IncidentSeverity = None, project_id: int = None
):
    """Builds the incident severity select block."""
    incident_severity_options = []
    for incident_severity in incident_severity_service.get_all_enabled(
        db_session=db_session, project_id=project_id
    ):
        incident_severity_options.append(
            option_from_template(text=incident_severity.name, value=incident_severity.name)
        )

    block = {
        "block_id": IncidentBlockId.severity,
        "type": "input",
        "label": {"type": "plain_text", "text": "Severity", "emoji": True},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Severity"},
            "options": incident_severity_options,
        },
    }

    if initial_option:
        block["element"].update(
            {
                "initial_option": option_from_template(
                    text=initial_option.name, value=initial_option.name
                )
            }
        )

    return block


def incident_priority_select_block(
    db_session: Session, initial_option: IncidentPriority = None, project_id: int = None
):
    """Builds the incident priority select block."""
    incident_priority_options = []
    for incident_priority in incident_priority_service.get_all_enabled(
        db_session=db_session, project_id=project_id
    ):
        incident_priority_options.append(
            option_from_template(text=incident_priority.name, value=incident_priority.name)
        )

    block = {
        "block_id": IncidentBlockId.priority,
        "type": "input",
        "label": {"type": "plain_text", "text": "Priority", "emoji": True},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Priority"},
            "options": incident_priority_options,
        },
    }

    if initial_option:
        block["element"].update(
            {
                "initial_option": option_from_template(
                    text=initial_option.name, value=initial_option.name
                )
            }
        )

    return block


def project_select_block(db_session: Session, initial_option: dict = None):
    """Builds the incident project select block."""
    project_options = []
    for project in project_service.get_all(db_session=db_session):
        project_options.append(option_from_template(text=project.name, value=project.name))

    block = {
        "block_id": IncidentBlockId.project,
        "type": "input",
        "dispatch_action": True,
        "label": {
            "text": "Project",
            "type": "plain_text",
        },
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Project"},
            "options": project_options,
            "action_id": ReportIncidentCallbackId.update_view,
        },
    }

    if initial_option:
        block["element"].update(
            {
                "initial_option": option_from_template(
                    text=initial_option.name, value=initial_option.name
                )
            }
        )
    return block


def tag_multi_select_block(
    initial_options: List[Tag] = None,
):
    """Builds the incident tag multi select block."""
    block = {
        "block_id": IncidentBlockId.tags,
        "type": "input",
        "optional": True,
        "label": {"type": "plain_text", "text": "Tags"},
        "element": {
            "action_id": IncidentBlockId.tags,
            "type": "multi_external_select",
            "placeholder": {"type": "plain_text", "text": "Select related tags"},
            "min_query_length": 3,
        },
    }

    if initial_options:
        block["element"].update(
            {
                "initial_options": [
                    option_from_template(text=f"{t.tag_type.name}/{t.name}", value=t.id)
                    for t in initial_options
                ]
            }
        )

    return block


def title_input_block(initial_value: str = None):
    """Builds a valid incident title input."""
    block = {
        "block_id": IncidentBlockId.title,
        "type": "input",
        "label": {"type": "plain_text", "text": "Title"},
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": "A brief explanatory title. You can change this later.",
            },
        },
    }

    if initial_value:
        block["element"].update({"initial_value": initial_value})

    return block


def description_input_block(initial_value: str = None):
    """Builds a valid incident description input."""
    block = {
        "block_id": IncidentBlockId.description,
        "type": "input",
        "label": {"type": "plain_text", "text": "Description"},
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": "A summary of what you know so far. It's all right if this is incomplete.",
            },
            "multiline": True,
        },
    }

    if initial_value:
        block["element"].update({"initial_value": initial_value})

    return block


def resolution_input_block(initial_value: str = None):
    """Builds a valid incident resolution input."""
    block = {
        "block_id": IncidentBlockId.resolution,
        "type": "input",
        "label": {"type": "plain_text", "text": "Resolution"},
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": "Description of the actions taken to resolve the incident.",
            },
            "multiline": True,
        },
    }

    if initial_value:
        block["element"].update({"initial_value": initial_value})

    return block


def participants_select_block(incident: Incident, initial_option: Participant = None):
    """Builds a static select with all current participants."""
    participant_options = []
    for p in incident.participants:
        participant_options.append(option_from_template(text=p.individual.name, value=p.id))

    block = {
        "block_id": UpdateParticipantBlockId.participant,
        "type": "input",
        "dispatch_action": True,
        "label": {"type": "plain_text", "text": "Participant"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select Participant"},
            "options": participant_options,
            "action_id": UpdateParticipantCallbackId.update_view,
        },
    }

    if initial_option:
        block["element"].update(
            {
                "initial_option": option_from_template(
                    text=initial_option.individual.name, value=initial_option.id
                )
            }
        )

    return block
