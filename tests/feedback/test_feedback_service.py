import pytest


def test_get(session, feedback):
    from dispatch.feedback.service import get

    t_feedback = get(db_session=session, feedback_id=feedback.id)
    assert t_feedback.id == feedback.id


def test_get_all(session, feedbacks):
    from dispatch.feedback.service import get_all

    t_feedbacks = get_all(db_session=session).all()
    assert len(t_feedbacks) > 1


def test_create(session):
    from dispatch.feedback.service import create
    from dispatch.feedback.models import FeedbackCreate

    rating = "XXX"
    feedback = "XXX"

    feedback_in = FeedbackCreate(
        rating=rating,
        feedback=feedback,
    )
    feedback = create(db_session=session, feedback_in=feedback_in)
    assert feedback


@pytest.mark.skip
def test_update(session, feedback):
    from dispatch.feedback.service import update
    from dispatch.feedback.models import FeedbackUpdate

    rating = "Updated rating"

    feedback_in = FeedbackUpdate(
        rating=rating,
    )
    feedback = update(db_session=session, feedback=feedback, feedback_in=feedback_in)
    assert feedback.rating == rating


def test_delete(session, feedback):
    from dispatch.feedback.service import delete, get

    delete(db_session=session, feedback_id=feedback.id)
    assert not get(db_session=session, feedback_id=feedback.id)
