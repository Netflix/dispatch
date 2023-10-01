from datetime import datetime, date
from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .enums import CaseStatus
from .messaging import send_case_close_reminder, send_case_triage_reminder
from .service import (
    get_all_by_status,
)


@scheduler.add(every(1).day.at("18:00"), name="case-close-reminder")
@timer
@scheduled_project_task
def case_close_reminder(db_session: SessionLocal, project: Project):
    """Sends a reminder to the case assignee to close out their case."""
    cases = get_all_by_status(
        db_session=db_session, project_id=project.id, status=CaseStatus.triage
    )

    for case in cases:
        span = datetime.utcnow() - case.triage_at
        q, r = divmod(span.days, 7)
        if q >= 1 and date.today().isoweekday() == 1:
            # we only send the reminder for cases that have been triaging
            # longer than a week and only on Mondays
            send_case_close_reminder(case, db_session)


@scheduler.add(every(1).day.at("18:00"), name="case-triage-reminder")
@timer
@scheduled_project_task
def case_triage_reminder(db_session: SessionLocal, project: Project):
    """Sends a reminder to the case assignee to triage their case."""
    cases = get_all_by_status(db_session=db_session, project_id=project.id, status=CaseStatus.new)

    # if we want more specific SLA reminders, we would need to add additional data model
    for case in cases:
        span = datetime.utcnow() - case.created
        q, r = divmod(span.days, 1)
        if q >= 1:
            # we only send one reminder per case per day
            send_case_triage_reminder(case, db_session)
