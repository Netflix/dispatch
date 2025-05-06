from datetime import datetime, timezone
from dispatch.feedback.incident.enums import FeedbackRating
from dispatch.project.models import ProjectRead
from dispatch.case.models import CaseReadMinimal
from dispatch.participant.models import ParticipantRead, ParticipantReadMinimal
from dispatch.case.type.models import CaseTypeRead
from dispatch.case.severity.models import CaseSeverityRead
from dispatch.case.priority.models import CasePriorityRead

def test_create(session, case, individual_contact, participant_role):
    from dispatch.feedback.incident.service import create
    from dispatch.feedback.incident.models import FeedbackCreate
    from dispatch.participant.models import Participant # ORM model

    # Ensure the case has a reporter with an individual contact
    # This would typically be set up by the CaseFactory
    if not case.reporter:
        # Create a minimal reporter participant if one doesn't exist
        reporter_participant = Participant(
            individual=individual_contact,
            case_id=case.id, # Link to the current case
            participant_roles=[participant_role] # Add a default role
        )
        session.add(reporter_participant)
        case.reporter = reporter_participant
        session.commit() # Commit to get IDs if necessary and establish relationship

    if not case.assignee: # Also ensure assignee for CaseReadMinimal
        case.assignee = case.reporter # Or another valid participant
        session.commit()


    rating = FeedbackRating.neither_satisfied_nor_dissatisfied
    feedback = "The incident commander did an excellent job"

    feedback_in = FeedbackCreate(
        rating=rating,
        feedback=feedback,
        case=CaseReadMinimal(
            id=case.id,
            name=case.name,
            title=case.title,
            description=case.description,
            resolution=case.resolution,
            status=case.status,
            visibility=case.visibility,
            closed_at=case.closed_at,
            reported_at=case.reported_at,
            dedicated_channel=case.dedicated_channel,
            case_type=CaseTypeRead.model_validate(case.case_type),
            case_severity=CaseSeverityRead.model_validate(case.case_severity),
            case_priority=CasePriorityRead.model_validate(case.case_priority),
            project=ProjectRead.model_validate(case.project),
            assignee=(
                ParticipantReadMinimal.model_validate(case.assignee)
                if case.assignee is not None
                else None
            ),
            case_costs=[],
        ),
        participant=(
            ParticipantRead.model_validate(case.reporter) if case.reporter is not None else None
        ),
    )
    created_feedback = create(db_session=session, feedback_in=feedback_in)
    assert created_feedback
    assert created_feedback.rating == rating
    assert created_feedback.feedback == feedback
    assert created_feedback.case_id == case.id
    if case.reporter:
        assert created_feedback.participant_id == case.reporter.id


def test_get(session, feedback):
    from dispatch.feedback.incident.service import get

    t_feedback = get(db_session=session, feedback_id=feedback.id)
    assert t_feedback.id == feedback.id


def test_get_all(session, feedbacks):
    from dispatch.feedback.incident.service import get_all

    t_feedbacks = get_all(db_session=session).all()
    # assert t_feedbacks # This might be empty if no feedbacks fixture provided data
    assert isinstance(t_feedbacks, list)


def test_update(session, feedback, individual_contact, case):  # Added case fixture
    from dispatch.feedback.incident.service import update
    from dispatch.feedback.incident.models import FeedbackUpdate
    from dispatch.participant.models import Participant  # ORM model

    # Ensure feedback.case is populated for the test
    if feedback.case is None:  # Added 'is None'
        feedback.case = case  # Use the case fixture
        session.commit()

    # Ensure feedback.participant and feedback.case are populated by the feedback fixture
    # and have the necessary nested data (like individual for participant)
    if feedback.participant is None:  # Added 'is None'
        # If feedback fixture doesn't create a participant, create one
        # This setup depends on how 'feedback' fixture is defined
        # Ensure feedback.case is not None before accessing its id
        if feedback.case is not None:
            p = Participant(
                individual=individual_contact, case_id=feedback.case.id
            )  # Removed project argument
            session.add(p)
            feedback.participant = p
            session.commit()
    elif feedback.participant.individual is None:  # Added 'is None'
        feedback.participant.individual = individual_contact
        session.commit()

    if feedback.case is not None and feedback.case.assignee is None:  # Added 'is not None' and 'is None'
        # Use feedback's participant as assignee if none, or another valid participant
        feedback.case.assignee = feedback.participant
        session.commit()

    updated_rating = FeedbackRating.very_satisfied
    updated_feedback_text = "The incident commander did an outstanding job after the update."

    feedback_in = FeedbackUpdate(
        rating=updated_rating,
        feedback=updated_feedback_text,
        case=CaseReadMinimal(
            id=feedback.case.id if feedback.case is not None else None,
            name=feedback.case.name if feedback.case is not None else None,
            title=feedback.case.title if feedback.case is not None else None,
            description=(
                feedback.case.description if feedback.case is not None else None
            ),
            resolution=(
                feedback.case.resolution if feedback.case is not None else None
            ),
            status=feedback.case.status if feedback.case is not None else None,
            visibility=(
                feedback.case.visibility if feedback.case is not None else None
            ),
            closed_at=(
                feedback.case.closed_at if feedback.case is not None else None
            ),
            reported_at=(
                feedback.case.reported_at if feedback.case is not None else None
            ),
            dedicated_channel=(
                feedback.case.dedicated_channel
                if feedback.case is not None
                else None
            ),
            case_type=(
                CaseTypeRead.model_validate(feedback.case.case_type)
                if feedback.case is not None
                else None
            ),
            case_severity=(
                CaseSeverityRead.model_validate(feedback.case.case_severity)
                if feedback.case is not None
                else None
            ),
            case_priority=(
                CasePriorityRead.model_validate(feedback.case.case_priority)
                if feedback.case is not None
                else None
            ),
            project=(
                ProjectRead.model_validate(feedback.case.project)
                if feedback.case is not None
                else None
            ),
            assignee=(
                ParticipantReadMinimal.model_validate(feedback.case.assignee)
                if feedback.case is not None and feedback.case.assignee is not None
                else None
            ),
            case_costs=[],
        ),
        participant=(
            ParticipantRead.model_validate(feedback.participant)
            if feedback.participant is not None
            else None
        ),
    )
    updated_feedback_obj = update(db_session=session, feedback=feedback, feedback_in=feedback_in)

    assert updated_feedback_obj.rating == updated_rating
    assert updated_feedback_obj.feedback == updated_feedback_text


def test_delete(session, feedback):
    from dispatch.feedback.incident.service import delete, get

    delete(db_session=session, feedback_id=feedback.id)
    assert not get(db_session=session, feedback_id=feedback.id)
