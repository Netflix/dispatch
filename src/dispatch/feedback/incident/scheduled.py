from collections import defaultdict
from schedule import every
import logging

from sqlalchemy.orm import Session

from dispatch.decorators import scheduled_project_task, timer
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .messaging import send_incident_feedback_daily_report, send_case_feedback_daily_report
from .service import (
    get_all_incident_last_x_hours_by_project_id,
    get_all_case_last_x_hours_by_project_id,
)

log = logging.getLogger(__name__)


def group_feedback_by_commander(feedback):
    """Groups feedback by commander."""
    grouped = defaultdict(lambda: [])
    for piece in feedback:
        if piece.incident and piece.incident.commander:
            grouped[piece.incident.commander.individual.email].append(piece)
    return grouped


def group_feedback_by_assignee(feedback):
    """Groups feedback by assignee."""
    grouped = defaultdict(lambda: [])
    for piece in feedback:
        if piece.case and piece.case.assignee:
            grouped[piece.case.assignee.individual.email].append(piece)
    return grouped


@scheduler.add(every(1).day.at("18:00"), name="feedback-report-daily")
@timer
@scheduled_project_task
def feedback_report_daily(db_session: Session, project: Project):
    """
    Fetches all incident and case feedback provided in the last 24 hours
    and sends a daily report to the commanders and assignees who handled the incidents/cases.
    """
    incident_feedback = get_all_incident_last_x_hours_by_project_id(
        db_session=db_session, project_id=project.id
    )

    if incident_feedback:
        grouped_incident_feedback = group_feedback_by_commander(incident_feedback)
        for commander_email, feedback in grouped_incident_feedback.items():
            send_incident_feedback_daily_report(commander_email, feedback, project.id, db_session)

    case_feedback = get_all_case_last_x_hours_by_project_id(
        db_session=db_session, project_id=project.id
    )

    if case_feedback:
        grouped_case_feedback = group_feedback_by_assignee(case_feedback)
        for assignee_email, feedback in grouped_case_feedback.items():
            send_case_feedback_daily_report(assignee_email, feedback, project.id, db_session)
