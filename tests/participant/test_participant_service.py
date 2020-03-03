import pytest


def test_get(session, participant):
    from dispatch.participant.service import get

    t_participant = get(db_session=session, participant_id=participant.id)
    assert t_participant.id == participant.id


def test_get_by_individual_contact_id(session, incident, participant, individual_contact):
    from dispatch.participant.service import get_by_individual_contact_id

    incident.participants.append(participant)
    individual_contact.participant.append(participant)

    t_participant = get_by_individual_contact_id(
        db_session=session, individual_contact_id=individual_contact.id
    )
    assert t_participant.individual_contact_id == individual_contact.id


def test_get_by_incident_id_and_role(session, incident, participant, participant_role):
    from dispatch.participant.service import get_by_incident_id_and_role

    participant.participant_role.append(participant_role)
    incident.participants.append(participant)

    t_participant = get_by_incident_id_and_role(
        db_session=session, incident_id=incident.id, role=participant_role.role
    )
    assert t_participant.incident_id == incident.id
    assert t_participant.participant_role[0].role == participant_role.role


def test_get_by_incident_id_and_email(session, incident, participant, individual_contact):
    from dispatch.participant.service import get_by_incident_id_and_email

    individual_contact.participant.append(participant)
    incident.participants.append(participant)

    t_participant = get_by_incident_id_and_email(
        db_session=session, incident_id=incident.id, email=individual_contact.email
    )
    assert t_participant.incident_id == incident.id
    assert t_participant.individual.email == individual_contact.email


def test_get_all(session, participants):
    from dispatch.participant.service import get_all

    t_participants = get_all(db_session=session).all()
    assert len(t_participants) > 1


def test_get_all_by_incident_id(session, incident, participants):
    from dispatch.participant.service import get_all_by_incident_id

    for participant in participants:
        incident.participants.append(participant)

    t_participants = get_all_by_incident_id(db_session=session, incident_id=incident.id).all()
    assert len(t_participants) > 1


def test_get_or_create(session, incident, individual_contact, participant_role):
    from dispatch.participant.service import create
    from dispatch.participant.models import Participant, ParticipantCreate

    participant = (
        session.query(Participant)
        .filter(Participant.incident_id == incident.id)
        .filter(Participant.individual_contact_id == individual_contact.id)
        .one_or_none()
    )

    if not participant:
        participant_in = ParticipantCreate(participant_role=[participant_role])
        participant = create(db_session=session, participant_in=participant_in)

    assert participant


def test_create(session, participant_role):
    from dispatch.participant.service import create
    from dispatch.participant.models import ParticipantCreate

    participant_in = ParticipantCreate(participant_role=[participant_role])
    participant = create(db_session=session, participant_in=participant_in)
    assert participant


def test_delete(session, participant):
    from dispatch.participant.service import delete, get

    delete(db_session=session, participant_id=participant.id)
    assert not get(db_session=session, participant_id=participant.id)
