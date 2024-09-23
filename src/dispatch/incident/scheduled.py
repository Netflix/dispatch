import logging

from collections import defaultdict

from datetime import datetime, date
from schedule import every
from sqlalchemy import func
from sqlalchemy.orm import Session

from dispatch.enums import Visibility
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.database.core import resolve_attr
from dispatch.decorators import scheduled_project_task, timer
from dispatch.messaging.strings import (
    INCIDENT,
    INCIDENT_DAILY_REPORT,
    INCIDENT_DAILY_REPORT_TITLE,
    INCIDENT_WEEKLY_REPORT,
    INCIDENT_WEEKLY_REPORT_TITLE,
    INCIDENT_SUMMARY_TEMPLATE,
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


@scheduler.add(every(1).hours, name="incident-auto-tagger")
@timer
@scheduled_project_task
def incident_auto_tagger(db_session: Session, project: Project):
    """Attempts to take existing tags and associate them with incidents."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="storage"
    )

    if not plugin:
        log.warning(
            f"Incident tags not updated. No storage plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    tags = tag_service.get_all(db_session=db_session, project_id=project.id).all()
    tag_strings = [t.name.lower() for t in tags if t.discoverable]
    phrases = build_term_vocab(tag_strings)
    matcher = build_phrase_matcher("dispatch-tag", phrases)

    incidents = get_all(db_session=db_session, project_id=project.id).all()

    for incident in incidents:
        log.debug(f"Processing incident {incident.name}...")

        if incident.incident_document:
            try:
                mime_type = "text/plain"
                text = plugin.instance.get(incident.incident_document.resource_id, mime_type)
            except Exception as e:
                log.warn(e)
                continue

            extracted_tags = list(set(extract_terms_from_text(text, matcher)))

            matched_tags = (
                db_session.query(Tag)
                .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
                .all()
            )

            incident.tags.extend(matched_tags)
            db_session.commit()

            log.debug(f"Associating tags with incident {incident.name}. Tags: {extracted_tags}")


@scheduler.add(every(1).day.at("18:00"), name="incident-report-daily")
@timer
@scheduled_project_task
def incident_report_daily(db_session: Session, project: Project):
    """Creates and sends incident daily reports based on notifications."""

    # don't send if set to false
    if project.send_daily_reports is False:
        return

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
                    subject=search_filter.subject,
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
        for _search_filter_id, incidents in search_filter_dict.items():
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
                        if incident.project.allow_self_join:
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
@timer
@scheduled_project_task
def incident_close_reminder(db_session: Session, project: Project):
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


@scheduler.add(every().monday.at("18:00"), name="incident-report-weekly")
@timer
@scheduled_project_task
def incident_report_weekly(db_session: Session, project: Project):
    """Creates and sends incident weekly reports based on notifications."""

    # don't send if set to false or no notification id is set
    if project.send_weekly_reports is False or not project.weekly_report_notification_id:
        return

    # don't send if no enabled ai plugin
    ai_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="artificial-intelligence", project_id=project.id
    )
    if not ai_plugin:
        log.warning("Incident weekly reports not sent. No AI plugin enabled.")
        return

    # we fetch all closed incidents in the last week
    incidents = get_all_last_x_hours_by_status(
        db_session=db_session,
        project_id=project.id,
        status=IncidentStatus.closed,
        hours=24 * 7,
    )

    # no incidents closed in the last week
    if not incidents:
        return

    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="storage", project_id=project.id
    )

    if not storage_plugin:
        log.warning(
            f"Incident weekly reports not sent. No storage plugin enabled. Project: {project.name}."
        )
        return

    # we create and send an incidents weekly report
    for incident in incidents:
        items_grouped = []
        items_grouped_template = INCIDENT_SUMMARY_TEMPLATE

        # Skip restricted incidents
        if incident.visibility == Visibility.restricted:
            continue
        try:
            pir_doc = storage_plugin.instance.get(
                file_id=incident.incident_review_document.resource_id,
                mime_type="text/plain",
            )
            messages = {
                "role": "user",
                "content": """Given the text of the security post-incident review document below,
                provide answers to the following questions:
                1. What is the summary of what happened?
                2. What were the overall risk(s)?
                3. How were the risk(s) mitigated?
                4. How was the incident resolved?
                5. What are the follow-up tasks?
                """
                + pir_doc,
            }

            response = ai_plugin.instance.chat_completion(messages)
            summary = response["choices"][0]["message"]["content"]

            item = {
                "commander_fullname": incident.commander.individual.name,
                "commander_team": incident.commander.team,
                "commander_weblink": incident.commander.individual.weblink,
                "name": incident.name,
                "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
                "title": incident.title,
                "summary": summary,
            }

            items_grouped.append(item)
        except Exception as e:
            log.exception(e)

    notification_kwargs = {
        "items_grouped": items_grouped,
        "items_grouped_template": items_grouped_template,
    }

    notification_title_text = f"{project.name} {INCIDENT_WEEKLY_REPORT_TITLE}"
    notification_params = {
        "text": notification_title_text,
        "type": MessageType.incident_weekly_report,
        "template": INCIDENT_WEEKLY_REPORT,
        "kwargs": notification_kwargs,
    }

    notification = notification_service.get(
        db_session=db_session, notification_id=project.weekly_report_notification_id
    )

    notification_service.send(
        db_session=db_session,
        project_id=notification.project.id,
        notification=notification,
        notification_params=notification_params,
    )
