import logging

from datetime import datetime, date
from schedule import every
from sqlalchemy import func

from dispatch.config import (
    DISPATCH_UI_URL,
    INCIDENT_ONCALL_SERVICE_ID,
    INCIDENT_NOTIFICATION_CONVERSATIONS,
)
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.database import resolve_attr
from dispatch.decorators import background_task
from dispatch.enums import Visibility
from dispatch.individual import service as individual_service
from dispatch.messaging import (
    INCIDENT_DAILY_SUMMARY_ACTIVE_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_NO_ACTIVE_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_NO_STABLE_CLOSED_INCIDENTS_DESCRIPTION,
    INCIDENT_DAILY_SUMMARY_STABLE_CLOSED_INCIDENTS_DESCRIPTION,
)
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from dispatch.plugin import service as plugin_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag

from .enums import IncidentStatus
from .flows import update_external_incident_ticket
from .service import (
    calculate_cost,
    get_all,
    get_all_by_status,
    get_all_last_x_hours_by_status,
)
from .messaging import send_incident_close_reminder


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

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")

    for incident in get_all(db_session=db_session).all():
        log.debug(f"Processing incident. Name: {incident.name}")

        doc = incident.incident_document

        if doc:
            try:
                mime_type = "text/plain"
                text = plugin.instance.get(doc.resource_id, mime_type)
            except Exception as e:
                log.debug(f"Failed to get document. Reason: {e}")
                log.exception(e)
                continue

            extracted_tags = list(set(extract_terms_from_text(text, matcher)))

            matched_tags = (
                db_session.query(Tag)
                .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
                .all()
            )

            incident.tags.extend(matched_tags)
            db_session.commit()

            log.debug(
                f"Associating tags with incident. Incident: {incident.name}, Tags: {extracted_tags}"
            )


@scheduler.add(every(1).day.at("18:00"), name="incident-daily-summary")
@background_task
def daily_summary(db_session=None):
    """Fetches all open incidents and provides a daily summary."""

    blocks = []
    blocks.append(
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{INCIDENT_DAILY_SUMMARY_DESCRIPTION}",
            },
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
            ticket_weblink = resolve_attr(incident, "ticket.weblink")
            if incident.visibility == Visibility.open:
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{ticket_weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Type*: {incident.incident_type.name}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Incident Commander*: <{incident.commander.weblink}|{incident.commander.name}>"
                                ),
                            },
                            "block_id": f"{ConversationButtonActions.invite_user}-active-{idx}",
                            "accessory": {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Join Incident"},
                                "value": f"{incident.id}",
                            },
                        }
                    )
                except Exception as e:
                    log.exception(e)

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"For more information about active incidents, please visit the active incidents status <{DISPATCH_UI_URL}/incidents/status|page>.",
                    }
                ],
            }
        )
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
    stable_incidents = get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.stable, hours=hours
    )
    closed_incidents = get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.closed, hours=hours
    )
    if stable_incidents or closed_incidents:
        for idx, incident in enumerate(stable_incidents):
            ticket_weblink = resolve_attr(incident, "ticket.weblink")

            if incident.visibility == Visibility.open:
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{ticket_weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Type*: {incident.incident_type.name}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Incident Commander*: <{incident.commander.weblink}|{incident.commander.name}>\n"
                                    f"*Status*: {incident.status}"
                                ),
                            },
                            "block_id": f"{ConversationButtonActions.invite_user}-stable-{idx}",
                            "accessory": {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Join Incident"},
                                "value": f"{incident.id}",
                            },
                        }
                    )
                except Exception as e:
                    log.exception(e)

        for incident in closed_incidents:
            ticket_weblink = resolve_attr(incident, "ticket.weblink")

            if incident.visibility == Visibility.open:
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{ticket_weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Type*: {incident.incident_type.name}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Incident Commander*: <{incident.commander.weblink}|{incident.commander.name}>\n"
                                    f"*Status*: {incident.status}"
                                ),
                            },
                        }
                    )
                except Exception as e:
                    log.exception(e)
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

    # NOTE INCIDENT_ONCALL_SERVICE_ID is optional
    if INCIDENT_ONCALL_SERVICE_ID:
        oncall_service = service_service.get_by_external_id(
            db_session=db_session, external_id=INCIDENT_ONCALL_SERVICE_ID
        )

        if not oncall_service:
            log.warning(
                "Oncall service ID specified, but not found in the database. Did you create it?"
            )
            return

        oncall_plugin = plugins.get(oncall_service.type)
        oncall_email = oncall_plugin.get(service_id=INCIDENT_ONCALL_SERVICE_ID)

        oncall_individual = individual_service.resolve_user_by_email(oncall_email, db_session)

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"For any questions about this notification, please reach out to <{oncall_individual['weblink']}|{oncall_individual['fullname']}> (current on-call)",
                    }
                ],
            }
        )

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")

    for c in INCIDENT_NOTIFICATION_CONVERSATIONS:
        plugin.instance.send(c, "Incident Daily Summary", {}, "", blocks=blocks)


@scheduler.add(every(5).minutes, name="calculate-incidents-cost")
@background_task
def calculate_incidents_cost(db_session=None):
    """Calculates the cost of all incidents."""

    # we want to update all incidents, all the time
    incidents = get_all(db_session=db_session)
    for incident in incidents:
        try:
            # we calculate the cost
            incident_cost = calculate_cost(incident.id, db_session)

            # if the cost hasn't changed, don't continue
            if incident.cost == incident_cost:
                continue

            # we update the incident
            incident.cost = incident_cost
            db_session.add(incident)
            db_session.commit()

            log.debug(f"Incident cost for {incident.name} updated in the database.")

            if incident.ticket:
                # we update the external ticket
                update_external_incident_ticket(incident, db_session)
                log.debug(f"Incident cost for {incident.name} updated in the ticket.")
            else:
                log.debug(f"Ticket not found. Incident cost for {incident.name} not updated.")

        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            log.exception(e)


@scheduler.add(every(1).day.at("18:00"), name="incident-status-reminder")
@background_task
def close_incident_reminder(db_session=None):
    """Sends a reminder to the IC to close out their incident."""
    incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.stable)

    for incident in incidents:
        span = datetime.utcnow() - incident.stable_at
        q, r = divmod(span.days, 7)  # only for incidents that have been stable longer than a week
        if q >= 1 and r == 0:
            if date.today().isoweekday() == 1:  # lets only send on mondays
                send_incident_close_reminder(incident, db_session)
