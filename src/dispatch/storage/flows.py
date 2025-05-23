import logging

from sqlalchemy.orm import Session

from dispatch.case.models import Case
from dispatch.database.core import get_table_name_by_class_instance
from dispatch.event import service as event_service
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.tag_type import service as tag_type_service

from .enums import StorageAction
from .models import Storage, StorageCreate
from .service import create

log = logging.getLogger(__name__)

Subject = Case | Incident


def create_storage(subject: Subject, storage_members: list[str], db_session: Session):
    """Creates a storage."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="storage"
    )
    if not plugin:
        log.warning("Storage not created. No storage plugin enabled.")
        return

    external_storage_root_id = None

    # if project is set to use the tag external_id for the root folder
    storage_tag_type = tag_type_service.get_storage_tag_type_for_project(
        db_session=db_session,
        project_id=subject.project.id,
    )

    if storage_tag_type:
        # find if the subject has a tag of the specified type
        tag = next((tag for tag in subject.tags if tag.tag_type.id == storage_tag_type.id), None)
        if tag:
            external_storage_root_id = tag.external_id

    if external_storage_root_id is None:
        # we create the external storage based on the root in the configuration of the plugin
        external_storage_root_id = plugin.configuration.root_id

    storage_name = subject.title if subject.project.storage_use_title else subject.name

    try:
        external_storage = plugin.instance.create_file(
            parent_id=external_storage_root_id, name=storage_name, participants=storage_members
        )
    except Exception as e:
        log.exception(e)
        return

    if not external_storage:
        log.error(f"Storage not created. Plugin {plugin.plugin.slug} encountered an error.")
        return

    # we create folders to store logs and screengrabs
    folder_one_name = (
        subject.project.storage_folder_one if subject.project.storage_folder_one else "Logs"
    )
    folder_one = plugin.instance.create_file(parent_id=external_storage["id"], name=folder_one_name)

    folder_two_name = (
        subject.project.storage_folder_two if subject.project.storage_folder_two else "Screengrabs"
    )
    plugin.instance.create_file(parent_id=external_storage["id"], name=folder_two_name)

    if subject.project.storage_use_folder_one_as_primary:
        external_storage = folder_one

    # we create the internal storage
    storage_in = StorageCreate(
        resource_id=external_storage["id"],
        resource_type=plugin.plugin.slug,
        weblink=external_storage["weblink"],
    )

    storage = create(db_session=db_session, storage_in=storage_in)
    subject.storage = storage
    db_session.add(subject)
    db_session.commit()

    subject_type = get_table_name_by_class_instance(subject)
    if subject_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Case storage created",
            case_id=subject.id,
        )
    if subject_type == "incident":
        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Incident storage created",
            incident_id=subject.id,
        )

    return storage


def update_storage(
    subject: Subject,
    storage_action: StorageAction,
    storage_members: list[str],
    db_session: Session,
):
    """Updates an existing storage."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="storage"
    )
    if not plugin:
        log.warning("Storage not updated. No storage plugin enabled.")
        return

    # we add the member(s) to the storage folder
    if storage_action == StorageAction.add_members:
        try:
            plugin.instance.add_participant(
                team_drive_or_file_id=subject.storage.resource_id, participants=storage_members
            )
        except Exception as e:
            log.exception(e)
            return

    # we remove the member(s) from the storage folder
    if storage_action == StorageAction.remove_members:
        try:
            plugin.instance.remove_participant(
                team_drive_or_file_id=subject.storage.resource_id, participants=storage_members
            )
        except Exception as e:
            log.exception(e)
            return

    subject_type = get_table_name_by_class_instance(subject)
    if subject_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Case storage updated",
            case_id=subject.id,
        )
    if subject_type == "incident":
        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Incident storage updated",
            incident_id=subject.id,
        )


def delete_storage(storage: Storage, project_id: int, db_session: Session):
    """Deletes an existing storage."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="storage"
    )
    if plugin:
        try:
            plugin.instance.delete_file(file_id=storage.resource_id)
        except Exception as e:
            log.exception(e)
    else:
        log.warning("Storage not deleted. No storage plugin enabled.")
