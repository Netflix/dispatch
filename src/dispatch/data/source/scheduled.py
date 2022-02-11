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

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="source-sync")
@scheduled_task
def sync_sources(db_session: SessionLocal):
    """Syncs sources from external sources."""
    pass
