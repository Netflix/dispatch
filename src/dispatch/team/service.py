from typing import List, Optional

from dispatch.project import service as project_service
from dispatch.project.models import Project
from dispatch.search_filter import service as search_filter_service

from .models import TeamContact, TeamContactCreate, TeamContactUpdate


def get(*, db_session, team_contact_id: int) -> Optional[TeamContact]:
    return db_session.query(TeamContact).filter(TeamContact.id == team_contact_id).first()


def get_by_email(*, db_session, email: str, project_id: int) -> Optional[TeamContact]:
    return (
        db_session.query(TeamContact)
        .filter(TeamContact.email == email)
        .filter(TeamContact.project_id == project_id)
        .first()
    )


def get_all(*, db_session) -> List[Optional[TeamContact]]:
    return db_session.query(TeamContact)


def get_or_create(*, db_session, email: str, project: Project, **kwargs) -> TeamContact:
    contact = get_by_email(db_session=db_session, email=email, project_id=project.id)

    if not contact:
        team_contact = TeamContactCreate(email=email, project=project, **kwargs)
        contact = create(db_session=db_session, team_contact_in=team_contact)

    return contact


def get_overdue_evergreen_teams(*, db_session, project_id: int) -> List[Optional[TeamContact]]:
    """Returns all teams that have not had a recent evergreen notification."""
    query = (
        db_session.query(TeamContact)
        .filter(TeamContact.project_id == project_id)
        .filter(TeamContact.evergreen == True)  # noqa
        .filter(TeamContact.overdue == True)  # noqa
    )
    return query.all()


def create(*, db_session, team_contact_in: TeamContactCreate) -> TeamContact:
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=team_contact_in.project
    )
    filters = [
        search_filter_service.get(db_session=db_session, search_filter_id=f.id)
        for f in team_contact_in.filters
    ]

    team = TeamContact(
        **team_contact_in.dict(exclude={"project", "filters"}),
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
    team_contact_data = team_contact.dict()
    update_data = team_contact_in.dict(skip_defaults=True, exclude={"filter"})

    for field in team_contact_data:
        if field in update_data:
            setattr(team_contact, field, update_data[field])

    if team_contact_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in team_contact_in.filters
        ]
        db_session.filters = filters

    db_session.commit()
    return team_contact


def delete(*, db_session, team_contact_id: int):
    team = db_session.query(TeamContact).filter(TeamContact.id == team_contact_id).first()
    team.terms = []
    db_session.delete(team)
    db_session.commit()
