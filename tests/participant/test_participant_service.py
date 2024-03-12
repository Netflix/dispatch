def test_get(session, participant):
    from dispatch.participant.service import get

    t_participant = get(db_session=session, participant_id=participant.id)
    assert t_participant.id == participant.id


def test_get_or_preview__get(session, participant, incident):
    from dispatch.participant.service import get_or_preview

    participant.incident = incident
    t_participant = get_or_preview(
        db_session=session,
        subject=participant.incident,
        individual_id=participant.individual_contact_id,
        service_id=0,
        participant_roles=[],
    )

    assert t_participant
    assert t_participant.id == participant.id


def test_get_or_preview__preview(session, incident, individual_contact, participant_role):
    from dispatch.participant.service import get_or_preview

    participant = get_or_preview(
        db_session=session,
        subject=incident,
        individual_id=individual_contact.id,
        service_id=0,
        participant_roles=[participant_role],
    )

    assert participant
    assert not participant.id


def test_create_preview(session, participant_role):
    from dispatch.participant.service import create
    from dispatch.participant.models import ParticipantCreate

    participant_in = ParticipantCreate(participant_role=[participant_role])
    participant = create(db_session=session, participant_in=participant_in, preview=True)
    assert participant
    assert not participant.id


def test_create(session, participant_role):
    from dispatch.participant.service import create
    from dispatch.participant.models import ParticipantCreate

    participant_in = ParticipantCreate(participant_role=[participant_role])
    participant = create(db_session=session, participant_in=participant_in, preview=False)
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
