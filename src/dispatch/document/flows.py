from typing import Any
import logging

from sqlalchemy.orm import Session

from dispatch.database.core import resolve_attr
from dispatch.database.core import get_table_name_by_class_instance
from dispatch.enums import DocumentResourceTypes
from dispatch.event import service as event_service
from dispatch.plugin import service as plugin_service

from .models import Document, DocumentCreate
from .service import create, delete
from .utils import deslug


log = logging.getLogger(__name__)


def create_document(
    subject: Any,
    document_type: str,
    document_template: Document,
    db_session: Session,
):
    """Creates a document."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="storage"
    )
    if not plugin:
        log.warning("Document not created. No storage plugin enabled.")
        return

    # we create the external document
    external_document_name = f"{subject.name} - {deslug(document_type)}"
    external_document_description = ""
    try:
        if document_template:
            external_document_description = document_template.description

            # we make a copy of the template in the storage folder
            external_document = plugin.instance.copy_file(
                folder_id=subject.storage.resource_id,
                file_id=document_template.resource_id,
                name=external_document_name,
            )
            # we move the document to the storage folder
            plugin.instance.move_file(subject.storage.resource_id, file_id=external_document["id"])
        else:
            # we create a blank document in the storage folder
            external_document = plugin.instance.create_file(
                parent_id=subject.storage.resource_id,
                name=external_document_name,
                file_type="document",
            )
    except Exception as e:
        log.exception(e)
        return

    if not external_document:
        log.error(
            f"{external_document_name} not created. Plugin {plugin.plugin.slug} encountered an error."  # noqa: E501
        )
        return

    external_document.update(
        {
            "name": external_document_name,
            "description": external_document_description,
            "resource_type": document_type,
            "resource_id": external_document["id"],
        }
    )

    # we create the internal document
    document_in = DocumentCreate(
        name=external_document["name"],
        description=external_document["description"],
        project={"name": subject.project.name},
        resource_id=external_document["resource_id"],
        resource_type=external_document["resource_type"],
        weblink=external_document["weblink"],
    )

    document = create(db_session=db_session, document_in=document_in)
    subject.documents.append(document)

    if document_type == DocumentResourceTypes.case:
        subject.case_document_id = document.id

    if document_type == DocumentResourceTypes.incident:
        subject.incident_document_id = document.id

    if document_type == DocumentResourceTypes.review:
        subject.incident_review_document_id = document.id

    db_session.add(subject)
    db_session.commit()

    subject_type = get_table_name_by_class_instance(subject)
    if subject_type == "case":
        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description=f"{deslug(document_type).lower().capitalize()} created",
            case_id=subject.id,
        )
    else:
        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description=f"{deslug(document_type).lower().capitalize()} created",
            incident_id=subject.id,
        )

    return document


def update_document(document: Document, project_id: int, db_session: Session):
    """Updates an existing document."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="document"
    )
    if not plugin:
        log.warning("Document not updated. No document plugin enabled.")
        return

    document_kwargs = {}
    if document.resource_type == DocumentResourceTypes.case:
        document_kwargs = {
            "case_description": document.case.description,
            "case_name": document.case.name,
            "case_owner": document.case.assignee.individual.email,
            "case_priority": document.case.case_priority.name,
            "case_resolution": document.case.resolution,
            "case_severity": document.case.case_severity.name,
            "case_status": document.case.status,
            "case_storage_weblink": resolve_attr(document.case, "storage.weblink"),
            "case_title": document.case.title,
            "case_type": document.case.case_type.name,
        }

    if (
        document.resource_type == DocumentResourceTypes.incident
        or document.resource_type == DocumentResourceTypes.review
    ):
        document_kwargs = {
            "commander_fullname": document.incident.commander.individual.name,
            "conference_challenge": resolve_attr(document.incident, "conference.challenge"),
            "conference_weblink": resolve_attr(document.incident, "conference.weblink"),
            "conversation_weblink": resolve_attr(document.incident, "conversation.weblink"),
            "description": document.incident.description,
            "document_weblink": resolve_attr(document.incident, "incident_document.weblink"),
            "name": document.incident.name,
            "priority": document.incident.incident_priority.name,
            "reported_at": document.incident.reported_at.strftime("%m/%d/%Y %H:%M:%S"),
            "resolution": document.incident.resolution,
            "severity": document.incident.incident_severity.name,
            "status": document.incident.status,
            "storage_weblink": resolve_attr(document.incident, "storage.weblink"),
            "ticket_weblink": resolve_attr(document.incident, "ticket.weblink"),
            "title": document.incident.title,
            "type": document.incident.incident_type.name,
        }

    if document.resource_type == DocumentResourceTypes.review:
        document_kwargs["stable_at"] = document.incident.stable_at.strftime("%m/%d/%Y %H:%M:%S")

    plugin.instance.update(document.resource_id, **document_kwargs)

    if document.resource_type == DocumentResourceTypes.case:
        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description=f"{deslug(DocumentResourceTypes.case).lower().capitalize()} updated",
            case_id=document.case.id,
        )

    if document.resource_type == DocumentResourceTypes.incident:
        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description=f"{deslug(DocumentResourceTypes.incident).lower().capitalize()} updated",
            incident_id=document.incident.id,
        )


def delete_document(document: Document, project_id: int, db_session: Session):
    """Deletes an existing document."""
    # we delete the external document
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="storage"
    )
    if plugin:
        # TODO(mvilanova): implement deleting the external document
        # plugin.instance.delete()
        pass
    else:
        log.warning("Document not deleted. No storage plugin enabled.")

    # we delete the internal document
    delete(db_session=db_session, document_id=document.id)


def open_document_access(document: Document, db_session: Session):
    """Opens access to document by adding domain wide permission, handling both incidents and cases."""
    subject_type = None
    project_id = None
    subject = None

    if document.incident:
        subject_type = "incident"
        subject = document.incident
        project_id = document.incident.project.id
    elif document.case:
        subject_type = "case"
        subject = document.case
        project_id = document.case.project.id

    if not subject_type:
        log.warning(f"Document {document.id} is neither linked to an incident nor a case.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="storage"
    )
    if not plugin:
        log.warning("Access to document not opened. No storage plugin enabled.")
        return

    try:
        plugin.instance.open(document.resource_id)
    except Exception as e:
        event_service.log_subject_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Opening {deslug(document.resource_type).lower()} to anyone in the domain failed. Reason: {e}",
            subject=subject,
        )
        log.exception(e)
    else:
        event_service.log_subject_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{deslug(document.resource_type).lower().capitalize()} opened to anyone in the domain",
            subject=subject,
        )


def mark_document_as_readonly(document: Document, db_session: Session):
    """Marks document as readonly, handling both incidents and cases."""
    subject_type = None
    project_id = None
    subject = None

    if document.incident:
        subject_type = "incident"
        subject = document.incident
        project_id = document.incident.project.id
    elif document.case:
        subject_type = "case"
        subject = document.case
        project_id = document.case.project.id

    if not subject_type:
        log.warning(f"Document {document.id} is neither linked to an incident nor a case.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="storage"
    )
    if not plugin:
        log.warning("Document not marked as readonly. No storage plugin enabled.")
        return

    try:
        plugin.instance.mark_readonly(document.resource_id)
    except Exception as e:
        event_service.log_subject_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Marking {deslug(document.resource_type).lower()} as readonly failed. Reason: {e}",
            subject=subject,
        )
        log.exception(e)
    else:
        event_service.log_subject_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"{deslug(document.resource_type).lower().capitalize()} marked as readonly",
            subject=subject,
        )
