"""Canvas flows for managing incident and case-related canvases."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from .models import Canvas, CanvasCreate
from .enums import CanvasType
from .service import create
from dispatch.incident.models import Incident
from dispatch.case.models import Case
from dispatch.participant.models import Participant
from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def create_participants_canvas(
    incident: Incident = None, case: Case = None, db_session: Session = None
) -> Optional[str]:
    """
    Creates a new participants canvas in the incident's or case's Slack channel.

    Args:
        incident: The incident to create the canvas for (mutually exclusive with case)
        case: The case to create the canvas for (mutually exclusive with incident)
        db_session: Database session

    Returns:
        The canvas ID if successful, None if failed
    """
    if incident and case:
        raise ValueError("Cannot specify both incident and case")
    if not incident and not case:
        raise ValueError("Must specify either incident or case")

    if incident:
        return _create_incident_participants_canvas(incident, db_session)
    else:
        return _create_case_participants_canvas(case, db_session)


def _create_incident_participants_canvas(incident: Incident, db_session: Session) -> Optional[str]:
    """
    Creates a new participants canvas in the incident's Slack channel.

    Args:
        incident: The incident to create the canvas for
        db_session: Database session

    Returns:
        The canvas ID if successful, None if failed
    """
    # Check if incident has a conversation
    if not incident.conversation:
        log.debug(f"Skipping canvas creation for incident {incident.id} - no conversation")
        return None

    # Check if conversation has a channel_id
    if not incident.conversation.channel_id:
        log.debug(f"Skipping canvas creation for incident {incident.id} - no channel_id")
        return None

    try:
        # Get the Slack plugin instance
        slack_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
        )

        # Create the canvas in Slack
        canvas_id = slack_plugin.instance.create_canvas(
            conversation_id=incident.conversation.channel_id,
            title="Participants",
            user_emails=(
                [incident.commander.individual.email] if incident.commander else []
            ),  # Give commander edit permissions
            content=_build_participants_table(incident, db_session),
        )

        if canvas_id:
            # Store the canvas record in the database
            create(
                db_session=db_session,
                canvas_in=CanvasCreate(
                    canvas_id=canvas_id,
                    incident_id=incident.id,
                    case_id=None,
                    type=CanvasType.participants,
                    project_id=incident.project_id,
                ),
            )
            return canvas_id
        else:
            log.error(f"Failed to create participants canvas for incident {incident.id}")
            return None

    except Exception as e:
        log.exception(f"Error creating participants canvas for incident {incident.id}: {e}")
        return None


def _create_case_participants_canvas(case: Case, db_session: Session) -> Optional[str]:
    """
    Creates a new participants canvas in the case's Slack channel.

    Args:
        case: The case to create the canvas for
        db_session: Database session

    Returns:
        The canvas ID if successful, None if failed
    """
    # Only create canvas for cases with dedicated channels
    if not case.dedicated_channel:
        log.debug(f"Skipping canvas creation for case {case.id} - no dedicated channel")
        return None

    # Check if case has a conversation
    if not case.conversation:
        log.debug(f"Skipping canvas creation for case {case.id} - no conversation")
        return None

    # Check if conversation has a channel_id
    if not case.conversation.channel_id:
        log.debug(f"Skipping canvas creation for case {case.id} - no channel_id")
        return None

    try:
        # Get the Slack plugin instance
        slack_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="conversation"
        )

        if not slack_plugin:
            log.error(f"No conversation plugin found for case {case.id}")
            return None

        # Build the participants table content
        table_content = _build_case_participants_table(case, db_session)
        log.debug(f"Built participants table for case {case.id}: {table_content[:100]}...")

        # Create the canvas in Slack
        canvas_id = slack_plugin.instance.create_canvas(
            conversation_id=case.conversation.channel_id,
            title="Participants",
            user_emails=(
                [case.assignee.individual.email] if case.assignee else []
            ),  # Give assginee edit permissions
            content=table_content,
        )

        if canvas_id:
            # Store the canvas record in the database
            create(
                db_session=db_session,
                canvas_in=CanvasCreate(
                    canvas_id=canvas_id,
                    incident_id=None,
                    case_id=case.id,
                    type=CanvasType.participants,
                    project_id=case.project_id,
                ),
            )
            log.info(f"Successfully created participants canvas {canvas_id} for case {case.id}")
            return canvas_id
        else:
            log.error(f"Failed to create participants canvas for case {case.id}")
            return None

    except Exception as e:
        log.exception(f"Error creating participants canvas for case {case.id}: {e}")
        return None


def update_participants_canvas(
    incident: Incident = None, case: Case = None, db_session: Session = None
) -> bool:
    """
    Updates the participants canvas with current participant information.

    Args:
        incident: The incident to update the canvas for (mutually exclusive with case)
        case: The case to update the canvas for (mutually exclusive with incident)
        db_session: Database session

    Returns:
        True if successful, False if failed
    """
    if incident and case:
        raise ValueError("Cannot specify both incident and case")
    if not incident and not case:
        raise ValueError("Must specify either incident or case")

    if incident:
        return _update_incident_participants_canvas(incident, db_session)
    else:
        return _update_case_participants_canvas(case, db_session)


def _update_incident_participants_canvas(incident: Incident, db_session: Session) -> bool:
    """
    Updates the participants canvas with current participant information.

    Args:
        incident: The incident to update the canvas for
        db_session: Database session

    Returns:
        True if successful, False if failed
    """
    # Check if incident has a conversation
    if not incident.conversation:
        log.debug(f"Skipping canvas update for incident {incident.id} - no conversation")
        return False

    # Check if conversation has a channel_id
    if not incident.conversation.channel_id:
        log.debug(f"Skipping canvas update for incident {incident.id} - no channel_id")
        return False

    try:
        # Get the existing canvas record by incident and type
        canvas = (
            db_session.query(Canvas)
            .filter(Canvas.incident_id == incident.id, Canvas.type == CanvasType.participants)
            .first()
        )

        if not canvas:
            log.warning(
                f"No participants canvas found for incident {incident.id}, creating new one"
            )
            return False

        # Get the Slack plugin instance
        slack_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
        )

        # Build the updated table content
        table_content = _build_participants_table(incident, db_session)

        # Update the canvas
        success = slack_plugin.instance.edit_canvas(
            canvas_id=canvas.canvas_id, content=table_content
        )

        if success:
            log.info(f"Updated participants canvas {canvas.canvas_id} for incident {incident.id}")
        else:
            log.error(
                f"Failed to update participants canvas {canvas.canvas_id} for incident {incident.id}"
            )

        return success

    except Exception as e:
        log.exception(f"Error updating participants canvas for incident {incident.id}: {e}")
        return False


def _build_participants_table(incident: Incident, db_session: Session) -> str:
    """
    Builds markdown tables of participants for the canvas.
    Splits into multiple tables if there are more than 60 participants to avoid Slack's 300 cell limit.

    Args:
        incident: The incident to build the table for
        db_session: Database session

    Returns:
        Markdown table string
    """
    # Get all participants for the incident
    participants = (
        db_session.query(Participant).filter(Participant.incident_id == incident.id).all()
    )

    if not participants:
        return "# Participants\n\nNo participants have been added to this incident yet."

    # Define role priority for sorting (lower number = higher priority)
    role_priority = {
        "Incident Commander": 1,
        "Scribe": 2,
        "Reporter": 3,
        "Participant": 4,
        "Observer": 5,
    }

    # Filter out inactive participants and sort by role priority
    active_participants = []
    for participant in participants:
        if participant.active_roles:
            # Get the highest priority role for this participant
            highest_priority = float("inf")
            primary_role = "Other"

            for role in participant.active_roles:
                # role.role is already a string (role name), not an object
                role_name = role.role if role.role else "Other"
                priority = role_priority.get(role_name, 999)  # Default to low priority
                if priority < highest_priority:
                    highest_priority = priority
                    primary_role = role_name

            active_participants.append((participant, highest_priority, primary_role))

    # Sort by priority, then by name
    active_participants.sort(
        key=lambda x: (x[1], x[0].individual.name if x[0].individual else "Unknown")
    )

    # Extract just the participants in sorted order
    sorted_participants = [p[0] for p in active_participants]

    if not sorted_participants:
        return "# Participants\n\nNo active participants found for this incident."

    # Build the content
    content = f"# Participants ({len(participants)} total)\n\n"

    # Group participants by their primary role
    participants_by_role = {}
    for participant in sorted_participants:
        # Get the highest priority role for this participant
        highest_priority = float("inf")
        primary_role = "Other"

        for role in participant.active_roles:
            # role.role is already a string (role name), not an object
            role_name = role.role if role.role else "Other"
            priority = role_priority.get(role_name, 999)  # Default to low priority
            if priority < highest_priority:
                highest_priority = priority
                primary_role = role_name

        if primary_role not in participants_by_role:
            participants_by_role[primary_role] = []
        participants_by_role[primary_role].append(participant)

    # Add participants grouped by role
    for role_name in [
        "Incident Commander",
        "Scribe",
        "Reporter",
        "Participant",
        "Observer",
        "Other",
    ]:
        if role_name in participants_by_role:
            participants_count = len(participants_by_role[role_name])
            # Add "s" only if there are multiple participants in this role
            heading = f"## {role_name}{'s' if participants_count > 1 else ''}\n\n"
            content += heading
            for participant in participants_by_role[role_name]:
                name = participant.individual.name if participant.individual else "Unknown"
                team = participant.team or "Unknown"
                location = participant.location or "Unknown"
                content += f"* **{name}** - {team} - {location}\n"
            content += "\n"

    return content


def _update_case_participants_canvas(case: Case, db_session: Session) -> bool:
    """
    Updates the participants canvas with current participant information.

    Args:
        case: The case to update the canvas for
        db_session: Database session

    Returns:
        True if successful, False if failed
    """
    # Only update canvas for cases with dedicated channels
    if not case.dedicated_channel:
        log.debug(f"Skipping canvas update for case {case.id} - no dedicated channel")
        return False

    # Check if case has a conversation
    if not case.conversation:
        log.debug(f"Skipping canvas update for case {case.id} - no conversation")
        return False

    # Check if conversation has a channel_id
    if not case.conversation.channel_id:
        log.debug(f"Skipping canvas update for case {case.id} - no channel_id")
        return False

    try:
        # Get the existing canvas record by case and type
        canvas = (
            db_session.query(Canvas)
            .filter(Canvas.case_id == case.id, Canvas.type == CanvasType.participants)
            .first()
        )

        if not canvas:
            log.warning(f"No participants canvas found for case {case.id}, creating new one")
            return False

        # Get the Slack plugin instance
        slack_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="conversation"
        )

        # Build the updated table content
        table_content = _build_case_participants_table(case, db_session)

        # Update the canvas
        success = slack_plugin.instance.edit_canvas(
            canvas_id=canvas.canvas_id, content=table_content
        )

        if success:
            log.info(f"Updated participants canvas {canvas.canvas_id} for case {case.id}")
        else:
            log.error(f"Failed to update participants canvas {canvas.canvas_id} for case {case.id}")

        return success

    except Exception as e:
        log.exception(f"Error updating participants canvas for case {case.id}: {e}")
        return False


def _build_case_participants_table(case: Case, db_session: Session) -> str:
    """
    Builds markdown tables of participants for the canvas.
    Splits into multiple tables if there are more than 60 participants to avoid Slack's 300 cell limit.

    Args:
        case: The case to build the table for
        db_session: Database session

    Returns:
        Markdown table string
    """
    # Get all participants for the case
    participants = db_session.query(Participant).filter(Participant.case_id == case.id).all()

    if not participants:
        return "# Participants\n\nNo participants have been added to this case yet."

    # Define role priority for sorting (lower number = higher priority)
    role_priority = {
        "Assignee": 1,
        "Reporter": 2,
        "Participant": 3,
        "Observer": 4,
    }

    # Filter out inactive participants and sort by role priority
    active_participants = []
    for participant in participants:
        if participant.active_roles:
            # Get the highest priority role for this participant
            highest_priority = float("inf")
            primary_role = "Other"

            for role in participant.active_roles:
                # role.role is already a string (role name), not an object
                role_name = role.role if role.role else "Other"
                priority = role_priority.get(role_name, 999)  # Default to low priority
                if priority < highest_priority:
                    highest_priority = priority
                    primary_role = role_name

            active_participants.append((participant, highest_priority, primary_role))

    # Sort by priority, then by name
    active_participants.sort(
        key=lambda x: (x[1], x[0].individual.name if x[0].individual else "Unknown")
    )

    # Extract just the participants in sorted order
    sorted_participants = [p[0] for p in active_participants]

    if not sorted_participants:
        return "# Participants\n\nNo active participants found for this case."

    # Build the content
    content = f"# Participants ({len(participants)} total)\n\n"

    # Group participants by their primary role
    participants_by_role = {}
    for participant in sorted_participants:
        # Get the highest priority role for this participant
        highest_priority = float("inf")
        primary_role = "Other"

        for role in participant.active_roles:
            # role.role is already a string (role name), not an object
            role_name = role.role if role.role else "Other"
            priority = role_priority.get(role_name, 999)  # Default to low priority
            if priority < highest_priority:
                highest_priority = priority
                primary_role = role_name

        if primary_role not in participants_by_role:
            participants_by_role[primary_role] = []
        participants_by_role[primary_role].append(participant)

    # Add participants grouped by role
    for role_name in [
        "Assignee",
        "Reporter",
        "Participant",
        "Observer",
        "Other",
    ]:
        if role_name in participants_by_role:
            participants_count = len(participants_by_role[role_name])
            # Add "s" only if there are multiple participants in this role
            heading = f"## {role_name}{'s' if participants_count > 1 else ''}\n\n"
            content += heading
            for participant in participants_by_role[role_name]:
                name = participant.individual.name if participant.individual else "Unknown"
                team = participant.team or "Unknown"
                location = participant.location or "Unknown"
                content += f"* **{name}** - {team} - {location}\n"
            content += "\n"

    return content
