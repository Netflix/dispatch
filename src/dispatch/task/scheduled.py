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
)
from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.individual import service as individual_service
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service
from dispatch.task import service as task_service

from .flows import create_reminder, group_tasks_by_assignee, create_or_update_task


TASK_REMINDERS_INTERVAL = 3600  # seconds
TASK_SYNC_INTERVAL = 30  # seconds

log = logging.getLogger(__name__)


@scheduler.add(every(TASK_REMINDERS_INTERVAL).seconds, name="incident-task-reminders")
@scheduled_project_task
def create_task_reminders(db_session: SessionLocal, project: Project):
    """Creates multiple task reminders."""
    tasks = task_service.get_overdue_tasks(db_session=db_session, project_id=project.id)
    log.debug(f"New tasks that need reminders. NumTasks: {len(tasks)}")

    # let's only remind for active incidents for now
    tasks = [t for t in tasks if t.incident.status == IncidentStatus.active]

    if tasks:
        contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL

        # NOTE INCIDENT_ONCALL_SERVICE_ID is optional
        if INCIDENT_ONCALL_SERVICE_ID:
            oncall_service = service_service.get_by_external_id(
                db_session=db_session, external_id=INCIDENT_ONCALL_SERVICE_ID
            )

            if not oncall_service:
                log.warning(
                    "INCIDENT_ONCALL_SERVICE_ID configured in the .env file, but not found in the database. Did you create the oncall service in the UI?"
                )
                return

            oncall_plugin = plugin_service.get_active_instance(
                db_session=db_session, project_id=project.id, plugin_type="oncall"
            )

            if not oncall_plugin:
                log.warning(
                    f"Unable to resolve oncall. No oncall plugin is enabled. Project: {project.name}"
                )

            if oncall_plugin.plugin.slug != oncall_service.type:
                log.warning(
                    f"Unable to resolve the oncall. Oncall plugin enabled not of type {oncall_plugin.plugin.slug}."
                )
                return

            if not oncall_plugin:
                log.warning(
                    f"Unable to resolve the oncall, INCIDENT_ONCALL_SERVICE_ID configured, but associated plugin ({oncall_plugin.plugin.slug}) is not enabled."
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


def sync_tasks(db_session, task_plugin, incidents, lookback: int = 60, notify: bool = False):
    """Syncs tasks and sends update notifications to incident channels."""
    for incident in incidents:
        for document in [
            incident.incident_document,
            incident.incident_review_document,
        ]:
            if not document:
                # the document may have not been created yet (e.g. incident review document)
                break

            # we get the list of tasks in the document
            tasks = task_plugin.instance.list(file_id=document.resource_id, lookback=lookback)

            for task in tasks:
                # we get the task information
                try:
                    create_or_update_task(
                        db_session, incident, task, notify=notify, sync_external=False
                    )
                except Exception as e:
                    log.exception(e)


@scheduler.add(every(1).day, name="incident-daily-task-sync")
@scheduled_project_task
def daily_sync_task(db_session: SessionLocal, project: Project):
    """Syncs all incident tasks daily."""
    incidents = incident_service.get_all(db_session=db_session, project_id=project.id).all()
    task_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="task"
    )

    if not task_plugin:
        log.warning(f"Skipping task sync no task plugin enabled. ProjectId: {project.id}")
        return

    lookback = 60 * 60 * 24  # 24hrs
    sync_tasks(db_session, task_plugin, incidents, lookback=lookback, notify=False)


@scheduler.add(every(TASK_SYNC_INTERVAL).seconds, name="incident-task-sync")
@scheduled_project_task
def sync_active_stable_tasks(db_session: SessionLocal, project: Project):
    """Syncs incident tasks."""
    task_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="task"
    )

    if not task_plugin:
        log.warning(f"Skipping task sync no task plugin enabled. ProjectId: {project.id}")
        return

    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )

    incidents = active_incidents + stable_incidents
    sync_tasks(db_session, task_plugin, incidents, lookback=TASK_SYNC_INTERVAL, notify=True)
