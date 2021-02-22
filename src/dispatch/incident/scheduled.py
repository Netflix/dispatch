import logging

from collections import defaultdict

from datetime import datetime, date
from schedule import every
from sqlalchemy import func

from dispatch.config import (
    DISPATCH_HELP_EMAIL,
    DISPATCH_UI_URL,
)
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.database import resolve_attr
from dispatch.decorators import background_task
from dispatch.messaging.strings import (
    INCIDENT,
    INCIDENT_DAILY_REPORT,
    INCIDENT_DAILY_REPORT_TITLE,
    MessageType,
)
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.notification import service as notification_service
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.search import service as search_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag

from .enums import IncidentStatus
from .flows import update_external_incident_ticket
from .messaging import send_incident_close_reminder
from .service import (
    calculate_cost,
    get_all,
    get_all_by_status,
    get_all_last_x_hours_by_status,
)


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


@scheduler.add(every(1).day.at("18:00"), name="incident-daily-report")
@background_task
def daily_report(db_session=None):
    """
    Creates and sends incident daily reports based on notifications.
    """
    # we fetch all active, stable and closed incidents
    active_incidents = get_all_by_status(db_session=db_session, status=IncidentStatus.active.value)
    stable_incidents = get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.stable.value, hours=24
    )
    closed_incidents = get_all_last_x_hours_by_status(
        db_session=db_session, status=IncidentStatus.closed.value, hours=24
    )
    incidents = active_incidents + stable_incidents + closed_incidents

    # we map incidents to notification filters
    incidents_notification_filters_mapping = defaultdict(lambda: defaultdict(lambda: []))
    notifications = notification_service.get_all_enabled(db_session=db_session)
    for incident in incidents:
        for notification in notifications:
            for search_filter in notification.filters:
                match = search_service.match(
                    db_session=db_session,
                    filter_spec=search_filter.expression,
                    class_instance=incident,
                )
                if match:
                    incidents_notification_filters_mapping[notification.id][
                        search_filter.id
                    ].append(incident)

            if not notification.filters:
                incidents_notification_filters_mapping[notification.id][0].append(incident)

    # we create and send an incidents daily report for each notification filter
    for notification_id, search_filter_dict in incidents_notification_filters_mapping.items():
        for search_filter_id, incidents in search_filter_dict.items():
            items_grouped = []
            items_grouped_template = INCIDENT

            for idx, incident in enumerate(incidents):
                try:
                    item = {
                        "commander_fullname": incident.commander.individual.name,
                        "commander_team": incident.commander.team,
                        "commander_weblink": incident.commander.individual.weblink,
                        "incident_id": incident.id,
                        "name": incident.name,
                        "priority": incident.incident_priority.name,
                        "priority_description": incident.incident_priority.description,
                        "status": incident.status,
                        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
                        "title": incident.title,
                        "type": incident.incident_type.name,
                        "type_description": incident.incident_type.description,
                    }

                    if incident.status != IncidentStatus.closed.value:
                        item.update(
                            {
                                "button_text": "Join Incident",
                                "button_value": str(incident.id),
                                "button_action": f"{ConversationButtonActions.invite_user.value}-{incident.status}-{idx}",
                            }
                        )

                    items_grouped.append(item)
                except Exception as e:
                    log.exception(e)

            notification_kwargs = {
                "contact_fullname": DISPATCH_HELP_EMAIL,
                "contact_weblink": DISPATCH_HELP_EMAIL,
                "items_grouped": items_grouped,
                "items_grouped_template": items_grouped_template,
            }

            notification_params = {
                "text": INCIDENT_DAILY_REPORT_TITLE,
                "type": MessageType.incident_daily_report,
                "template": INCIDENT_DAILY_REPORT,
                "kwargs": notification_kwargs,
            }

            notification = notification_service.get(
                db_session=db_session, notification_id=notification_id
            )

            notification_service.send(
                db_session=db_session,
                notification=notification,
                notification_params=notification_params,
            )


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
