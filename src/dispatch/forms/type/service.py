import logging
from typing import Optional

from sqlalchemy.orm import Session

from .models import FormsType, FormsTypeCreate, FormsTypeUpdate
from dispatch.individual import service as individual_service
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def get(*, forms_type_id: int, db_session: Session) -> Optional[FormsType]:
    """Gets a from type by its id."""
    return (
        db_session.query(FormsType)
        .filter(FormsType.id == forms_type_id)
        .one_or_none()
    )


def get_all(*, db_session: Session):
    """Gets all form types."""
    return db_session.query(FormsType)


def create(*, db_session: Session, forms_type_in: FormsTypeCreate, creator) -> FormsType:
    """Creates form type."""

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=forms_type_in.project
    )

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=creator.email, project_id=project.id
    )

    form_type = FormsType(
        **forms_type_in.dict(exclude={"creator", "project"}),
        creator_id=individual.id,
        project_id=project.id,
    )
    db_session.add(form_type)
    db_session.commit()
    return form_type


def update(
    *,
    forms_type: FormsType,
    forms_type_in: FormsTypeUpdate,
    db_session: Session,
) -> FormsType:
    """Updates a form type."""
    form_data = forms_type.dict()
    update_data = forms_type_in.dict(skip_defaults=True)

    for field in form_data:
        if field in update_data:
            setattr(forms_type, field, update_data[field])

    db_session.commit()
    return forms_type


def delete(*, db_session, forms_type_id: int):
    """Deletes a form type."""
    form = (
        db_session.query(FormsType)
        .filter(FormsType.id == forms_type_id)
        .one_or_none()
    )
    db_session.delete(form)
    db_session.commit()
