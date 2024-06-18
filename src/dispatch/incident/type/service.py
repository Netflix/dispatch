from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.incident_cost import service as incident_cost_service
from dispatch.incident import service as incident_service
from dispatch.cost_model import service as cost_model_service
from dispatch.document import service as document_service
from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.service import service as service_service

from .models import IncidentType, IncidentTypeCreate, IncidentTypeRead, IncidentTypeUpdate


def get(*, db_session, incident_type_id: int) -> Optional[IncidentType]:
    """Returns an incident type based on the given type id."""
    return db_session.query(IncidentType).filter(IncidentType.id == incident_type_id).one_or_none()


def get_default(*, db_session, project_id: int):
    """Returns the default incident type."""
    return (
        db_session.query(IncidentType)
        .filter(IncidentType.default == true())
        .filter(IncidentType.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> IncidentType:
    """Returns the default incident_type or raise a ValidationError if one doesn't exist."""
    incident_type = get_default(db_session=db_session, project_id=project_id)

    if not incident_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default incident type defined."),
                    loc="incident_type",
                )
            ],
            model=IncidentTypeRead,
        )
    return incident_type


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[IncidentType]:
    """Returns an incident type based on the given type name."""
    return (
        db_session.query(IncidentType)
        .filter(IncidentType.name == name)
        .filter(IncidentType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, incident_type_in=IncidentTypeRead
) -> IncidentType:
    """Returns the incident_type specified or raises ValidationError."""
    incident_type = get_by_name(
        db_session=db_session, project_id=project_id, name=incident_type_in.name
    )

    if not incident_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Incident type not found.", incident_type=incident_type_in.name
                    ),
                    loc="incident_type",
                )
            ],
            model=IncidentTypeRead,
        )

    return incident_type


def get_by_name_or_default(
    *, db_session, project_id: int, incident_type_in=IncidentTypeRead
) -> IncidentType:
    """Returns a incident_type based on a name or the default if not specified."""
    if incident_type_in:
        if incident_type_in.name:
            return get_by_name_or_raise(
                db_session=db_session, project_id=project_id, incident_type_in=incident_type_in
            )
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_by_slug(*, db_session, project_id: int, slug: str) -> Optional[IncidentType]:
    """Returns an incident type based on the given type slug."""
    return (
        db_session.query(IncidentType)
        .filter(IncidentType.slug == slug)
        .filter(IncidentType.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int = None) -> List[Optional[IncidentType]]:
    """Returns all incident types."""
    if project_id:
        return db_session.query(IncidentType).filter(IncidentType.project_id == project_id)
    return db_session.query(IncidentType)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[IncidentType]]:
    """Returns all enabled incident types."""
    if project_id:
        return (
            db_session.query(IncidentType)
            .filter(IncidentType.project_id == project_id)
            .filter(IncidentType.enabled == true())
            .order_by(IncidentType.name)
        )
    return (
        db_session.query(IncidentType)
        .filter(IncidentType.enabled == true())
        .order_by(IncidentType.name)
    )


def create(*, db_session, incident_type_in: IncidentTypeCreate) -> IncidentType:
    """Creates an incident type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=incident_type_in.project
    )
    incident_type = IncidentType(
        **incident_type_in.dict(
            exclude={
                "incident_template_document",
                "executive_template_document",
                "tracking_template_document",
                "review_template_document",
                "cost_model",
                "project",
                "description_service",
            }
        ),
        project=project,
    )

    if incident_type_in.cost_model:
        cost_model = cost_model_service.get_cost_model_by_id(
            db_session=db_session, cost_model_id=incident_type_in.cost_model.id
        )
        incident_type.cost_model = cost_model

    if incident_type_in.incident_template_document:
        incident_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.incident_template_document.id
        )
        incident_type.incident_template_document = incident_template_document

    if incident_type_in.executive_template_document:
        executive_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.executive_template_document.id
        )
        incident_type.executive_template_document = executive_template_document

    if incident_type_in.review_template_document:
        review_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.review_template_document.id
        )
        incident_type.review_template_document = review_template_document

    if incident_type_in.tracking_template_document:
        tracking_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.tracking_template_document.id
        )
        incident_type.tracking_template_document = tracking_template_document

    if incident_type_in.description_service:
        service = service_service.get(
            db_session=db_session, service_id=incident_type_in.description_service.id
        )
        if service:
            incident_type.description_service_id = service.id

    db_session.add(incident_type)
    db_session.commit()
    return incident_type


def update(
    *, db_session, incident_type: IncidentType, incident_type_in: IncidentTypeUpdate
) -> IncidentType:
    """Updates an incident type.

    If the cost model is updated, we need to update the costs of all incidents associated with this incident type.
    """
    cost_model = None
    if incident_type_in.cost_model:
        cost_model = cost_model_service.get_cost_model_by_id(
            db_session=db_session, cost_model_id=incident_type_in.cost_model.id
        )
    should_update_incident_cost = incident_type.cost_model != cost_model
    incident_type.cost_model = cost_model

    # Calculate the cost of all non-closed incidents associated with this incident type
    incidents = incident_service.get_all_open_by_incident_type(
        db_session=db_session, incident_type_id=incident_type.id
    )
    for incident in incidents:
        incident_cost_service.calculate_incident_response_cost(
            incident_id=incident.id, db_session=db_session, incident_review=False
        )

    if incident_type_in.incident_template_document:
        incident_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.incident_template_document.id
        )
        incident_type.incident_template_document = incident_template_document

    if incident_type_in.executive_template_document:
        executive_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.executive_template_document.id
        )
        incident_type.executive_template_document = executive_template_document

    if incident_type_in.review_template_document:
        review_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.review_template_document.id
        )
        incident_type.review_template_document = review_template_document

    if incident_type_in.tracking_template_document:
        tracking_template_document = document_service.get(
            db_session=db_session, document_id=incident_type_in.tracking_template_document.id
        )
        incident_type.tracking_template_document = tracking_template_document

    if incident_type_in.description_service:
        service = service_service.get(
            db_session=db_session, service_id=incident_type_in.description_service.id
        )
        if service:
            incident_type.description_service_id = service.id

    incident_type_data = incident_type.dict()

    update_data = incident_type_in.dict(
        skip_defaults=True,
        exclude={
            "incident_template_document",
            "executive_template_document",
            "tracking_template_document",
            "review_template_document",
            "cost_model",
            "description_service",
        },
    )

    for field in incident_type_data:
        if field in update_data:
            setattr(incident_type, field, update_data[field])

    db_session.commit()

    if should_update_incident_cost:
        incident_cost_service.update_incident_response_cost_for_incident_type(
            db_session=db_session, incident_type=incident_type
        )

    return incident_type


def delete(*, db_session, incident_type_id: int):
    """Deletes an incident type."""
    db_session.query(IncidentType).filter(IncidentType.id == incident_type_id).delete()
    db_session.commit()
