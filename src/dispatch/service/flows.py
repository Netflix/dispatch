import logging

from dispatch.database.core import SessionLocal
from dispatch.service.models import Service
from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def resolve_oncall(service: Service, db_session: SessionLocal) -> str:
    """Uses the active oncall plugin to resolve a given oncall service to its email address."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=service.project.id, plugin_type="oncall"
    )
    if not plugin:
        log.warning("Oncall service not resolved. No oncall plugin enabled.")
        return

    email_address = plugin.instance.get(service_id=service.external_id)

    if not email_address:
        log.warning("Email address for oncall service not returned.")
        return

    return email_address
