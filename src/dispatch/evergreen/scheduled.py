import logging

from typing import List
from schedule import every
from datetime import datetime
from collections import defaultdict

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task
from dispatch.scheduler import scheduler
from dispatch.config import DISPATCH_HELP_EMAIL
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.team import service as team_service
from dispatch.notification import service as notification_service
from dispatch.service import service as service_service


from dispatch.document import service as document_service


log = logging.getLogger(__name__)


def create_evergreen_reminder(
    db_session: SessionLocal, project: Project, owner_email: str, documents: List[Document]
):
    """Contains the logic for evergreen reminders."""
    # send email
    contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="email", project_id=project.id
    )
    if not plugin:
        log.warning("Document reminder not sent, no email plugin enabled.")
        return

    notification_template = EVERGREEN_REMINDER

    items = []
    for doc in documents:
        items.append(
            {
                "name": doc.name,
                "description": doc.description,
                "weblink": doc.weblink,
            }
        )
    notification_type = "evergreen-reminder"
    name = subject = notification_text = "Evergreen Reminder"
    plugin.instance.send(
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

    for item in items:
        doc.evergreen_last_reminder_at = datetime.utcnow()
        db_session.add(doc)

    db_session.commit()


def group_items_by_owner_and_type(items):
    """Groups documents by owner."""
    grouped = defaultdict(lambda: [])
    for item in items:
        grouped[item.evergreen_owner].append(item)
    return grouped


@scheduler.add(every(1).day.at("18:00"), name="evergreen-reminder")
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
        for owner, item_type, item in grouped_items.items():
            create_evergreen_reminder(db_session, project, owner, items)
