from schedule import every
import logging

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.plugin.models import PluginInstance
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from .reminder import service as reminder_service

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
    oncall_shift_feedback(db_session=db_session, project=project, hour=16)
    find_expired_reminders_and_send(db_session=db_session, project=project)


@scheduler.add(every(1).day.at("06:00"), name="oncall-shift-feedback-emea")
@timer
@scheduled_project_task
def oncall_shift_feedback_emea(db_session: SessionLocal, project: Project):
    oncall_shift_feedback(db_session=db_session, project=project, hour=6)
    find_expired_reminders_and_send(db_session=db_session, project=project)


def find_expired_reminders_and_send(*, db_session: SessionLocal, project: Project):
    reminders = reminder_service.get_all_expired_reminders_by_project_id(
        db_session=db_session, project_id=project.id
    )
    for reminder in reminders:
        individual = individual_service.get(
            db_session=db_session, individual_contact_id=reminder.individual_contact_id
        )
        send_oncall_shift_feedback_message(
            project=project,
            individual=individual,
            schedule_id=reminder.schedule_id,
            shift_end_at=str(reminder.shift_end_at),
            schedule_name=reminder.schedule_name,
            reminder=reminder,
            db_session=db_session,
        )


def find_schedule_and_send(
    *,
    db_session: SessionLocal,
    project: Project,
    oncall_plugin: PluginInstance,
    schedule_id: str,
    hour: int,
):
    """
    Given PagerDuty schedule_id, determine if the shift ended for the previous oncall person and
    send the health metrics feedback request - note that if current and previous oncall is the
    same, then did_oncall_just_go_off_shift will return None
    """
    current_oncall = oncall_plugin.instance.did_oncall_just_go_off_shift(schedule_id, hour)

    if current_oncall is None:
        return

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=current_oncall["email"], project_id=project.id
    )

    send_oncall_shift_feedback_message(
        project=project,
        individual=individual,
        schedule_id=schedule_id,
        shift_end_at=current_oncall["shift_end"],
        schedule_name=current_oncall["schedule_name"],
        db_session=db_session,
    )


def oncall_shift_feedback(db_session: SessionLocal, project: Project, hour: int):
    """
    Experimental: collects feedback from individuals participating in an oncall service that has health metrics enabled
    when their oncall shift ends. For now, only for one project and schedule.
    """
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="oncall"
    )

    if not oncall_plugin:
        log.warning(
            f"Skipping collection of oncall shift feedback for project {project.name}. No oncall plugin enabled."
        )
        return

    # Get all oncall services marked for health metrics for this project
    oncall_services = service_service.get_all_by_health_metrics(
        db_session=db_session,
        service_type=oncall_plugin.instance.slug,
        health_metrics=True,
        project_id=project.id,
    )

    for oncall_service in oncall_services:
        # for each service, get the schedule_id
        external_id = oncall_service.external_id
        schedule_id = oncall_plugin.instance.get_schedule_id_from_service_id(service_id=external_id)
        if schedule_id:
            find_schedule_and_send(
                db_session=db_session,
                project=project,
                oncall_plugin=oncall_plugin,
                schedule_id=schedule_id,
                hour=hour,
            )
