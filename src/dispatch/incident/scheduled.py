import logging

from collections import defaultdict

from datetime import datetime, date
from schedule import every
from sqlalchemy import func

from dispatch.conversation.enums import ConversationButtonActions
from dispatch.database.core import SessionLocal, resolve_attr
from dispatch.decorators import scheduled_project_task
from dispatch.messaging.strings import (
    INCIDENT,
    INCIDENT_DAILY_REPORT,
    INCIDENT_DAILY_REPORT_TITLE,
    MessageType,
)
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.notification import service as notification_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.search_filter import service as search_filter_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag

from .enums import IncidentStatus
from .messaging import send_incident_close_reminder
from .service import (
    get_all,
    get_all_by_status,
    get_all_last_x_hours_by_status,
)


log = logging.getLogger(__name__)


@scheduler.add(every(1).hours, name="incident-tagger")
@scheduled_project_task
def auto_tagger(db_session: SessionLocal, project: Project):
    """Attempts to take existing tags and associate them with incidents."""
    tags = tag_service.get_all(db_session=db_session, project_id=project.id).all()
    log.debug(f"Fetched {len(tags)} tags from database.")

    tag_strings = [t.name.lower() for t in tags if t.discoverable]
    phrases = build_term_vocab(tag_strings)
    matcher = build_phrase_matcher("dispatch-tag", phrases)

    for incident in get_all(db_session=db_session, project_id=project.id).all():
        plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="storage"
        )

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
@scheduled_project_task
def daily_report(db_session: SessionLocal, project: Project):
    """Creates and sends incident daily reports based on notifications."""
    # we fetch all active, stable and closed incidents
    active_incidents = get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = get_all_last_x_hours_by_status(
        db_session=db_session,
        project_id=project.id,
        status=IncidentStatus.stable,
        hours=24,
    )
    closed_incidents = get_all_last_x_hours_by_status(
        db_session=db_session,
        project_id=project.id,
        status=IncidentStatus.closed,
        hours=24,
    )
    incidents = active_incidents + stable_incidents + closed_incidents

    # we map incidents to notification filters
    incidents_notification_filters_mapping = defaultdict(lambda: defaultdict(lambda: []))
    notifications = notification_service.get_all_enabled(
        db_session=db_session, project_id=project.id
    )
    for incident in incidents:
        for notification in notifications:
            for search_filter in notification.filters:
                match = search_filter_service.match(
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
                        "buttons": [],
                        "commander_fullname": incident.commander.individual.name,
                        "commander_team": incident.commander.team,
                        "commander_weblink": incident.commander.individual.weblink,
                        "incident_id": incident.id,
                        "name": incident.name,
                        "organization_slug": incident.project.organization.slug,
                        "priority": incident.incident_priority.name,
                        "priority_description": incident.incident_priority.description,
                        "severity": incident.incident_severity.name,
                        "severity_description": incident.incident_severity.description,
                        "status": incident.status,
                        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
                        "title": incident.title,
                        "type": incident.incident_type.name,
                        "type_description": incident.incident_type.description,
                    }

                    if incident.status != IncidentStatus.closed:
                        item["buttons"].append(
                            {
                                "button_text": "Subscribe",
                                "button_value": f"{incident.project.organization.slug}-{incident.id}",
                                "button_action": f"{ConversationButtonActions.subscribe_user}-{incident.status}-{idx}",
                            }
                        )
                        item["buttons"].append(
                            {
                                "button_text": "Join",
                                "button_value": f"{incident.project.organization.slug}-{incident.id}",
                                "button_action": f"{ConversationButtonActions.invite_user}-{incident.status}-{idx}",
                            }
                        )

                    items_grouped.append(item)
                except Exception as e:
                    log.exception(e)

            notification_kwargs = {
                "items_grouped": items_grouped,
                "items_grouped_template": items_grouped_template,
            }

            notification_title_text = f"{project.name} {INCIDENT_DAILY_REPORT_TITLE}"
            notification_params = {
                "text": notification_title_text,
                "type": MessageType.incident_daily_report,
                "template": INCIDENT_DAILY_REPORT,
                "kwargs": notification_kwargs,
            }

            notification = notification_service.get(
                db_session=db_session, notification_id=notification_id
            )

            notification_service.send(
                db_session=db_session,
                project_id=notification.project.id,
                notification=notification,
                notification_params=notification_params,
            )


@scheduler.add(every(1).day.at("18:00"), name="incident-close-reminder")
@scheduled_project_task
def incident_close_reminder(db_session: SessionLocal, project: Project):
    """Sends a reminder to the incident commander to close out their incident."""
    incidents = get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )

    for incident in incidents:
        span = datetime.utcnow() - incident.stable_at
        q, r = divmod(span.days, 7)
        if q >= 1 and date.today().isoweekday() == 1:
            # we only send the reminder for incidents that have been stable
            # longer than a week and only on Mondays
            send_incident_close_reminder(incident, db_session)
