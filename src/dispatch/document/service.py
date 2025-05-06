from typing import List, Optional
from pydantic.error_wrappers import ValidationError
from datetime import datetime

from dispatch.enums import DocumentResourceReferenceTypes, DocumentResourceTemplateTypes
from dispatch.project import service as project_service
from dispatch.search_filter import service as search_filter_service
from dispatch.tag import service as tag_service

from .models import Document, DocumentCreate, DocumentUpdate


def get(*, db_session, document_id: int) -> Optional[Document]:
    """Returns a document based on the given document id."""
    return db_session.query(Document).filter(Document.id == document_id).one_or_none()


def get_by_incident_id_and_resource_type(
    *, db_session, incident_id: int, project_id: int, resource_type: str
) -> Optional[Document]:
    """Returns a document based on the given incident and id and document resource type."""
    return (
        db_session.query(Document)
        .filter(Document.incident_id == incident_id)
        .filter(Document.project_id == project_id)
        .filter(Document.resource_type == resource_type)
        .one_or_none()
    )


def get_project_forms_export_template(*, db_session, project_id: int) -> Optional[Document]:
    """Fetches the project forms export template."""
    resource_type = DocumentResourceTemplateTypes.forms
    return (
        db_session.query(Document)
        .filter(Document.project_id == project_id)
        .filter(Document.resource_type == resource_type)
        .one_or_none()
    )


def get_incident_faq_document(*, db_session, project_id: int):
    """Fetches incident faq document."""
    return (
        db_session.query(Document).filter(
            Document.resource_type == DocumentResourceReferenceTypes.faq,
            Document.project_id == project_id,
        )
    ).one_or_none()


def get_conversation_reference_document(*, db_session, project_id: int):
    """Fetches conversation reference document."""
    return (
        db_session.query(Document).filter(
            Document.resource_type == DocumentResourceReferenceTypes.conversation,
            Document.project_id == project_id,
        )
    ).one_or_none()


def get_overdue_evergreen_documents(*, db_session, project_id: int) -> List[Optional[Document]]:
    """Returns all documents that have not had a recent evergreen notification."""
    query = (
        db_session.query(Document)
        .filter(Document.project_id == project_id)
        .filter(Document.evergreen == True)  # noqa
        .filter(Document.overdue == True)  # noqa
    )
    return query.all()


def get_all(*, db_session) -> List[Optional[Document]]:
    """Returns all documents."""
    return db_session.query(Document)


def create(*, db_session, document_in: DocumentCreate) -> Document:
    """Creates a new document."""
    # handle the special case of only allowing 1 FAQ / Forms Export document per-project
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=document_in.project
    )

    if document_in.resource_type == DocumentResourceReferenceTypes.faq:
        faq_doc = (
            db_session.query(Document)
            .filter(Document.resource_type == DocumentResourceReferenceTypes.faq)
            .filter(Document.project_id == project.id)
            .one_or_none()
        )
        if faq_doc:
            raise ValidationError([
                {
                    "msg": "FAQ document already defined for this project.",
                    "loc": "document",
                }
            ])

    if document_in.resource_type == DocumentResourceTemplateTypes.forms:
        forms_doc = (
            db_session.query(Document)
            .filter(Document.resource_type == DocumentResourceTemplateTypes.forms)
            .filter(Document.project_id == project.id)
            .one_or_none()
        )
        if forms_doc:
            raise ValidationError([
                {
                    "msg": "Forms export template document already defined for this project.",
                    "loc": "document",
                }
            ])

    filters = [
        search_filter_service.get(db_session=db_session, search_filter_id=f.id)
        for f in document_in.filters
    ]

    tags = []
    for t in document_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    # set the last reminder to now
    if document_in.evergreen:
        document_in.evergreen_last_reminder_at = datetime.utcnow()

    document = Document(
        **document_in.dict(exclude={"project", "filters", "tags"}),
        filters=filters,
        project=project,
        tags=tags,
    )

    db_session.add(document)
    db_session.commit()
    return document


def get_or_create(*, db_session, document_in) -> Document:
    """Gets a document by it's resource_id or creates a new document."""
    if hasattr(document_in, "resource_id"):
        q = db_session.query(Document).filter(Document.resource_id == document_in.resource_id)
    else:
        q = db_session.query(Document).filter_by(**document_in.dict())

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, document_in=document_in)


def update(*, db_session, document: Document, document_in: DocumentUpdate) -> Document:
    """Updates a document."""
    document_data = document.dict()

    # we reset the last evergreeen reminder to now
    if document_in.evergreen:
        if not document.evergreen:
            document_in.evergreen_last_reminder_at = datetime.utcnow()

    update_data = document_in.dict(skip_defaults=True, exclude={"filters", "tags"})

    tags = []
    for t in document_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    for field in document_data:
        if field in update_data:
            setattr(document, field, update_data[field])

    if document_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in document_in.filters
        ]
        document.filters = filters

    document.tags = tags

    db_session.commit()
    return document


def delete(*, db_session, document_id: int):
    """Deletes a document."""
    db_session.query(Document).filter(Document.id == document_id).delete()
    db_session.commit()
