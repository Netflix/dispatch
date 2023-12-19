import logging
from typing import Optional

from sqlalchemy.orm import Session

from .models import Forms, FormsUpdate
from dispatch.individual import service as individual_service

log = logging.getLogger(__name__)


def get(*, forms_id: int, db_session: Session) -> Optional[Forms]:
    """Gets a from by its id."""
    return (
        db_session.query(Forms)
        .filter(Forms.id == forms_id)
        .one_or_none()
    )


def get_all(*, db_session: Session):
    """Gets all forms."""
    return db_session.query(Forms)


def create(*, forms_in: dict, db_session: Session, creator) -> Forms:
    """Creates form data."""

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=creator.email, project_id=forms_in["project_id"]
    )

    form = Forms(
        **forms_in,
        creator_id=individual.id,
    )

    db_session.add(form)
    db_session.commit()
    return form


def update(
    *,
    forms: Forms,
    forms_in: FormsUpdate,
    db_session: Session,
) -> Forms:
    """Updates a form."""
    form_data = forms.dict()
    update_data = forms_in.dict(skip_defaults=True)

    for field in form_data:
        if field in update_data:
            setattr(forms, field, update_data[field])

    db_session.commit()
    return forms


def delete(*, db_session, forms_id: int):
    """Deletes a form."""
    form = (
        db_session.query(Forms)
        .filter(Forms.id == forms_id)
        .one_or_none()
    )
    db_session.delete(form)
    db_session.commit()
