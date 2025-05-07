import pytest
from dispatch.feedback.incident.enums import FeedbackRating
from dispatch.case.models import CaseReadMinimal
from dispatch.participant.models import ParticipantRead, ParticipantReadMinimal
from dispatch.project.models import ProjectRead
from dispatch.case.type.models import CaseTypeRead
from dispatch.case.severity.models import CaseSeverityRead
from dispatch.case.priority.models import CasePriorityRead


def test_get(session, feedback):
    from dispatch.feedback.incident.service import get

    t_feedback = get(db_session=session, feedback_id=feedback.id)
    assert t_feedback.id == feedback.id


def test_get_all(session, feedbacks):
    from dispatch.feedback.incident.service import get_all

    t_feedbacks = get_all(db_session=session).all()
    assert t_feedbacks


@pytest.mark.skip
def test_create(session, incident, incident_type, incident_priority):
    from dispatch.feedback.incident.service import create
    from dispatch.feedback.incident.models import FeedbackCreate

    # This test is skipped, but if enabled, it would need similar fixes
    # to ensure incident.case and incident.participant are fully populated ORM objects
    # before being used in CaseReadMinimal and ParticipantRead.

    incident.incident_type = incident_type
    incident.incident_priority = incident_priority
    rating = FeedbackRating.neither_satisfied_nor_dissatisfied
    rating = FeedbackRating.neither_satisfied_nor_dissatisfied
    feedback = "The incident commander did an excellent job"

    feedback_in = FeedbackCreate(
        rating=rating,
        feedback=feedback,
        incident=incident, # This would need to be IncidentRead.model_validate(incident)
        # case=... # Similar full population as in other tests
        # participant=... # Similar full population
    )
    feedback_obj = create(db_session=session, feedback_in=feedback_in)
    assert feedback_obj


def test_update(session, feedback, individual_contact, case): # Added case fixture
    from dispatch.feedback.incident.service import update
    from dispatch.feedback.incident.models import FeedbackUpdate
    from dispatch.participant.models import Participant # ORM model

    # Ensure feedback.case is populated for the test
    if not feedback.case:
        feedback.case = case  # Use the case fixture directly
        session.commit()

    # Ensure feedback.participant is populated
    if not feedback.participant:
        # Create a participant for the case if needed
        participant = Participant(
            individual=individual_contact,
            case_id=feedback.case.id
        )
        session.add(participant)
        session.commit()
        feedback.participant = participant
        session.commit()
    elif not feedback.participant.individual:
        feedback.participant.individual = individual_contact
        session.commit()

    # Ensure case has an assignee
    if not feedback.case.assignee:
        feedback.case.assignee = feedback.participant
        session.commit()

    # Verify everything is set up properly
    assert feedback.case is not None, "Feedback must have a case"
    assert feedback.participant is not None, "Feedback must have a participant"
    assert feedback.case.case_type is not None, "Case must have a type"
    assert feedback.case.case_severity is not None, "Case must have a severity"
    assert feedback.case.case_priority is not None, "Case must have a priority"
    assert feedback.case.project is not None, "Case must have a project"

    updated_rating = FeedbackRating.very_satisfied
    updated_feedback_text = "The incident commander did an excellent job after service update."

    feedback_in = FeedbackUpdate(
        rating=updated_rating,
        feedback=updated_feedback_text,
        case=CaseReadMinimal(
            id=feedback.case.id,
            name=feedback.case.name,
            title=feedback.case.title,
            description=feedback.case.description,
            resolution=feedback.case.resolution,
            resolution_reason=feedback.case.resolution_reason or "Resolved successfully",  # Add resolution_reason with default value
            status=feedback.case.status,
            visibility=feedback.case.visibility,
            closed_at=feedback.case.closed_at,
            reported_at=feedback.case.reported_at,
            dedicated_channel=feedback.case.dedicated_channel,
            case_type=CaseTypeRead.model_validate(feedback.case.case_type),
            case_severity=CaseSeverityRead.model_validate(feedback.case.case_severity),
            case_priority=CasePriorityRead.model_validate(feedback.case.case_priority),
            project=ProjectRead.model_validate(feedback.case.project),
            assignee=ParticipantReadMinimal.model_validate(feedback.case.assignee) if feedback.case.assignee else None,
            case_costs=[]
        ),
        participant=ParticipantRead.model_validate(feedback.participant),
    )
    updated_feedback_obj = update(db_session=session, feedback=feedback, feedback_in=feedback_in)

    assert updated_feedback_obj.rating == updated_rating
    assert updated_feedback_obj.feedback == updated_feedback_text


def test_delete(session, feedback):
    from dispatch.feedback.incident.service import delete, get

    delete(db_session=session, feedback_id=feedback.id)
    assert not get(db_session=session, feedback_id=feedback.id)
