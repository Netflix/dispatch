from schedule import every
from typing import Any
import logging
from operator import attrgetter

from dispatch.database.core import SessionLocal
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.incident_role import service as incident_role_service
from dispatch.participant_role.models import ParticipantRoleType

log = logging.getLogger(__name__)


# TODO: timezones.
@scheduler.add(every(1).day.at("18:00"), name="shift-feedback-daily")
def oncall_shift_feedback_flow(subject: Any, db_session: SessionLocal):
    incident_roles = incident_role_service.get_all_enabled_by_role(
        db_session=db_session,
        role=ParticipantRoleType.incident_commander,
        project_id=subject.project.id,
    )
    role = sorted(incident_roles, key=attrgetter("order"))[0]

    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="oncall"
    )
    if not oncall_plugin:
        log.warning("Feedback form not sent. No plugin of type oncall enabled.")
        return

    oncall_plugin.instance.send_shift_feedback_form_message(role.service_id)
