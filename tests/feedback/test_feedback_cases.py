def test_create(session, case, case_type, case_priority):
    from dispatch.feedback.incident.service import create
    from dispatch.feedback.incident.models import FeedbackCreate

    case.incident_type = case_type
    case.incident_priority = case_priority
    rating = "Neither satisfied nor dissatisfied"
    feedback = "The incident commander did an excellent job"

    feedback_in = FeedbackCreate(rating=rating, feedback=feedback, case=case)
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

    rating = "Very satisfied"
    feedback_text = "The incident commander did an excellent job"

    feedback_in = FeedbackUpdate(rating=rating, feedback=feedback_text)
    feedback = update(db_session=session, feedback=feedback, feedback_in=feedback_in)

    assert feedback.rating == rating
    assert feedback.feedback == feedback_text


def test_delete(session, feedback):
    from dispatch.feedback.incident.service import delete, get

    delete(db_session=session, feedback_id=feedback.id)
    assert not get(db_session=session, feedback_id=feedback.id)
