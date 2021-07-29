def test_get(session, participant_role):
    from dispatch.participant_role.service import get

    t_participant_role = get(db_session=session, participant_role_id=participant_role.id)
    assert t_participant_role.id == participant_role.id


def test_create(session, participant_role):
    from dispatch.participant_role.service import create
    from dispatch.participant_role.models import ParticipantRoleCreate, ParticipantRoleType

    role = ParticipantRoleType.incident_commander

    participant_role_in = ParticipantRoleCreate(role=role)
    participant_role = create(db_session=session, participant_role_in=participant_role_in)
    assert participant_role.role == role


def test_update(session, participant_role):
    from dispatch.participant_role.service import update
    from dispatch.participant_role.models import ParticipantRoleUpdate

    role = "Participant"

    participant_role_in = ParticipantRoleUpdate(role=role)
    participant_role = update(
        db_session=session,
        participant_role=participant_role,
        participant_role_in=participant_role_in,
    )
    assert participant_role.role == role


def test_delete(session, participant_role):
    from dispatch.participant_role.service import delete, get

    delete(db_session=session, participant_role_id=participant_role.id)
    assert not get(db_session=session, participant_role_id=participant_role.id)
