import logging
from datetime import datetime
from sqlalchemy import func

from schedule import every

from dispatch.config import (
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID,
    INCIDENT_NOTIFICATION_CONVERSATIONS,
    INCIDENT_PLUGIN_TICKET_SLUG,
    INCIDENT_PLUGIN_STORAGE_SLUG,
)
from dispatch.decorators import background_task
from dispatch.enums import Visibility
from dispatch.extensions import sentry_sdk
from dispatch.individual import service as individual_service
from dispatch.messaging import (
    INCIDENT_DAILY_SUMMARY_ACTIVE_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_NO_ACTIVE_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_NO_STABLE_CLOSED_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_STABLE_CLOSED_INCIDENTS_DESCRIPTION,
)

from dispatch.nlp import (
    build_phrase_matcher,
    build_term_vocab,
    extract_terms_from_text,
)
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag

from dispatch.conversation.enums import ConversationButtonActions
from .enums import IncidentStatus
from .service import calculate_cost, get_all, get_all_by_status, get_all_last_x_hours_by_status
from .messaging import send_incident_status_report_reminder


log = logging.getLogger(__name__)


@scheduler.add(every(1).hours, name="incident-tagger")
@background_task
def auto_tagger(db_session):
    """Attempts to take existing tags and associate them with incidents."""
    tags = tag_service.get_all(db_session=db_session).all()
    log.debug(f"Fetched {len(tags)} tags from database.")

    tag_strings = [t.name.lower() for t in tags if t.discoverable]
    phrases = build_term_vocab(tag_strings)
    matcher = build_phrase_matcher("dispatch-tag", phrases)

    p = plugins.get(
        INCIDENT_PLUGIN_STORAGE_SLUG
    )  # this may need to be refactored if we support multiple document types

    for incident in get_all(db_session=db_session).all():
        log.debug(f"Processing incident. Name: {incident.name}")

        doc = incident.incident_document
        try:
            mime_type = "text/plain"
            text = p.get(doc.resource_id, mime_type)
        except Exception as e:
            print(f"Failed to get document. Reason: {e}")
            sentry_sdk.capture_exception(e)
            continue

        extracted_tags = list(set(extract_terms_from_text(text, matcher)))

        matched_tags = (
            db_session.query(Tag)
            .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
            .all()
        )

        incident.tags.extend(matched_tags)
        db_session.commit()

        print(f"Associating tags with incident. Incident: {incident.name}, Tags: {extracted_tags}")


@scheduler.add(every(1).hours, name="incident-status-report-reminder")
@background_task
def status_report_reminder(db_session=None):
    """Sends status report reminders to active incident commanders."""
    incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active)

    for incident in incidents:
        try:
            notification_hour = incident.incident_priority.status_reminder

            if incident.last_status_report:
                remind_after = incident.last_status_report.created_at
            else:
                remind_after = incident.created_at

            now = datetime.utcnow() - remind_after

            # we calculate the number of hours and seconds since last CAN was sent
            hours, seconds = divmod((now.days * 86400) + now.seconds, 3600)

            q, r = divmod(hours, notification_hour)
            if q >= 1 and r == 0:  # it's time to send the reminder
                send_incident_status_report_reminder(incident)

        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            sentry_sdk.capture_exception(e)


@scheduler.add(every(1).day.at("18:00"), name="incident-daily-summary")
@background_task
def daily_summary(db_session=None):
    """Fetches all open incidents and provides a daily summary."""

    blocks = []
    blocks.append(
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{INCIDENT_DAILY_SUMMARY_DESCRIPTION}*"},
        }
    )

    active_incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active)
    if active_incidents:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{INCIDENT_DAILY_SUMMARY_ACTIVE_INCIDENTS_DESCRIPTION}*",
                },
            }
        )
        for idx, incident in enumerate(active_incidents):
            if incident.visibility == Visibility.open:
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{incident.ticket.weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Incident Commander*: <{incident.commander.weblink}|{incident.commander.name}>"
                                ),
                            },
                            "block_id": f"{ConversationButtonActions.invite_user}-{idx}",
                            "accessory": {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Get Involved"},
                                "value": f"{incident.id}",
                            },
                        }
                    )
                except Exception as e:
                    sentry_sdk.capture_exception(e)
    else:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": INCIDENT_DAILY_SUMMARY_NO_ACTIVE_INCIDENTS_DESCRIPTION,
                },
            }
        )

    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{INCIDENT_DAILY_SUMMARY_STABLE_CLOSED_INCIDENTS_DESCRIPTION}*",
            },
        }
    )

    hours = 24
    stable_closed_incidents = get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.stable, hours=hours
    ) + get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.closed, hours=hours
    )
    if stable_closed_incidents:
        for incident in stable_closed_incidents:
            if incident.visibility == Visibility.open:
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{incident.ticket.weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Status*: {incident.status}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Incident Commander*: <{incident.commander.weblink}|{incident.commander.name}>"
                                ),
                            },
                        }
                    )
                except Exception as e:
                    sentry_sdk.capture_exception(e)
    else:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": INCIDENT_DAILY_SUMMARY_NO_STABLE_CLOSED_INCIDENTS_DESCRIPTION,
                },
            }
        )

    # NOTE INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID is optional
    if INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID:
        oncall_service = service_service.get_by_external_id(
            db_session=db_session, external_id=INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID
        )

        oncall_plugin = plugins.get(oncall_service.type)
        oncall_email = oncall_plugin.get(service_id=INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID)

        oncall_individual = individual_service.resolve_user_by_email(oncall_email)

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"For questions about this notification, reach out to <{oncall_individual['weblink']}|{oncall_individual['fullname']}> (current on-call)",
                    }
                ],
            }
        )

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    for c in INCIDENT_NOTIFICATION_CONVERSATIONS:
        convo_plugin.send(c, "Incident Daily Summary", {}, "", blocks=blocks)


@scheduler.add(every(5).minutes, name="calculate-incidents-cost")
@background_task
def calculate_incidents_cost(db_session=None):
    """Calculates the cost of all incidents."""

    # we want to update all incidents, all the time
    incidents = get_all(db_session=db_session)

    for incident in incidents:
        # we calculate the cost
        try:
            incident_cost = calculate_cost(incident.id, db_session)

            # if the cost hasn't changed don't continue
            if incident.cost == incident_cost:
                continue

            # we update the incident
            incident.cost = incident_cost
            db_session.add(incident)
            db_session.commit()

            if incident.ticket.resource_id:
                # we update the external ticket
                ticket_plugin = plugins.get(INCIDENT_PLUGIN_TICKET_SLUG)
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
