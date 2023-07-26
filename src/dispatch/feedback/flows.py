from schedule import every
from typing import Any
import logging

from dispatch.database.core import SessionLocal
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler

log = logging.getLogger(__name__)


@scheduler.add(every(1).day.at("18:00"), name="shift-feedback-daily")
def oncall_shift_feedback_flow(subject: Any, db_session: SessionLocal):
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="oncall"
    )
    if not oncall_plugin:
        log.warning("Feedback form not sent. No plugin of type oncall enabled.")
        return
    # TODO: Implement this
    oncall_plugin.instance.send_shift_feedback_form_message()
