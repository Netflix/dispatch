from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.project import service as project_service
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.term import service as term_service

from .models import TeamContact, TeamContactCreate, TeamContactUpdate


def get(*, db_session, team_contact_id: int) -> Optional[TeamContact]:
    return db_session.query(TeamContact).filter(TeamContact.id == team_contact_id).first()


def get_by_email(*, db_session, email: str) -> Optional[TeamContact]:
    return db_session.query(TeamContact).filter(TeamContact.email == email).first()


def get_all(*, db_session) -> List[Optional[TeamContact]]:
    return db_session.query(TeamContact)


def get_or_create(*, db_session, email: str, **kwargs) -> TeamContact:
    contact = get_by_email(db_session=db_session, email=email)

    if not contact:
        team_contact = TeamContactCreate(email=email, **kwargs)
        contact = create(db_session=db_session, team_contact_in=team_contact)

    return contact


def create(*, db_session, team_contact_in: TeamContactCreate) -> TeamContact:
    project = project_service.get_by_name(db_session=db_session, name=team_contact_in.project.name)
    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t) for t in team_contact_in.terms
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(
            db_session=db_session, project_id=project.id, name=n.name
        )
        for n in team_contact_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, project_id=project.id, name=n.name)
        for n in team_contact_in.incident_types
    ]

    team = TeamContact(
        **team_contact_in.dict(
            exclude={"terms", "incident_priorities", "incident_types", "project"}
        ),
        project=project,
        terms=terms,
        incident_types=incident_types,
        incident_priorities=incident_priorities,
    )
    db_session.add(team)
    db_session.commit()
    return team


def create_all(*, db_session, team_contacts_in: List[TeamContactCreate]) -> List[TeamContact]:
    contacts = [TeamContact(**t.dict()) for t in team_contacts_in]
    db_session.bulk_save_objects(contacts)
    db_session.commit()
    return contacts


def update(
    *, db_session, team_contact: TeamContact, team_contact_in: TeamContactUpdate
) -> TeamContact:
    team_contact_data = jsonable_encoder(team_contact)

    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t) for t in team_contact_in.terms
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(
            db_session=db_session, project_id=team_contact.project.id, name=n.name
        )
        for n in team_contact_in.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(
            db_session=db_session, project_id=team_contact.project.id, name=n.name
        )
        for n in team_contact_in.incident_types
    ]
    update_data = team_contact_in.dict(
        skip_defaults=True, exclude={"terms", "incident_priorities", "incident_types"}
    )

    for field in team_contact_data:
        if field in update_data:
            setattr(team_contact, field, update_data[field])

    team_contact.terms = terms
    team_contact.incident_priorities = incident_priorities
    team_contact.incident_types = incident_types
    db_session.add(team_contact)
    db_session.commit()
    return team_contact


def delete(*, db_session, team_contact_id: int):
    team = db_session.query(TeamContact).filter(TeamContact.id == team_contact_id).first()
    team.terms = []
    db_session.delete(team)
    db_session.commit()
