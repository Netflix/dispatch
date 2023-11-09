from typing import Optional

from sqlalchemy.orm import Session

from .models import FormsType, FormTypeCreate, FormsTypeUpdate


def get(*, forms_type_id: int, db_session: Session) -> Optional[FormsType]:
    """Gets a from by its id."""
    return (
        db_session.query(FormsType)
        .filter(FormsType.id == forms_type_id)
        .one_or_none()
    )


def get_all(*, db_session: Session):
    """Gets all forms."""
    return db_session.query(FormsType)


def create(*, forms_type_in: FormTypeCreate, db_session: Session) -> FormsType:
    """Creates form data."""

    creator_id = (
        None if not forms_type_in.creator else forms_type_in.creator.id
    )

    project_id = None if not forms_type_in.project else forms_type_in.project.id

    form_type = FormsType(
        **forms_type_in.dict(exclude={"creator", "project"}),
        creator_id=creator_id,
        project_id=project_id,
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
    """Updates a form."""
    form_data = forms_type.dict()
    update_data = forms_type_in.dict(skip_defaults=True)

    for field in form_data:
        if field in update_data:
            setattr(forms_type, field, update_data[field])

    db_session.commit()
    return forms_type


def delete(*, db_session, forms_type_id: int):
    """Deletes a form."""
    form = (
        db_session.query(FormsType)
        .filter(FormsType.id == forms_type_id)
        .one_or_none()
    )
    db_session.delete(form)
    db_session.commit()
