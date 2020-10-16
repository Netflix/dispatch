"""
.. module: dispatch.task.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging

from schedule import every

from dispatch.config import (
    DISPATCH_HELP_EMAIL,
    INCIDENT_ONCALL_SERVICE_ID,
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
)
from dispatch.decorators import background_task
from dispatch.document.service import get_by_incident_id_and_resource_type as get_document
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from dispatch.task import service as task_service

from .flows import create_reminder, group_tasks_by_assignee, create_or_update_task


TASK_REMINDERS_INTERVAL = 3600  # seconds
TASK_SYNC_INTERVAL = 30  # seconds

log = logging.getLogger(__name__)


@scheduler.add(every(TASK_REMINDERS_INTERVAL).seconds, name="incident-task-reminders")
@background_task
def create_task_reminders(db_session=None):
    """Creates multiple task reminders."""
    tasks = task_service.get_overdue_tasks(db_session=db_session)
    log.debug(f"New tasks that need reminders. NumTasks: {len(tasks)}")
    # lets only remind for active incidents for now
    tasks = [t for t in tasks if t.incident.status == IncidentStatus.active]
    if tasks:
        contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
        # NOTE INCIDENT_ONCALL_SERVICE_ID is optional
        if INCIDENT_ONCALL_SERVICE_ID:
            oncall_service = service_service.get_by_external_id(
                db_session=db_session, external_id=INCIDENT_ONCALL_SERVICE_ID
            )
            oncall_plugin = plugin_service.get_by_slug(
                db_session=db_session, slug=oncall_service.type
            )
            if not oncall_plugin.enabled:
                log.warning(
                    f"Unable to resolve oncall, INCIDENT_ONCALL_SERVICE_ID configured but associated plugin ({oncall_plugin.slug}) is not enabled."
                )
                contact_fullname = "Unknown"
                contact_weblink = None
            else:
                oncall_email = oncall_plugin.instance.get(service_id=INCIDENT_ONCALL_SERVICE_ID)
                oncall_individual = individual_service.resolve_user_by_email(
                    oncall_email, db_session
                )
                contact_fullname = oncall_individual["fullname"]
                contact_weblink = oncall_individual["weblink"]

        grouped_tasks = group_tasks_by_assignee(tasks)
        for assignee, tasks in grouped_tasks.items():
            create_reminder(db_session, assignee, tasks, contact_fullname, contact_weblink)


def sync_tasks(db_session, incidents, notify: bool = False):
    """Syncs tasks and sends update notifications to incident channels."""
    drive_task_plugin = plugin_service.get_active(db_session=db_session, plugin_type="task")
    for incident in incidents:
        for doc_type in [
            INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
            INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
        ]:
            try:
                # we get the document object
                document = get_document(
                    db_session=db_session, incident_id=incident.id, resource_type=doc_type
                )

                if not document:
                    # the document may have not been created yet (e.g. incident review document)
                    break

                # we get the list of tasks in the document
                tasks = drive_task_plugin.instance.list(file_id=document.resource_id)

                for task in tasks:
                    # we get the task information
                    try:
                        create_or_update_task(db_session, incident, task["task"], notify=notify)
                    except Exception as e:
                        log.exception(e)
            except Exception as e:
                log.exception(e)


@scheduler.add(every(1).day, name="incident-daily-task-sync")
@background_task
def daily_sync_task(db_session=None):
    """Syncs all incident tasks daily."""
    incidents = incident_service.get_all(db_session=db_session).all()
    sync_tasks(db_session, incidents, notify=False)


@scheduler.add(every(TASK_SYNC_INTERVAL).seconds, name="incident-task-sync")
@background_task
def sync_active_stable_tasks(db_session=None):
    """Syncs incident tasks."""
    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents
    sync_tasks(db_session, incidents, notify=True)
