"""
.. module: dispatch.case.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from datetime import datetime, date
from schedule import every
from sqlalchemy.orm import Session
from sqlalchemy import or_

from dispatch.decorators import scheduled_project_task, timer
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .enums import CaseStatus
from .messaging import send_case_close_reminder, send_case_triage_reminder
from .models import Case
from .service import (
    get_all_by_status,
)


log = logging.getLogger(__name__)


@scheduler.add(every(1).day.at("18:00"), name="case-close-reminder")
@timer
@scheduled_project_task
def case_close_reminder(db_session: Session, project: Project):
    """Sends a reminder to the case assignee to close out their case."""
    cases = get_all_by_status(
        db_session=db_session,
        project_id=project.id,
        statuses=[CaseStatus.triage]
    )

    for case in cases:
        try:
            span = datetime.utcnow() - case.triage_at
            q, r = divmod(span.days, 7)
            if q >= 1 and date.today().isoweekday() == 1:
                # we only send the reminder for cases that have been triaging
                # longer than a week and only on Mondays
                send_case_close_reminder(case, db_session)
        except Exception as e:
            # if one fails we don't want all to fail
            log.exception(e)


@scheduler.add(every(1).day.at("18:00"), name="case-triage-reminder")
@timer
@scheduled_project_task
def case_triage_reminder(db_session: Session, project: Project):
    """Sends a reminder to the case assignee to triage their case."""

    cases = (
        db_session.query(Case)
        .filter(Case.project_id == project.id)
        .filter(Case.status != CaseStatus.closed)
        .filter(
            or_(
                Case.title == "Security Event Triage",
                Case.status == CaseStatus.new
            )
        )
        .all()
    )

    # if we want more specific SLA reminders, we would need to add additional data model
    for case in cases:
        span = datetime.utcnow() - case.created_at
        q, r = divmod(span.days, 1)
        if q >= 1:
            # we only send one reminder per case per day
            send_case_triage_reminder(case, db_session)


@scheduler.add(every(1).day.at("18:00"), name="case-stable-reminder")
@timer
@scheduled_project_task
def case_stable_reminder(db_session: Session, project: Project):
    """Sends a reminder to the case assignee to close their stable case."""
    cases = get_all_by_status(
        db_session=db_session, project_id=project.id, statuses=[CaseStatus.stable]
    )

    for case in cases:
        try:
            span = datetime.utcnow() - case.stable_at
            q, r = divmod(span.days, 7)
            if q >= 1 and date.today().isoweekday() == 1:
                # we only send the reminder for cases that have been stable
                # longer than a week and only on Mondays
                send_case_close_reminder(case, db_session)
        except Exception as e:
            # if one fails we don't want all to fail
            log.exception(e)
