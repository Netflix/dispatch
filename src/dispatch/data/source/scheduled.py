"""
.. module: dispatch.source.scheduled
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every
from dispatch.database.core import SessionLocal
from dispatch.scheduler import scheduler
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.data.source import service as source_service
from dispatch.decorators import scheduled_project_task

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="source-sync")
@scheduled_project_task
def sync_sources(db_session: SessionLocal, project: Project):
    """Syncs sources from external sources."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="source", project_id=project.id
    )

    if not plugin:
        log.debug(f"No active plugins were found. PluginType: 'source' ProjectId: {project.id}")
        return

    log.debug(f"Getting source information via: {plugin.plugin.slug}")

    sources = source_service.get_all(db_session=db_session, project_id=project.id)

    for s in sources:
        log.debug(f"Syncing Source. Source: {s}")
        if not s.external_id:
            log.debug(f"Skipping source, no externalId Source: {s}")
            continue

        data = plugin.instance.get(external_id=s.external_id)

        if data:
            for k, v in data.items():
                setattr(s, k, v)

            db_session.commit()
