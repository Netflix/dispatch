import logging
from datetime import datetime, timedelta
from schedule import every
from typing import Optional

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .messaging import send_incident_report_reminder
from .models import ReportTypes


log = logging.getLogger(__name__)


def reminder_set_in_future(reminder: Optional[datetime]) -> bool:
    """if this reminder has been manually delayed, do not send regularly scheduled one"""
    if reminder and reminder - datetime.utcnow() > timedelta(minutes=1):
        return True
    return False


@scheduler.add(every(1).hours, name="incident-report-reminders")
@timer
@scheduled_project_task
def incident_report_reminders(db_session: SessionLocal, project: Project):
    """Sends report reminders to incident commanders for active incidents."""
    incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )

    for incident in incidents:
        for report_type in ReportTypes:
            try:
                remind_after = incident.created_at
                if report_type == ReportTypes.tactical_report:
                    if reminder_set_in_future(incident.delay_tactical_report_reminder):
                        continue
                    notification_hour = incident.incident_priority.tactical_report_reminder
                    if incident.last_tactical_report:
                        remind_after = incident.last_tactical_report.created_at
                elif report_type == ReportTypes.executive_report:
                    if reminder_set_in_future(incident.delay_executive_report_reminder):
                        continue
                    notification_hour = incident.incident_priority.executive_report_reminder
                    if incident.last_executive_report:
                        remind_after = incident.last_executive_report.created_at

                now = datetime.utcnow() - remind_after

                # we calculate the number of hours and seconds since last report was sent
                hours, seconds = divmod((now.days * 86400) + now.seconds, 3600)

                q, r = divmod(hours, notification_hour)
                if q >= 1 and r == 0:  # it's time to send the reminder
                    send_incident_report_reminder(incident, report_type, db_session)

            except Exception as e:
                # we shouldn't fail to send all reminders when one fails
                log.exception(e)


@scheduler.add(every(5).minutes, name="incident-report-delayed-reminders")
@timer
@scheduled_project_task
def incident_report_delayed_reminders(db_session: SessionLocal, project: Project):
    """Sends user-delayed report reminders to incident commanders for active incidents."""
    incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )

    for incident in incidents:
        try:
            if exec_report_time := incident.delay_executive_report_reminder:
                if datetime.utcnow() - exec_report_time > timedelta(minutes=1):
                    # send exec report reminder now
                    send_incident_report_reminder(
                        incident, ReportTypes.executive_report, db_session, True
                    )

            if tech_report_time := incident.delay_tactical_report_reminder:
                if datetime.utcnow() - tech_report_time > timedelta(minutes=1):
                    # send tech report reminder now!
                    send_incident_report_reminder(
                        incident, ReportTypes.tactical_report, db_session, True
                    )

        except Exception as e:
            # we shouldn't fail to send all reminders when one fails
            log.exception(e)
