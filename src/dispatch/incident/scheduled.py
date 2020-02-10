import logging
from datetime import datetime

from schedule import every


from dispatch.config import (
    INCIDENT_CONVERSATION_SLUG,
    INCIDENT_NOTIFICATION_CONVERSATIONS,
    INCIDENT_TICKET_PLUGIN_SLUG,
)
from dispatch.conversation.enums import ConversationCommands
from dispatch.decorators import background_task
from dispatch.incident_priority.models import IncidentPriorityType
from dispatch.messaging import INCIDENT_DAILY_SUMMARY, INCIDENT_STATUS_REPORT_REMINDER, MessageType
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.extensions import sentry_sdk

from .enums import IncidentStatus
from .service import calculate_cost, get_all_by_status

# TODO figure out a way to do mapping in the config file
# reminder (in hours)
STATUS_REPORT_REMINDER_MAPPING = {
    IncidentPriorityType.high.name: 2,
    IncidentPriorityType.medium.name: 6,
    IncidentPriorityType.low.name: 12,
    IncidentPriorityType.info.name: 24,
}

log = logging.getLogger(__name__)


@scheduler.add(every(1).hours, name="incident-status-report-reminder")
@background_task
def status_report_reminder(db_session=None):
    """Sends status report reminders to active incident commanders."""
    incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active)

    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    status_report_command = convo_plugin.get_command_name(ConversationCommands.status_report)

    for incident in incidents:
        try:
            notification_hour = STATUS_REPORT_REMINDER_MAPPING[
                incident.incident_priority.name.lower()
            ]

            if incident.last_status_report:
                remind_after = incident.last_status_report.created_at
            else:
                remind_after = incident.created_at

            now = datetime.utcnow() - remind_after

            # we calculate the number of hours and seconds since last CAN was sent
            hours, seconds = divmod((now.days * 86400) + now.seconds, 3600)

            q, r = divmod(hours, notification_hour)
            if q >= 1 and r == 0:  # it's time to send the reminder
                if incident.ticket:  # TODO remove once we get clean data
                    items = [
                        {
                            "name": incident.name,
                            "ticket_weblink": incident.ticket.weblink,
                            "title": incident.title,
                            "command": status_report_command,
                        }
                    ]

                    convo_plugin.send_direct(
                        incident.commander.email,
                        "Incident Status Report Reminder",
                        INCIDENT_STATUS_REPORT_REMINDER,
                        MessageType.incident_status_report,
                        items=items,
                    )
        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            sentry_sdk.capture_exception(e)


@scheduler.add(every(1).day.at("18:00"), name="incident-daily-summary")
@background_task
def daily_summary(db_session=None):
    """Fetches all open incidents and provides a daily summary."""
    incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active)
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)

    incident_data = []
    if incidents:
        for incident in incidents:
            incident_data.append(
                {
                    "name": incident.name,
                    "title": incident.title,
                    "status": incident.status,
                    "priority": incident.incident_priority.name,
                    "ticket_weblink": incident.ticket.weblink,
                    "commander_fullname": incident.commander.name,
                    "commander_weblink": incident.commander.weblink,
                }
            )

        for c in INCIDENT_NOTIFICATION_CONVERSATIONS:
            convo_plugin.send(
                c,
                "Incident Summary",
                INCIDENT_DAILY_SUMMARY,
                MessageType.incident_daily_summary,
                items=incident_data,
            )


@scheduler.add(every(5).minutes, name="calculate-incident-cost")
@background_task
def active_incidents_cost(db_session=None):
    """Calculates the cost of all active incidents."""
    active_incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active)

    for incident in active_incidents:
        # we calculate the cost
        try:
            incident_cost = calculate_cost(incident.id, db_session)

            # we update the incident
            incident.cost = incident_cost
            db_session.add(incident)
            db_session.commit()

            if incident.ticket.resource_id:
                # we update the external ticket
                ticket_plugin = plugins.get(INCIDENT_TICKET_PLUGIN_SLUG)
                ticket_plugin.update(
                    incident.ticket.resource_id,
                    cost=incident_cost,
                    incident_type=incident.incident_type.name,
                )
                log.debug(f"Incident cost for {incident.name} updated in the ticket.")
            else:
                log.debug(f"Incident cost for {incident.name} not updated. Ticket not found.")

            log.debug(f"Incident cost for {incident.name} updated in the database.")
        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            sentry_sdk.capture_exception(e)
