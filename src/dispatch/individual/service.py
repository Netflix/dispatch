from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from dispatch.database.core import SessionLocal

from dispatch.incident.models import Incident
from dispatch.project import service as project_service
from dispatch.search_filter import service as search_filter_service
from dispatch.plugin import service as plugin_service

from .models import IndividualContact, IndividualContactCreate, IndividualContactUpdate


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


def get_by_email(*, db_session, email: str) -> Optional[IndividualContact]:
    """Returns an individual given an individual email address."""
    return (
        db_session.query(IndividualContact).filter(IndividualContact.email == email).one_or_none()
    )


def get_all(*, db_session) -> List[Optional[IndividualContact]]:
    """Returns all individuals."""
    return db_session.query(IndividualContact)


def get_or_create(
    *, db_session, email: str, incident: Incident = None, **kwargs
) -> IndividualContact:
    """Gets or creates an individual."""
    contact = get_by_email(db_session=db_session, email=email)

    if not contact:
        contact_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="contact"
        )
        individual_info = {}

        if contact_plugin:
            individual_info = contact_plugin.instance.get(email, db_session=db_session)

        kwargs["email"] = individual_info.get("email", email)
        kwargs["name"] = individual_info.get("fullname", "Unknown")
        kwargs["weblink"] = individual_info.get("weblink", "Unknown")
        individual_contact_in = IndividualContactCreate(**kwargs, project=incident.project)
        contact = create(db_session=db_session, individual_contact_in=individual_contact_in)

    return contact


def create(*, db_session, individual_contact_in: IndividualContactCreate) -> IndividualContact:
    """Creates an individual."""
    project = project_service.get_by_name(
        db_session=db_session, name=individual_contact_in.project.name
    )

    filters = [
        search_filter_service.get(db_session=db_session, search_filter_id=f.id)
        for f in individual_contact_in.filters
    ]

    contact = IndividualContact(
        **individual_contact_in.dict(
            exclude={"terms", "incident_priorities", "incident_types", "project"}
        ),
        filters=filters,
        project=project,
    )
    db_session.add(contact)
    db_session.commit()
    return contact


def update(
    *,
    db_session,
    individual_contact: IndividualContact,
    individual_contact_in: IndividualContactUpdate,
) -> IndividualContact:
    individual_contact_data = jsonable_encoder(individual_contact_in)

    project = project_service.get_by_name(
        db_session=db_session, name=individual_contact_in.project.name
    )

    filters = [
        search_filter_service.get(db_session=db_session, search_filter_id=f.id)
        for f in individual_contact_in.filters
    ]

    update_data = individual_contact_in.dict(skip_defaults=True, exclude={"filters"})

    for field in individual_contact_data:
        if field in update_data:
            setattr(individual_contact, field, update_data[field])

    individual_contact.filters = filters
    individual_contact.project = project
    db_session.add(individual_contact)
    db_session.commit()
    return individual_contact


def delete(*, db_session, individual_contact_id: int):
    individual = (
        db_session.query(IndividualContact)
        .filter(IndividualContact.id == individual_contact_id)
        .first()
    )
    individual.terms = []
    db_session.delete(individual)
    db_session.commit()
