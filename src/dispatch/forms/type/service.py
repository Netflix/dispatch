import logging
from typing import Optional

from sqlalchemy.orm import Session

from .models import FormsType, FormsTypeCreate, FormsTypeUpdate
from dispatch.individual import service as individual_service
from dispatch.project import service as project_service
from dispatch.service import service as service_service
from dispatch.plugin import service as plugin_service
from dispatch.forms.models import Forms
from dispatch.service.models import Service
from dispatch.incident.messaging import send_completed_form_email

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

    service_id = None
    if forms_type_in.service:
        service = service_service.get(
            db_session=db_session, service_id=forms_type_in.service.id
        )
        if service:
            service_id = service.id

    form_type = FormsType(
        **forms_type_in.dict(exclude={"creator", "project", "service"}),
        creator_id=individual.id,
        project_id=project.id,
        service_id=service_id,
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

    service = forms_type_in.service
    if service:
        forms_type.service_id = service.id
    else:
        forms_type.service_id = None

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


def send_email_to_service(
    *,
    form: Forms,
    service: Service,
    db_session: Session,
):
    """Notifies oncall about completed form"""
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=form.project.id, plugin_type="oncall"
    )
    if not oncall_plugin:
        log.debug("Unable to send email since oncall plugin is not active.")
    else:
        current_oncall = oncall_plugin.instance.get(service.external_id)
        if current_oncall:
            send_completed_form_email(current_oncall, form, db_session)
