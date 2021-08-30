"""
.. module: dispatch.plugins.google_gmail.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from typing import Any
from schedule import every
from datetime import datetime
from collections import defaultdict

from dispatch.database.core import SessionLocal
from dispatch.messaging.strings import EVERGREEN_REMINDER
from dispatch.decorators import scheduled_project_task
from dispatch.scheduler import scheduler
from dispatch.config import DISPATCH_HELP_EMAIL, DISPATCH_UI_URL
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.team import service as team_service
from dispatch.notification import service as notification_service
from dispatch.service import service as service_service
from dispatch.document import service as document_service


log = logging.getLogger(__name__)


def create_evergreen_reminder(
    db_session: SessionLocal, project: Project, owner_email: str, resource_groups: Any
):
    """Contains the logic for evergreen reminders."""
    contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="email", project_id=project.id
    )
    if not plugin:
        log.warning("Evergreen reminder not sent, no email plugin enabled.")
        return

    notification_template = EVERGREEN_REMINDER

    items = []
    for resource_type, resources in resource_groups.items():
        for resource in resources:
            weblink = getattr(resource, "weblink", None)
            if not weblink:
                weblink = DISPATCH_UI_URL

            items.append(
                {
                    "resource_type": resource_type.replace("_", " ").title(),
                    "name": resource.name,
                    "description": getattr(resource, "description", None),
                    "weblink": weblink,
                }
            )

    notification_type = "evergreen-reminder"
    name = subject = notification_text = "Evergreen Reminder"
    success = plugin.instance.send(
        owner_email,
        notification_text,
        notification_template,
        notification_type,
        name=name,
        subject=subject,
        contact_fullname=contact_fullname,
        contact_weblink=contact_weblink,
        items=items,  # plugin expect dicts
    )

    if success:
        for item in items:
            item.evergreen_last_reminder_at = datetime.utcnow()

        db_session.commit()
    else:
        log.error(f"Unable to send evergreen message. Email: {owner_email}")


def group_items_by_owner_and_type(items):
    """Groups documents by owner."""
    grouped = defaultdict(lambda: defaultdict(lambda: []))
    for item in items:
        grouped[item.evergreen_owner][item.__tablename__].append(item)
    return grouped


@scheduler.add(every().monday.at("18:00"), name="evergreen-reminder")
@scheduled_project_task
def create_evergreen_reminders(db_session: SessionLocal, project: Project):
    """Sends reminders for items that have evergreen enabled."""

    items = []
    items += document_service.get_overdue_evergreen_documents(
        db_session=db_session, project_id=project.id
    )

    items += service_service.get_overdue_evergreen_services(
        db_session=db_session, project_id=project.id
    )

    items += team_service.get_overdue_evergreen_teams(db_session=db_session, project_id=project.id)

    items += notification_service.get_overdue_evergreen_notifications(
        db_session=db_session, project_id=project.id
    )

    if items:
        grouped_items = group_items_by_owner_and_type(items)
        for owner, items in grouped_items.items():
            create_evergreen_reminder(db_session, project, owner, items)
