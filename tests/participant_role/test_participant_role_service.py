import pytest


def test_get(session, participant_role):
    from dispatch.participant_role.service import get

    t_participant_role = get(db_session=session, participant_role_id=participant_role.id)
    assert t_participant_role.id == participant_role.id


def test_get_all(session, participant_roles):
    from dispatch.participant_role.service import get_all

    t_participant_roles = get_all(db_session=session).all()
    assert len(t_participant_roles) > 1


@pytest.mark.skip()
def test_get_all_active_roles(session, participant, participant_roles):
    from dispatch.participant_role.service import get_all_active_roles

    for participant_role in participant_roles:
        participant.participant_role.append(participant_role)

    t_participant_roles = get_all_active_roles(
        db_session=session, participant_id=participant.id
    ).all()
    assert len(t_participant_roles) > 1


def test_add_role(session, participant, participant_role):
    from dispatch.participant_role.service import add_role

    t_participant_role = add_role(
        db_session=session, participant_id=participant.id, participant_role=participant_role.role
    )
    assert t_participant_role.participant_id == participant.id
    assert t_participant_role.role == participant_role.role


@pytest.mark.skip
def test_renounce_role(session, participant_role):
    from dispatch.participant_role.service import renounce_role

    t_participant_role = renounce_role(db_session=session, participant_role=participant_role)
    assert t_participant_role.renounce_at


def test_create(session, participant_role):
    from dispatch.participant_role.service import create
    from dispatch.participant_role.models import ParticipantRoleCreate, ParticipantRoleType

    role = ParticipantRoleType.incident_commander

    participant_role_in = ParticipantRoleCreate(role=role)
    participant_role = create(db_session=session, participant_role_in=participant_role_in)
    assert participant_role.role == role


def test_delete(session, participant_role):
    from dispatch.participant_role.service import delete, get

    delete(db_session=session, participant_role_id=participant_role.id)
    assert not get(db_session=session, participant_role_id=participant_role.id)
