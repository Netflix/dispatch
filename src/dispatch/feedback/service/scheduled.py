from schedule import every
import logging
from operator import attrgetter

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.config import DISPATCH_FEEDBACK_PROJECT_NAME, DISPATCH_FEEDBACK_SCHEDULE_ID
from .messaging import send_oncall_shift_feedback_message

log = logging.getLogger(__name__)

"""
    Experimental: will wake up and check the oncall schedule for previous day
    vs current day to see if a different person is oncall, if so, the previous day's
    oncall will receive a shift feedback form.
    Timing: for UCAN, wake at 4pm UTC == 8am PST / 9am PDT
            for EMEA, wake at 6am UTC == 8am UTC+2 Standard / 9am UTC+2 Daylight Saving
"""


@scheduler.add(every(1).day.at("16:00"), name="oncall-shift-feedback-ucan")
@timer
@scheduled_project_task
def oncall_shift_feedback_ucan(db_session: SessionLocal, project: Project):
    oncall_shift_feedback(db_session=db_session, project=project)


@scheduler.add(every(1).day.at("06:00"), name="oncall-shift-feedback-emea")
@timer
@scheduled_project_task
def oncall_shift_feedback_emea(db_session: SessionLocal, project: Project):
    oncall_shift_feedback(db_session=db_session, project=project)


def oncall_shift_feedback(db_session: SessionLocal, project: Project):
    """
    Experimental: collects feedback from individuals participating in an oncall service that has health metrics enabled
    when their oncall shift ends. For now, only for one project and schedule.
    """
    if project.name != DISPATCH_FEEDBACK_PROJECT_NAME:
        return

    schedule_id = DISPATCH_FEEDBACK_SCHEDULE_ID
    if not schedule_id:
        return

    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="oncall"
    )
    if not oncall_plugin:
        log.warning("Feedback form not sent. No plugin of type oncall enabled.")
        return

    current_oncall = oncall_plugin.instance.did_oncall_just_go_off_shift(schedule_id)

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=current_oncall["email"], project_id=project.id
    )

    send_oncall_shift_feedback_message(
        project=project,
        individual=individual,
        schedule_id=schedule_id,
        shift_end_at=current_oncall["shift_end"],
        db_session=db_session,
    )

    print(
        f"Requesting oncall shift feedback from {individual.name}."
    )
