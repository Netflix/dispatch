import logging
from datetime import datetime
from schedule import every

from dispatch.decorators import background_task
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.scheduler import scheduler

from .messaging import send_incident_report_reminder
from .models import ReportTypes

log = logging.getLogger(__name__)


@scheduler.add(every(1).hours, name="incident-report-reminders")
@background_task
def incident_report_reminders(db_session=None):
    """Sends report reminders to incident commanders for active incidents."""
    incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.active
    )

    for incident in incidents:
        for report_type in ReportTypes:
            try:
                remind_after = incident.created_at
                if report_type == ReportTypes.tactical_report:
                    notification_hour = incident.incident_priority.tactical_report_reminder
                    if incident.last_tactical_report:
                        remind_after = incident.last_tactical_report.created_at
                elif report_type == ReportTypes.executive_report:
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
