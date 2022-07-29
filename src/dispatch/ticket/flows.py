from typing import Any
import logging

from dispatch.enums import Visibility
from dispatch.database import SessionLocal
from dispatch.plugin import service as plugin_service
from dispatch.database import service as database_service

log = logging.getLogger(__name__)


def create_ticket(obj: Any, db_session: SessionLocal):
    """Creates a ticket."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=obj.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Case ticket not created. No ticket plugin enabled.")
        return

    title = obj.title
    if obj.visibility == Visibility.restricted:
        title = obj.case_type.name  # TODO(mvilanova): fix

    # case_type_plugin_metadata = case_type_service.get_by_name_or_raise(
    #     db_session=db_session,
    #     project_id=case.project.id,
    #     case_type_in=case.case_type,
    # ).get_meta(plugin.plugin.slug)

    ticket = plugin.instance.create(
        obj.id,
        title,
        # TODO(mvilanova): fix
        # obj.case_type.name,
        # obj.case_priority.name,
        # obj.commander.individual.email,
        # obj.reporter.individual.email,
        # case_type_plugin_metadata,
        db_session=db_session,
    )
    ticket.update({"resource_type": plugin.plugin.slug})

    # event_service.log(
    #     db_session=db_session,
    #     source=plugin.plugin.title,
    #     description="Ticket created",
    #     case_id=case.id,
    # )

    return ticket


def update_ticket(
    object_id: int,
    db_session: SessionLocal,
):
    """Updates a ticket."""
    obj = database_service.get(db_session=db_session, object_id=object_id)

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=obj.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("External ticket not updated. No ticket plugin enabled.")
        return

    title = obj.title
    description = obj.description
    if obj.visibility == Visibility.restricted:
        title = description = obj.case_type.name

    # case_type_plugin_metadata = case_type_service.get_by_name_or_raise(
    #     db_session=db_session,
    #     project_id=case.project.id,
    #     case_type_in=case.case_type,
    # ).get_meta(plugin.plugin.slug)

    plugin.instance.update(
        obj.ticket.resource_id,
        title,
        description,
        # obj.case_type.name,
        # obj.case_priority.name,
        # obj.status.lower(),
        # case_type_plugin_metadata=case_type_plugin_metadata,
    )

    # event_service.log(
    #     db_session=db_session,
    #     source=plugin.plugin.title,
    #     description=f"Ticket updated. Status: {case.status}",
    #     case_id=case.id,
    # )
