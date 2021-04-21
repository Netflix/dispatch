from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.exceptions import InvalidConfiguration
from dispatch.project import service as project_service
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.plugin import service as plugin_service
from dispatch.term import service as term_service

from .models import Service, ServiceCreate, ServiceUpdate


def get(*, db_session, service_id: int) -> Optional[Service]:
    """Gets a service by id."""
    return db_session.query(Service).filter(Service.id == service_id).first()


def get_by_external_id(*, db_session, external_id: str) -> Optional[Service]:
    """Gets a service by external id (e.g. PagerDuty service id)."""
    return db_session.query(Service).filter(Service.external_id == external_id).first()


def get_all(*, db_session):
    """Gets all services."""
    return db_session.query(Service)


def get_all_by_status(*, db_session, is_active: bool):
    """Gets services by status."""
    return db_session.query(Service).filter(Service.is_active.is_(is_active))


def get_all_by_type_and_status(
    *, db_session, service_type: str, is_active: bool
) -> List[Optional[Service]]:
    """Gets a service by type and status."""
    return (
        db_session.query(Service)
        .filter(Service.type == service_type)
        .filter(Service.is_active.is_(is_active))
        .all()
    )


def create(*, db_session, service_in: ServiceCreate) -> Service:
    """Creates a new service."""
    project = project_service.get_by_name(db_session=db_session, name=service_in.project.name)
    terms = [term_service.get_or_create(db_session=db_session, term_in=t) for t in service_in.terms]
    incident_priorities = [
        incident_priority_service.get_by_name(
            db_session=db_session, project_id=project.id, name=n.name
        )
        for n in service_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, project_id=project.id, name=n.name)
        for n in service_in.incident_types
    ]
    service = Service(
        **service_in.dict(exclude={"terms", "incident_priorities", "incident_types", "project"}),
        incident_priorities=incident_priorities,
        incident_types=incident_types,
        terms=terms,
        project=project,
    )
    db_session.add(service)
    db_session.commit()
    return service


def update(*, db_session, service: Service, service_in: ServiceUpdate) -> Service:
    """Updates an existing service."""
    service_data = jsonable_encoder(service)

    terms = [term_service.get_or_create(db_session=db_session, term_in=t) for t in service_in.terms]
    incident_priorities = [
        incident_priority_service.get_by_name(
            db_session=db_session, project_id=service.project.id, name=n.name
        )
        for n in service_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(
            db_session=db_session, project_id=service.project.id, name=n.name
        )
        for n in service_in.incident_types
    ]
    update_data = service_in.dict(
        skip_defaults=True, exclude={"terms", "incident_priorities", "incident_types"}
    )

    if service_in.is_active:  # user wants to enable the service
        oncall_plugin_instance = plugin_service.get_active_instance_by_slug(
            db_session=db_session, slug=service_in.type, project_id=service.project.id
        )
        if not oncall_plugin_instance.enabled:
            raise InvalidConfiguration(
                f"Cannot enable service: {service.name}. Its associated plugin {oncall_plugin_instance.plugin.title} is not enabled."
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
    """Deletes a service."""
    service = db_session.query(Service).filter(Service.id == service_id).one()

    # TODO clear out other relationships
    # we clear out our associated items
    service.terms = []
    db_session.delete(service)
    db_session.commit()
    return service_id
