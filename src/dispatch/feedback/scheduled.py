from collections import defaultdict
from datetime import datetime
from schedule import every
import logging

from dispatch.decorators import background_task
from dispatch.scheduler import scheduler

from .messaging import send_incident_feedback_daily_report
from .service import get_all_last_x_hours


log = logging.getLogger(__name__)


def group_feedback_by_commander(feedback):
    """Groups feedback by commander."""
    grouped = defaultdict(lambda: [])
    for piece in feedback:
        grouped[piece.incident.commander.individual.email].append(piece)
    return grouped


@scheduler.add(every(1).day.at("17:00"), name="incident-feedback-daily-report")
@background_task
def daily_report(db_session=None):
    """
    Fetches all incident feedback provided in the last 24 hours
    and sends a daily report to the commanders who handled the incidents.
    """
    feedback = get_all_last_x_hours(db_session=db_session)

    if feedback:
        grouped_feedback = group_feedback_by_commander(feedback)
        for commander, feedback in grouped_feedback.items():
            send_incident_feedback_daily_report(commander, feedback, db_session)
