from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.project import service as project_service
from dispatch.search import service as search_service

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
    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in team_contact_in.filters
    ]

    team = TeamContact(
        **team_contact_in.dict(
            exclude={"terms", "incident_priorities", "incident_types", "project"}
        ),
        filters=filters,
        project=project,
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

    update_data = team_contact_in.dict(
        skip_defaults=True, exclude={"terms", "incident_priorities", "incident_types"}
    )

    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in team_contact_in.filters
    ]

    for field in team_contact_data:
        if field in update_data:
            setattr(team_contact, field, update_data[field])

    db_session.filters = filters
    db_session.add(team_contact)
    db_session.commit()
    return team_contact


def delete(*, db_session, team_contact_id: int):
    team = db_session.query(TeamContact).filter(TeamContact.id == team_contact_id).first()
    team.terms = []
    db_session.delete(team)
    db_session.commit()
