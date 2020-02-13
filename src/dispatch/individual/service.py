from typing import Optional

from fastapi.encoders import jsonable_encoder

from dispatch.config import INCIDENT_PLUGIN_CONTACT_SLUG
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.plugins.base import plugins
from dispatch.term import service as term_service

from .models import IndividualContact, IndividualContactCreate, IndividualContactUpdate


def resolve_user_by_email(email):
    """Resolves a user's details given their email."""
    p = plugins.get(INCIDENT_PLUGIN_CONTACT_SLUG)
    return p.get(email)


def get(*, db_session, individual_contact_id: int) -> Optional[IndividualContact]:
    return (
        db_session.query(IndividualContact)
        .filter(IndividualContact.id == individual_contact_id)
        .first()
    )


def get_by_email(*, db_session, email: str) -> Optional[IndividualContact]:
    return (
        db_session.query(IndividualContact).filter(IndividualContact.email == email).one_or_none()
    )


def get_all(*, db_session):
    return db_session.query(IndividualContact)


def get_or_create(*, db_session, email: str, **kwargs) -> IndividualContact:
    contact = get_by_email(db_session=db_session, email=email)

    if not contact:
        contact_plugin = plugins.get(INCIDENT_PLUGIN_CONTACT_SLUG)
        individual_info = contact_plugin.get(email)
        kwargs["email"] = individual_info["email"]
        kwargs["name"] = individual_info["fullname"]
        kwargs["weblink"] = individual_info["weblink"]
        individual_contact = IndividualContactCreate(**kwargs)
        contact = create(db_session=db_session, individual_contact_in=individual_contact)

    return contact


def create(*, db_session, individual_contact_in: IndividualContactCreate) -> IndividualContact:
    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t)
        for t in individual_contact_in.terms
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in individual_contact_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in individual_contact_in.incident_types
    ]
    contact = IndividualContact(
        **individual_contact_in.dict(exclude={"terms", "incident_priorities", "incident_types"}),
        terms=terms,
        incident_types=incident_types,
        incident_priorities=incident_priorities,
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

    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t)
        for t in individual_contact_in.terms
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in individual_contact_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in individual_contact_in.incident_types
    ]
    update_data = individual_contact_in.dict(
        skip_defaults=True, exclude={"terms", "incident_priorities", "incident_types"}
    )

    for field in individual_contact_data:
        if field in update_data:
            setattr(individual_contact_in, field, update_data[field])

    individual_contact.terms = terms
    individual_contact.incident_types = incident_types
    individual_contact.incident_priorities = incident_priorities
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
