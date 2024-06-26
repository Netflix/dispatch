"""
.. module: dispatch.case.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from dispatch.database.core import SessionLocal, resolve_attr
from dispatch.case.models import Case
from dispatch.email_templates.models import EmailTemplates
from dispatch.messaging.strings import (
    CASE_CLOSE_REMINDER,
    CASE_TRIAGE_REMINDER,
    MessageType,
    generate_case_welcome_message,
)
from dispatch.config import DISPATCH_UI_URL
from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def send_case_close_reminder(case: Case, db_session: SessionLocal) -> None:
    """
    Sends a direct message to the assignee reminding them to close the case if possible.
    """
    message_text = "Case Close Reminder"
    message_template = CASE_CLOSE_REMINDER

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if plugin is None:
        log.warning("Case close reminder message not sent. No conversation plugin enabled.")
        return
    if case.assignee is None:
        log.warning(f"Case close reminder message not sent. No assignee for {case.name}.")
        return

    items = [
        {
            "name": case.name,
            "dispatch_ui_case_url": f"{DISPATCH_UI_URL}/{case.project.organization.name}/cases/{case.name}",  # noqa
            "title": case.title,
            "status": case.status,
        }
    ]

    plugin.instance.send_direct(
        case.assignee.individual.email,
        message_text,
        message_template,
        MessageType.case_status_reminder,
        items=items,
    )

    log.debug(f"Case close reminder sent to {case.assignee.individual.email}.")


def send_case_triage_reminder(case: Case, db_session: SessionLocal) -> None:
    """
    Sends a direct message to the assignee reminding them to triage the case if possible.
    """
    message_text = "Case Triage Reminder"
    message_template = CASE_TRIAGE_REMINDER

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if plugin is None:
        log.warning("Case triage reminder message not sent. No conversation plugin enabled.")
        return

    if case.assignee is None:
        log.warning(f"Case triage reminder message not sent. No assignee for {case.name}.")
        return

    items = [
        {
            "name": case.name,
            "title": case.title,
            "status": case.status,
            "dispatch_ui_case_url": f"{DISPATCH_UI_URL}/{case.project.organization.name}/cases/{case.name}",  # noqa
        }
    ]

    plugin.instance.send_direct(
        case.assignee.individual.email,
        message_text,
        message_template,
        MessageType.case_status_reminder,
        items=items,
    )

    log.debug(f"Case triage reminder sent to {case.assignee.individual.email}.")


def send_case_welcome_ephemeral_message_to_participant(
    *,
    participant_email: str,
    case: Case,
    db_session: SessionLocal,
    welcome_template: EmailTemplates | None = None,
):
    """Sends an ephemeral welcome message to the participant."""
    if not case.conversation:
        log.warning(
            "Case participant welcome message not sent. No conversation available for this case."
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Case participant welcome message not sent. No conversation plugin enabled.")
        return

    case_description = (
        case.description if len(case.description) <= 500 else f"{case.description[:500]}..."
    )

    # we send the ephemeral message
    message_kwargs = {
        "name": case.name,
        "title": case.title,
        "description": case_description,
        "visibility": case.visibility,
        "status": case.status,
        "type": case.case_type.name,
        "type_description": case.case_type.description,
        "severity": case.case_severity.name,
        "severity_description": case.case_severity.description,
        "priority": case.case_priority.name,
        "priority_description": case.case_priority.description,
        "assignee_fullname": case.assignee.individual.name,
        "reporter_fullname": case.reporter.individual.name,
    }

    plugin.instance.send_ephemeral(
        case.conversation.channel_id,
        participant_email,
        "Case Welcome Message",
        generate_case_welcome_message(welcome_template),
        MessageType.incident_participant_welcome,
        **message_kwargs,
    )

    log.debug(f"Welcome ephemeral message sent to {participant_email}.")
