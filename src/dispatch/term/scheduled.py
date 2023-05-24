"""
.. module: dispatch.term.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.term import service as term_service
from dispatch.term.models import TermCreate

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="sync-terms")
@timer
@scheduled_project_task
def sync_terms(db_session: SessionLocal, project: Project):
    """Syncs terms from external sources."""
    term_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="term"
    )

    if not term_plugin:
        log.warning(
            f"Skipping syncing terms. No term plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    for t in term_plugin.instance.get():
        log.debug(f"Adding term {t} to {project.name} project.")
        term_in = TermCreate(**t)
        term = term_service.get_by_text(db_session=db_session, text=term_in.text)

        if term:
            term_service.update(db_session=db_session, term=term, term_in=term_in)
        else:
            term_service.create(db_session=db_session, term_in=term_in)
