from typing import Optional

from fastapi.encoders import jsonable_encoder

from dispatch.document import service as document_service
from dispatch.service import service as service_service

from .models import IncidentType, IncidentTypeCreate, IncidentTypeUpdate


def get(*, db_session, incident_type_id: int) -> Optional[IncidentType]:
    return db_session.query(IncidentType).filter(IncidentType.id == incident_type_id).one()


def get_by_name(*, db_session, name: str) -> Optional[IncidentType]:
    return db_session.query(IncidentType).filter(IncidentType.name == name).one()


def get_by_slug(*, db_session, slug: str) -> Optional[IncidentType]:
    return db_session.query(IncidentType).filter(IncidentType.slug == slug).one()


def get_all(*, db_session):
    return db_session.query(IncidentType)


def create(*, db_session, incident_type_in: IncidentTypeCreate) -> IncidentType:
    if incident_type_in.template_document:
        template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.template_document.id
        )

    if incident_type_in.commander_service:
        commander_service = service_service.get(
            db_session=db_session, service_id=incident_type_in.commander_service.id
        )

    incident_type = IncidentType(
        **incident_type_in.dict(exclude={"commander_service", "template_document"},),
        commander_service=commander_service,
        template_document=template_document,
    )
    db_session.add(incident_type)
    db_session.commit()
    return incident_type


def update(
    *, db_session, incident_type: IncidentType, incident_type_in: IncidentTypeUpdate
) -> IncidentType:

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

    incident_type_data = jsonable_encoder(incident_type)

    update_data = incident_type_in.dict(
        skip_defaults=True, exclude={"commander_service", "template_document"}
    )

    for field in incident_type_data:
        if field in update_data:
            setattr(incident_type, field, update_data[field])

    db_session.add(incident_type)
    db_session.commit()
    return incident_type
