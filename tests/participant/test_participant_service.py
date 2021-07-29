def test_get(session, participant):
    from dispatch.participant.service import get

    t_participant = get(db_session=session, participant_id=participant.id)
    assert t_participant.id == participant.id


def test_create(session, participant_role):
    from dispatch.participant.service import create
    from dispatch.participant.models import ParticipantCreate

    participant_in = ParticipantCreate(participant_role=[participant_role])
    participant = create(db_session=session, participant_in=participant_in)
    assert participant


def test_update(session, participant):
    from dispatch.participant.service import update
    from dispatch.participant.models import ParticipantUpdate

    location = "Updated location"

    participant_in = ParticipantUpdate(location=location)
    participant = update(db_session=session, participant=participant, participant_in=participant_in)
    assert participant.location == location


def test_delete(session, participant):
    from dispatch.participant.service import delete, get

    delete(db_session=session, participant_id=participant.id)
    assert not get(db_session=session, participant_id=participant.id)
