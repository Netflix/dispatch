"""
.. module: dispatch.evergreen.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from collections import defaultdict
from datetime import datetime
from schedule import every
from typing import Any

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.document import service as document_service
from dispatch.messaging.strings import EVERGREEN_REMINDER
from dispatch.notification import service as notification_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from dispatch.team import service as team_service


log = logging.getLogger(__name__)


def create_evergreen_reminder(
    db_session: SessionLocal, project: Project, owner_email: str, resource_groups: Any
):
    """Contains the logic for evergreen reminders."""
    if not owner_email:
        log.warning(
            "Evergreen reminder not sent. No owner email. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="email", project_id=project.id
    )
    if not plugin:
        log.warning(
            "Evergreen reminder not sent. No email plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    items = []
    for resource_type, resources in resource_groups.items():
        for resource in resources:
            weblink = getattr(resource, "weblink", "N/A")
            items.append(
                {
                    "description": getattr(resource, "description", None),
                    "name": resource.name,
                    "project": resource.project.name,
                    "resource_type": resource_type.replace("_", " ").title(),
                    "weblink": weblink,
                }
            )

    notification_template = EVERGREEN_REMINDER
    notification_type = "evergreen-reminder"
    name = subject = notification_text = "Evergreen Reminder"

    # Can raise exception "tenacity.RetryError: RetryError". (Email may still go through).
    success = False
    try:
        success = plugin.instance.send(
            owner_email,
            notification_text,
            notification_template,
            notification_type,
            name=name,
            subject=subject,
            items=items,  # plugin expect dicts
        )
    except Exception as e:
        log.error(f"Error in sending {notification_text} email to {owner_email}: {e}")

    if not success:
        log.error(f"Unable to send evergreen message. Email: {owner_email}")
        return

    # we set the evergreen last reminder at time to now
    for _, resources in resource_groups.items():
        for resource in resources:
            resource.evergreen_last_reminder_at = datetime.utcnow()

    db_session.commit()


def group_items_by_owner_and_type(items):
    """Groups items by owner."""
    grouped = defaultdict(lambda: defaultdict(lambda: []))
    for item in items:
        grouped[item.evergreen_owner][item.__tablename__].append(item)
    return grouped


@scheduler.add(every().monday.at("18:00"), name="create-evergreen-reminders")
@timer
@scheduled_project_task
def create_evergreen_reminders(db_session: SessionLocal, project: Project):
    """Sends reminders for items that have evergreen enabled."""
    items = []

    # Overdue evergreen documents
    items += document_service.get_overdue_evergreen_documents(
        db_session=db_session, project_id=project.id
    )

    # Overdue evergreen oncall services
    items += service_service.get_overdue_evergreen_services(
        db_session=db_session, project_id=project.id
    )

    # Overdue evergreen teams
    items += team_service.get_overdue_evergreen_teams(db_session=db_session, project_id=project.id)

    # Overdue evergreen notifications
    items += notification_service.get_overdue_evergreen_notifications(
        db_session=db_session, project_id=project.id
    )

    if items:
        grouped_items = group_items_by_owner_and_type(items)
        for owner, items in grouped_items.items():
            create_evergreen_reminder(db_session, project, owner, items)
