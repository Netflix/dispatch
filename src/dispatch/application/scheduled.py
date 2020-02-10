"""
.. module: dispatch.application.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.plugins.base import plugins
from dispatch.scheduler import scheduler
from dispatch.application import service as application_service
from dispatch.application.models import ApplicationCreate

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="application-sync")
@background_task
def sync_applications(db_session=None):
    """Syncs applications from external sources."""
    for p in plugins.all(plugin_type="application"):
        log.debug(f"Getting applications via: {p.slug}")
        for app in p.get():
            log.debug(f"Adding Application. Application: {app}")
            application_in = ApplicationCreate(**app)
            application = application_service.get_by_name(
                db_session=db_session, name=application_in.name
            )

            if application:
                application_service.update(
                    db_session=db_session, app=application, app_in=application_in
                )
            else:
                application_service.create(db_session=db_session, app_in=application_in)
