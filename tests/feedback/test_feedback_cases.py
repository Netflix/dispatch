from datetime import datetime, timezone
from dispatch.feedback.incident.enums import FeedbackRating
from dispatch.project.models import ProjectRead
from dispatch.case.models import CaseReadMinimal
from dispatch.participant.models import ParticipantRead

def test_create(session, case, case_type, case_priority):
    from dispatch.feedback.incident.service import create
    from dispatch.feedback.incident.models import FeedbackCreate

    case.incident_type = case_type
    case.incident_priority = case_priority
    rating = FeedbackRating.neither_satisfied_nor_dissatisfied
    feedback = "The incident commander did an excellent job"

    feedback_in = FeedbackCreate(
        rating=rating,
        feedback=feedback,
        case=CaseReadMinimal(id=case.id, name=getattr(case, 'name', 'Test Case')),
        participant=ParticipantRead(id=getattr(case, 'participant_id', 1)),
    )
    feedback = create(db_session=session, feedback_in=feedback_in)
    assert feedback


def test_get(session, feedback):
    from dispatch.feedback.incident.service import get

    t_feedback = get(db_session=session, feedback_id=feedback.id)
    assert t_feedback.id == feedback.id


def test_get_all(session, feedbacks):
    from dispatch.feedback.incident.service import get_all

    t_feedbacks = get_all(db_session=session).all()
    assert t_feedbacks


def test_update(session, feedback):
    from dispatch.feedback.incident.service import update
    from dispatch.feedback.incident.models import FeedbackUpdate

    rating = FeedbackRating.very_satisfied
    feedback_text = "The incident commander did an excellent job"

    feedback_in = FeedbackUpdate(
        rating=rating,
        feedback=feedback_text,
        case=CaseReadMinimal(id=feedback.case.id, name=getattr(feedback.case, 'name', 'Test Case')) if feedback.case else None,
        participant=ParticipantRead(id=getattr(feedback, 'participant_id', 1)),
    )
    feedback = update(db_session=session, feedback=feedback, feedback_in=feedback_in)

    assert feedback.rating == rating
    assert feedback.feedback == feedback_text


def test_delete(session, feedback):
    from dispatch.feedback.incident.service import delete, get

    delete(db_session=session, feedback_id=feedback.id)
    assert not get(db_session=session, feedback_id=feedback.id)
