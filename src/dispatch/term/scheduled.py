"""
.. module: dispatch.term.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.term import service as term_service
from dispatch.term.models import TermCreate

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="term-sync")
@background_task
def sync_terms(db_session=None):
    """Syncs terms from external sources."""
    for p in plugins.all(plugin_type="term"):
        log.debug(f"Getting terms via: {p.slug}")
        for t in p.get():
            log.debug(f"Adding Term. Term: {t}")
            term_in = TermCreate(**t)
            term = term_service.get_by_text(db_session=db_session, text=term_in.text)

            if term:
                term_service.update(db_session=db_session, term=term, term_in=term_in)
            else:
                term_service.create(db_session=db_session, term_in=term_in)
