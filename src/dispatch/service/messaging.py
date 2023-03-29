import logging

from sqlalchemy.orm import Session

from dispatch.individual.models import IndividualContact
from dispatch.messaging.strings import (
    ONCALL_SHIFT_FEEDBACK_NOTIFICATION,
    MessageType,
)
from dispatch.plugin import service as plugin_service

from .service import Service

log = logging.getLogger(__name__)


def send_oncall_shift_feedback_message(
    service: Service, individual: IndividualContact, db_session: Session
):
    """
    Sends a direct message to the oncall about to end their shift
    asking to provide feedback about their experience.
    """
    notification_text = "Oncall Shift Feedback"
    notification_template = ONCALL_SHIFT_FEEDBACK_NOTIFICATION

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=service.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Oncall shift feedback notification not sent. No conversation plugin enabled.")
        return

    items = [
        {
            "individual_name": individual.name,
            "oncall_service_name": service.name,
            "organization_slug": service.project.organization.slug,
        }
    ]

    try:
        plugin.instance.send_direct(
            individual.email,
            notification_text,
            notification_template,
            MessageType.oncall_shift_feedback,
            items=items,
        )
    except Exception as e:
        log.exception(e)

    log.debug(f"Oncall shift message sent to {individual.name}.")
