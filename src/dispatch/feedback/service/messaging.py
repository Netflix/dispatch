import logging

from sqlalchemy.orm import Session

from dispatch.individual.models import IndividualContact
from dispatch.messaging.strings import (
    ONCALL_SHIFT_FEEDBACK_NOTIFICATION,
    MessageType,
)
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project


log = logging.getLogger(__name__)


def send_oncall_shift_feedback_message(
    *,
    project: Project,
    individual: IndividualContact,
    schedule_id: str,
    shift_end_at: str,
    schedule_name: str,
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

    items = [
        {
            "individual_name": individual.name,
            "oncall_schedule_id": schedule_id,
            "oncall_service_name": schedule_name,
            "organization_slug": project.organization.slug,
            "project_id": project.id,
            "shift_end_at": shift_end_at,
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
