from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.database.core import SessionLocal
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service
from dispatch.search_filter import service as search_filter_service

from .models import (
    IndividualContact,
    IndividualContactCreate,
    IndividualContactRead,
    IndividualContactUpdate,
)


def resolve_user_by_email(email, db_session: SessionLocal):
    """Resolves a user's details given their email."""
    plugin = plugin_service.get_active_instance(db_session=db_session, plugin_type="contact")
    return plugin.instance.get(email)


def get(*, db_session, individual_contact_id: int) -> Optional[IndividualContact]:
    """Returns an individual given an individual id."""
    return (
        db_session.query(IndividualContact)
        .filter(IndividualContact.id == individual_contact_id)
        .one_or_none()
    )


def get_by_email_and_project(
    *, db_session, email: str, project_id: int
) -> Optional[IndividualContact]:
    """Returns an individual given an email address and project id."""
    return (
        db_session.query(IndividualContact)
        .filter(IndividualContact.email == email)
        .filter(IndividualContact.project_id == project_id)
        .one_or_none()
    )


def get_by_email_and_project_id_or_raise(
    *, db_session, project_id: int, individual_contact_in=IndividualContactRead
) -> IndividualContactRead:
    """Returns the individual specified or raises ValidationError."""
    individual_contact = get_by_email_and_project(
        db_session=db_session, project_id=project_id, email=individual_contact_in.email
    )

    if not individual_contact:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Indivdual not found.",
                        individual=individual_contact_in.email,
                    ),
                    loc="individual",
                )
            ],
            model=IndividualContactRead,
        )

    return individual_contact


def get_all(*, db_session) -> List[Optional[IndividualContact]]:
    """Returns all individuals."""
    return db_session.query(IndividualContact)


def get_or_create(
    *, db_session, email: str, incident: Incident = None, **kwargs
) -> IndividualContact:
    """Gets or creates an individual."""
    # we fetch the individual contact from the database
    individual_contact = get_by_email_and_project(
        db_session=db_session, email=email, project_id=incident.project.id
    )

    # we try to fetch the individual's contact information using the contact plugin
    contact_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="contact"
    )

    individual_info = {}
    if contact_plugin:
        individual_info = contact_plugin.instance.get(email, db_session=db_session)

    kwargs["email"] = individual_info.get("email", email)
    kwargs["name"] = individual_info.get("fullname", "Unknown")
    kwargs["weblink"] = individual_info.get("weblink", "")

    if not individual_contact:
        # we create a new contact
        individual_contact_in = IndividualContactCreate(**kwargs, project=incident.project)
        individual_contact = create(
            db_session=db_session, individual_contact_in=individual_contact_in
        )
    else:
        # we update the existing contact
        individual_contact_in = IndividualContactUpdate(**kwargs, project=incident.project)
        individual_contact = update(
            db_session=db_session,
            individual_contact=individual_contact,
            individual_contact_in=individual_contact_in,
        )

    return individual_contact


def create(*, db_session, individual_contact_in: IndividualContactCreate) -> IndividualContact:
    """Creates an individual."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=individual_contact_in.project
    )

    contact = IndividualContact(
        **individual_contact_in.dict(exclude={"project", "filters"}),
        project=project,
    )

    if individual_contact_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in individual_contact_in.filters
        ]
        contact.filters = filters

    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    individual_contact: IndividualContact,
    individual_contact_in: IndividualContactUpdate,
) -> IndividualContact:
    """Updates an individual."""
    individual_contact_data = individual_contact.dict()
    update_data = individual_contact_in.dict(skip_defaults=True, exclude={"filters"})

    for field in individual_contact_data:
        if field in update_data:
            setattr(individual_contact, field, update_data[field])

    if individual_contact_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in individual_contact_in.filters
        ]
        individual_contact.filters = filters

    db_session.commit()
    return individual_contact


def delete(*, db_session, individual_contact_id: int):
    """Deletes an individual."""
    individual = (
        db_session.query(IndividualContact)
        .filter(IndividualContact.id == individual_contact_id)
        .first()
    )
    individual.terms = []
    db_session.delete(individual)
    db_session.commit()
