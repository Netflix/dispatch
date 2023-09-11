import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from dispatch.individual.models import IndividualContact
from dispatch.messaging.strings import (
    ONCALL_SHIFT_FEEDBACK_NOTIFICATION,
    ONCALL_SHIFT_FEEDBACK_NOTIFICATION_REMINDER,
    MessageType,
)
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from .reminder.models import ServiceFeedbackReminder, ServiceFeedbackReminderUpdate
from .reminder import service as reminder_service

log = logging.getLogger(__name__)


def send_oncall_shift_feedback_message(
    *,
    project: Project,
    individual: IndividualContact,
    schedule_id: str,
    shift_end_at: str,
    schedule_name: str,
    reminder: Optional[ServiceFeedbackReminder] = None,
    db_session: Session,
):
    """
    Experimental: sends a direct message to the oncall about to end their shift
    asking to provide feedback about their experience.
    """
    notification_text = "Oncall Shift Feedback Request"
    notification_template = ONCALL_SHIFT_FEEDBACK_NOTIFICATION

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning(
            "Oncall shift feedback request notification not sent. No conversation plugin enabled."
        )
        return

    if reminder:
        # update reminder with 23 hours from now
        reminder = reminder_service.update(
            db_session=db_session,
            reminder=reminder,
            reminder_in=ServiceFeedbackReminderUpdate(
                id=reminder.id,
                reminder_at=datetime.utcnow() + timedelta(hours=23),
            ),
        )
        notification_template = ONCALL_SHIFT_FEEDBACK_NOTIFICATION_REMINDER
    else:
        # create reminder and pass to plugin
        reminder = reminder_service.create(
            db_session=db_session,
            reminder_in=ServiceFeedbackReminder(
                reminder_at=datetime.utcnow() + timedelta(hours=23),
                individual_contact_id=individual.id,
                project_id=project.id,
                schedule_id=schedule_id,
                schedule_name=schedule_name,
                shift_end_at=shift_end_at,
            ),
        )

    shift_end_clean = shift_end_at.replace("T", " ").replace("Z", "")
    items = [
        {
            "individual_name": individual.name,
            "oncall_schedule_id": schedule_id,
            "oncall_service_name": schedule_name,
            "organization_slug": project.organization.slug,
            "project_id": project.id,
            "shift_end_at": shift_end_clean,
            "reminder_id": reminder.id,
        }
    ]

    try:
        plugin.instance.send_direct(
            individual.email,
            notification_text,
            notification_template,
            MessageType.service_feedback,
            items=items,
        )
    except Exception as e:
        log.exception(e)
