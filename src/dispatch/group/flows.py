from typing import Any, List
import logging

from dispatch.database.core import SessionLocal
from dispatch.database.core import get_table_name_by_class_instance
from dispatch.event import service as event_service
from dispatch.plugin import service as plugin_service

from .enums import GroupType
from .models import GroupCreate
from .service import create, delete


log = logging.getLogger(__name__)


def create_group(
    obj: Any, group_type: str, group_participants: List[str], db_session: SessionLocal
):
    """Creates a group."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=obj.project.id, plugin_type="participant-group"
    )
    if not plugin:
        log.warning("Group not created. No group plugin enabled.")
        return

    # we create the external group
    try:
        external_group = plugin.instance.create(name=obj.name, participants=group_participants)
    except Exception as e:
        log.exception(e)
        return

    if not external_group:
        log.error("Group not created. Plugin {plugin.plugin.slug} encountered an error.")
        return

    external_group.update(
        {
            "resource_type": f"{plugin.plugin.slug}-{group_type}-group",
            "resource_id": external_group["id"],
        }
    )

    # we create the internal group
    group_in = GroupCreate(
        name=external_group["name"],
        email=external_group["email"],
        resource_type=external_group["resource_type"],
        resource_id=external_group["resource_id"],
        weblink=external_group["weblink"],
    )
    group = create(db_session=db_session, group_in=group_in)
    obj.groups.append(group)

    if group_type == GroupType.tactical:
        obj.tactical_group_id = group.id
    else:
        obj.notifications_group_id = group.id

    db_session.add(obj)
    db_session.commit()

    obj_type = get_table_name_by_class_instance(obj)
    if obj_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Case group created",
            case_id=obj.id,
        )
    else:
        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Incident group created",
            incident_id=obj.id,
        )

    return group


def delete_group(obj: Any, db_session: SessionLocal):
    """Deletes an existing group."""
    # we delete the external group
    # TODO(mvilanova): implement deleting the external group
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=obj.project.id, plugin_type="participant-group"
    )
    if plugin:
        plugin.instance.delete()
    else:
        log.warning("Group not deleted. No group plugin enabled.")

    # we delete the internal ticket
    delete(db_session=db_session, group_id=obj.id)
