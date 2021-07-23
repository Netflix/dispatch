import pytest


def test_get(session, team_contact):
    from dispatch.team.service import get

    t_team = get(db_session=session, team_contact_id=team_contact.id)
    assert t_team.id == team_contact.id


def test_get_all(session, team_contacts):
    from dispatch.team.service import get_all

    t_teams = get_all(db_session=session).all()
    assert len(t_teams) > 1


def test_create(session, project):
    from dispatch.team.service import create
    from dispatch.team.models import TeamContactCreate

    name = "name"
    notes = "notes"
    email = "team@example.com"

    team_contact_in = TeamContactCreate(
        name=name,
        notes=notes,
        email=email,
        project=project,
    )
    team = create(db_session=session, team_contact_in=team_contact_in)
    assert team


@pytest.mark.skip
def test_update(session, team_contact):
    from dispatch.team.service import update
    from dispatch.team.models import TeamContactUpdate

    name = "Updated name"

    team_contact_in = TeamContactUpdate(
        name=name,
    )
    team = update(
        db_session=session,
        team_contact=team_contact,
        team_contact_in=team_contact_in,
    )
    assert team.name == name


def test_delete(session, team_contact):
    from dispatch.team.service import delete, get

    delete(db_session=session, team_contact_id=team_contact.id)
    assert not get(db_session=session, team_contact_id=team_contact.id)
