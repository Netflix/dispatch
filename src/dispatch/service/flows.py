"""
.. module: dispatch.service.flows
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from sqlalchemy.orm import Session

from dispatch.plugin import service as plugin_service
from dispatch.service.models import Service


log = logging.getLogger(__name__)


def resolve_oncall(service: Service, db_session: Session) -> str:
    """Resolves the oncall for a service."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=service.project.id, plugin_type="oncall"
    )
    if not plugin:
        log.warning("Oncall not resolved. No oncall plugin enabled.")
        return

    email_address = plugin.instance.get(service_id=service.external_id)

    if not email_address:
        log.warning("Email address for oncall service not returned.")
        return

    return email_address
