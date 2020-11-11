from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.expression import true

from dispatch.document import service as document_service
from dispatch.service import service as service_service

from .models import IncidentType, IncidentTypeCreate, IncidentTypeUpdate


def get(*, db_session, incident_type_id: int) -> Optional[IncidentType]:
    """Returns an incident type based on the given type id."""
    return db_session.query(IncidentType).filter(IncidentType.id == incident_type_id).one_or_none()


def get_default(*, db_session):
    """Returns the default incident type."""
    return (
        db_session.query(IncidentType).filter(IncidentType.default == true()).one_or_none()
    )  # noqa


def get_by_name(*, db_session, name: str) -> Optional[IncidentType]:
    """Returns an incident type based on the given type name."""
    return db_session.query(IncidentType).filter(IncidentType.name == name).one_or_none()


def get_by_slug(*, db_session, slug: str) -> Optional[IncidentType]:
    """Returns an incident type based on the given type slug."""
    return db_session.query(IncidentType).filter(IncidentType.slug == slug).one_or_none()


def get_all(*, db_session) -> List[Optional[IncidentType]]:
    """Returns all incident types."""
    return db_session.query(IncidentType)


def create(*, db_session, incident_type_in: IncidentTypeCreate) -> IncidentType:
    """Creates an incident type."""
    incident_type = IncidentType(
        **incident_type_in.dict(exclude={"commander_service", "template_document"}),
    )

    if incident_type_in.template_document:
        template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.template_document.id
        )
        incident_type.template_document = template_document

    if incident_type_in.commander_service:
        commander_service = service_service.get(
            db_session=db_session, service_id=incident_type_in.commander_service.id
        )
        incident_type.commander_service = commander_service

    if incident_type_in.liaison_service:
        liaison_service = service_service.get(
            db_session=db_session, service_id=incident_type_in.liaison_service.id
        )
        incident_type.liaison_service = liaison_service

    db_session.add(incident_type)
    db_session.commit()
    return incident_type


def update(
    *, db_session, incident_type: IncidentType, incident_type_in: IncidentTypeUpdate
) -> IncidentType:
    """Updates an incident type."""
    if incident_type_in.template_document:
        template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.template_document.id
        )
        incident_type.template_document = template_document

    if incident_type_in.commander_service:
        commander_service = service_service.get(
            db_session=db_session, service_id=incident_type_in.commander_service.id
        )
        incident_type.commander_service = commander_service

    if incident_type_in.liaison_service:
        liaison_service = service_service.get(
            db_session=db_session, service_id=incident_type_in.liaison_service.id
        )
        incident_type.liaison_service = liaison_service

    incident_type_data = jsonable_encoder(incident_type)

    update_data = incident_type_in.dict(
        skip_defaults=True, exclude={"commander_service", "liaison_service", "template_document"}
    )

    for field in incident_type_data:
        if field in update_data:
            setattr(incident_type, field, update_data[field])

    db_session.add(incident_type)
    db_session.commit()
    return incident_type


def delete(*, db_session, incident_type_id: int):
    """Deletes an incident type."""
    db_session.query(IncidentType).filter(IncidentType.id == incident_type_id).delete()
    db_session.commit()
