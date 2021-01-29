import logging

from dispatch.database import SessionLocal
from dispatch.plugin import service as plugin_service

from .service import get_by_external_id


log = logging.getLogger(__name__)


def get_oncall_email(external_id: str, db_session: SessionLocal):
    oncall_service = get_by_external_id(db_session=db_session, external_id=external_id)
    if not oncall_service:
        log.warning(
            f"INCIDENT_ONCALL_SERVICE_ID configured in the .env file, but its value {external_id} not found in the database. Did you create the oncall service in the Web UI?"
        )
        return

    oncall_plugin = plugin_service.get_active(db_session=db_session, plugin_type="oncall")
    if not oncall_plugin:
        log.warning(
            f"Unable to resolve the oncall. INCIDENT_ONCALL_SERVICE_ID configured, but associated plugin ({oncall_plugin.slug}) is not enabled."
        )
        return

    if oncall_plugin.slug != oncall_service.type:
        log.warning(
            f"Unable to resolve the oncall. The oncall plugin enabled is not of type {oncall_plugin.slug}."
        )
        return

    oncall_email = oncall_plugin.instance.get(service_id=external_id)
    return oncall_email
