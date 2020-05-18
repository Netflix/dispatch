from typing import Optional

from fastapi.encoders import jsonable_encoder
from dispatch.config import ONCALL_PLUGIN_SLUG

from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.term import service as term_service

from .models import Service, ServiceCreate, ServiceUpdate


def get(*, db_session, service_id: int) -> Optional[Service]:
    return db_session.query(Service).filter(Service.id == service_id).first()


def get_by_external_id(*, db_session, external_id: str) -> Optional[Service]:
    return db_session.query(Service).filter(Service.external_id == external_id).first()


def get_all(*, db_session):
    return db_session.query(Service)


def get_all_by_status(*, db_session, is_active: bool):
    return db_session.query(Service).filter(Service.is_active.is_(is_active))


def create(*, db_session, service_in: ServiceCreate) -> Service:
    terms = [term_service.get_or_create(db_session=db_session, term_in=t) for t in service_in.terms]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in service_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in service_in.incident_types
    ]
    service = Service(
        **service_in.dict(exclude={"terms", "incident_priorities", "incident_types"}),
        incident_priorities=incident_priorities,
        incident_types=incident_types,
        terms=terms,
    )
    service.type = ONCALL_PLUGIN_SLUG
    db_session.add(service)
    db_session.commit()
    return service


def update(*, db_session, service: Service, service_in: ServiceUpdate) -> Service:
    service_data = jsonable_encoder(service)

    terms = [term_service.get_or_create(db_session=db_session, term_in=t) for t in service_in.terms]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in service_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in service_in.incident_types
    ]
    update_data = service_in.dict(
        skip_defaults=True, exclude={"terms", "incident_priorities", "incident_types"}
    )

    for field in service_data:
        if field in update_data:
            setattr(service, field, update_data[field])

    service.terms = terms
    service.incident_priorities = incident_priorities
    service.incident_types = incident_types
    db_session.add(service)
    db_session.commit()
    return service


def delete(*, db_session, service_id: int):
    service = db_session.query(Service).filter(Service.id == service_id).one()

    # TODO clear out other relationships
    # we clear out our associated items
    service.terms = []
    db_session.delete(service)
    db_session.commit()
    return service_id
