from typing import Optional

from sqlalchemy.orm import Session

from .models import Forms, FormsCreate, FormsUpdate


def get(*, form_id: int, db_session: Session) -> Optional[Forms]:
    """Gets a from by its id."""
    return (
        db_session.query(Forms)
        .filter(Forms.id == form_id)
        .one_or_none()
    )


def get_all(*, db_session: Session):
    """Gets all forms."""
    return db_session.query(Forms)


def create(*, form_in: FormsCreate, db_session: Session) -> Forms:
    """Creates form data."""

    creator_id = (
        None if not form_in.creator else form_in.creator.id
    )

    project_id = None if not form_in.project else form_in.project.id

    form = Forms(
        **form_in.dict(exclude={"creator", "project"}),
        creator_id=creator_id,
        project_id=project_id,
    )
    db_session.add(form)
    db_session.commit()
    return form


def update(
    *,
    form: Forms,
    form_in: FormsUpdate,
    db_session: Session,
) -> Forms:
    """Updates a form."""
    form_data = form.dict()
    update_data = form_in.dict(skip_defaults=True)

    for field in form_data:
        if field in update_data:
            setattr(form, field, update_data[field])

    db_session.commit()
    return form


def delete(*, db_session, form_id: int):
    """Deletes a form."""
    form = (
        db_session.query(Forms)
        .filter(Forms.id == form_id)
        .one_or_none()
    )
    db_session.delete(form)
    db_session.commit()
