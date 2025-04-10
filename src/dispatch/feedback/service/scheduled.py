from schedule import every
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from dispatch.decorators import scheduled_project_task, timer
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.plugin.models import PluginInstance
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from .reminder import service as reminder_service
from dispatch.incident import service as incident_service
from dispatch.case import service as case_service

from .messaging import send_oncall_shift_feedback_message

log = logging.getLogger(__name__)

"""
    Experimental: will wake up and check the oncall schedule for previous day
    vs current day to see if a different person is oncall, if so, the previous day's
    oncall will receive a shift feedback form.

    Timing is determined by the shift_hours_type attribute of the service:
    - For 12-hour shifts: Teams trade off between UCAN and EMEA
      - EMEA: wake at 6am UTC == 8am UTC+2 Standard / 9am UTC+2 Daylight Saving
      - UCAN: wake at 4pm UTC == 8am PST / 9am PDT
    - For 24-hour shifts: All UCAN, no EMEA
      - UCAN only: wake at 4pm UTC == 8am PST / 9am PDT
"""


@scheduler.add(every(1).day.at("16:00"), name="oncall-shift-feedback-ucan")
@timer
@scheduled_project_task
def oncall_shift_feedback_ucan(db_session: Session, project: Project):
    # Process both 12-hour shifts (UCAN handoff) and 24-hour shifts (UCAN only) at 4pm UTC
    # First process 12-hour shifts
    oncall_shift_feedback(db_session=db_session, project=project, hour=6, shift_hours=12)
    # Then process 24-hour shifts
    oncall_shift_feedback(db_session=db_session, project=project, hour=16, shift_hours=24)
    find_expired_reminders_and_send(db_session=db_session, project=project)


@scheduler.add(every(1).day.at("06:00"), name="oncall-shift-feedback-emea")
@timer
@scheduled_project_task
def oncall_shift_feedback_emea(db_session: Session, project: Project):
    # Process 12-hour shifts at 6am UTC (EMEA handoff)
    oncall_shift_feedback(db_session=db_session, project=project, hour=16, shift_hours=12)
    find_expired_reminders_and_send(db_session=db_session, project=project)


def find_expired_reminders_and_send(*, db_session: Session, project: Project):
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
            service_id=reminder.schedule_id,
            shift_end_at=str(reminder.shift_end_at),
            schedule_name=reminder.schedule_name,
            reminder=reminder,
            db_session=db_session,
            details=reminder.details,
        )


def find_schedule_and_send(
    *,
    db_session: Session,
    project: Project,
    oncall_plugin: PluginInstance,
    schedule_id: str,
    service_id: str,
    hour: int,
):
    """
    Given PagerDuty schedule_id, determine if the shift ended for the previous oncall person and
    send the health metrics feedback request - note that if current and previous oncall is the
    same, then did_oncall_just_go_off_shift will return None
    """

    # Counts the number of participants with one or more active roles
    def count_active_participants(participants):
        return sum(1 for participant in participants if len(participant.active_roles) >= 1)

    current_oncall = oncall_plugin.instance.did_oncall_just_go_off_shift(schedule_id, hour)

    if current_oncall is None:
        return

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=current_oncall["email"], project_id=project.id
    )

    # Calculate the number of hours in the shift
    if current_oncall["shift_start"]:
        shift_start_raw = current_oncall["shift_start"]
        shift_start_at = (
            datetime.strptime(shift_start_raw, "%Y-%m-%dT%H:%M:%SZ")
            if "T" in shift_start_raw
            else datetime.strptime(shift_start_raw, "%Y-%m-%d %H:%M:%S")
        )
        shift_end_raw = current_oncall["shift_end"]
        shift_end_at = (
            datetime.strptime(shift_end_raw, "%Y-%m-%dT%H:%M:%SZ")
            if "T" in shift_end_raw
            else datetime.strptime(shift_end_raw, "%Y-%m-%d %H:%M:%S")
        )
        hours_in_shift = (shift_end_at - shift_start_at).total_seconds() / 3600
    else:
        hours_in_shift = 7 * 24  # default to 7 days

    num_incidents = 0
    num_cases = 0
    num_participants = 0
    incidents = incident_service.get_all_last_x_hours(db_session=db_session, hours=hours_in_shift)
    for incident in incidents:
        if incident.commander.individual.email == current_oncall["email"]:
            num_participants += count_active_participants(incident.participants)
            num_incidents += 1

    cases = case_service.get_all_last_x_hours(db_session=db_session, hours=hours_in_shift)
    for case in cases:
        if case.has_channel and case.assignee.individual.email == current_oncall["email"]:
            num_participants += count_active_participants(case.participants)
            num_cases += 1
    details = [
        {
            "num_incidents": num_incidents,
            "num_cases": num_cases,
            "num_participants": num_participants,
        }
    ]

    send_oncall_shift_feedback_message(
        project=project,
        individual=individual,
        service_id=service_id,
        shift_end_at=current_oncall["shift_end"],
        schedule_name=current_oncall["schedule_name"],
        details=details,
        db_session=db_session,
    )


def oncall_shift_feedback(
    db_session: Session, project: Project, hour: int, shift_hours: int = None
):
    """
    Experimental: collects feedback from individuals participating in an oncall service that has health metrics enabled
    when their oncall shift ends. For now, only for one project and schedule.

    Args:
        db_session: Database session
        project: Project to process
        hour: Hour of the day to check for shift changes
        shift_hours: If provided, only process services with this shift_hours_type (12 or 24)
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
        # Skip services that don't match the requested shift_hours_type
        if shift_hours and oncall_service.shift_hours_type != shift_hours:
            continue

        # for each service, get the schedule_id
        external_id = oncall_service.external_id
        schedule_id = oncall_plugin.instance.get_schedule_id_from_service_id(service_id=external_id)
        if schedule_id:
            find_schedule_and_send(
                db_session=db_session,
                project=project,
                oncall_plugin=oncall_plugin,
                schedule_id=schedule_id,
                service_id=external_id,
                hour=hour,
            )
