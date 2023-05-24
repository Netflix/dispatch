"""
.. module: dispatch.task.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging

from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.task import service as task_service

from .flows import create_reminder, group_tasks_by_assignee, create_or_update_task


TASK_REMINDERS_INTERVAL = 3600  # seconds
TASK_SYNC_INTERVAL = 30  # seconds

log = logging.getLogger(__name__)


@scheduler.add(every(TASK_REMINDERS_INTERVAL).seconds, name="create-incident-tasks-reminders")
@scheduled_project_task
def create_incident_tasks_reminders(db_session: SessionLocal, project: Project):
    """Creates incident tasks reminders."""
    overdue_tasks = task_service.get_overdue_tasks(db_session=db_session, project_id=project.id)
    log.debug(f"Overdue tasks in {project.name} project that need reminders: {len(overdue_tasks)}")

    tasks = [t for t in overdue_tasks if t.incident.status == IncidentStatus.active]

    if tasks:
        grouped_tasks = group_tasks_by_assignee(tasks)
        for assignee, tasks in grouped_tasks.items():
            create_reminder(db_session, assignee, tasks, project.id)


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
            try:
                tasks = task_plugin.instance.list(file_id=document.resource_id, lookback=lookback)
            except Exception as e:
                log.warn(f"Unable to list tasks in document {document.resource_id}. Error: {e}")
                continue

            for task in tasks:
                # we get the task information
                try:
                    create_or_update_task(
                        db_session, incident, task, notify=notify, sync_external=False
                    )
                except Exception as e:
                    log.exception(e)


@scheduler.add(every(1).day, name="sync-incident-tasks-daily")
@timer
@scheduled_project_task
def sync_incident_tasks_daily(db_session: SessionLocal, project: Project):
    """Syncs all incident tasks daily."""
    incidents = incident_service.get_all(db_session=db_session, project_id=project.id).all()
    task_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="task"
    )

    if not task_plugin:
        log.warning(
            f"Daily incident tasks sync skipped. No task plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    lookback = 60 * 60 * 24  # 24hrs
    sync_tasks(db_session, task_plugin, incidents, lookback=lookback, notify=False)


@scheduler.add(every(TASK_SYNC_INTERVAL).seconds, name="sync-active-stable-incident-tasks")
@timer
@scheduled_project_task
def sync_active_stable_incident_tasks(db_session: SessionLocal, project: Project):
    """Syncs active and stable incident tasks."""
    task_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="task"
    )

    if not task_plugin:
        log.warning(
            f"Active and stable incident tasks sync skipped. No task plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )

    incidents = active_incidents + stable_incidents
    lookback = 60 * 10  # 10 min
    sync_tasks(db_session, task_plugin, incidents, lookback=lookback, notify=True)
