import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import EmailTemplates, EmailTemplatesUpdate, EmailTemplatesCreate
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def get(*, email_template_id: int, db_session: Session) -> Optional[EmailTemplates]:
    """Gets an email template by its id."""
    return (
        db_session.query(EmailTemplates)
        .filter(EmailTemplates.id == email_template_id)
        .one_or_none()
    )


def get_by_type(*, email_template_type: str, project_id: int, db_session: Session) -> Optional[EmailTemplates]:
    """Gets an email template by its type."""
    return (
        db_session.query(EmailTemplates)
        .filter(EmailTemplates.project_id == project_id)
        .filter(EmailTemplates.email_template_type == email_template_type)
        .filter(EmailTemplates.enabled == True)  # noqa
        .first()
    )


def get_all(*, db_session: Session) -> List[Optional[EmailTemplates]]:
    """Gets all email templates."""
    return db_session.query(EmailTemplates)


def create(*, email_template_in: EmailTemplatesCreate, db_session: Session) -> EmailTemplates:
    """Creates email template data."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=email_template_in.project
    )

    email_template = EmailTemplates(
        **email_template_in.dict(exclude={"project"}), project=project
    )

    db_session.add(email_template)
    db_session.commit()
    return email_template


def update(
    *,
    email_template: EmailTemplates,
    email_template_in: EmailTemplatesUpdate,
    db_session: Session,
) -> EmailTemplates:
    """Updates an email template."""
    new_template = email_template.dict()
    update_data = email_template_in.dict(skip_defaults=True)

    for field in new_template:
        if field in update_data:
            setattr(email_template, field, update_data[field])

    db_session.commit()
    return email_template


def delete(*, db_session, email_template_id: int):
    """Deletes an email template."""
    email_template = (
        db_session.query(EmailTemplates)
        .filter(EmailTemplates.id == email_template_id)
        .one_or_none()
    )
    db_session.delete(email_template)
    db_session.commit()
