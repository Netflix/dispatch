""" Tests oncall service feedback """


def test_create(session, participant, project):
    from dispatch.feedback.service.service import create
    from dispatch.feedback.service.models import ServiceFeedbackCreate

    feedback = "Not a difficult shift"
    hours = 5
    rating = "No effort"

    feedback_in = ServiceFeedbackCreate(
        individual=participant.individual,
        rating=rating,
        feedback=feedback,
        hours=hours,
        project=project,
    )
    feedback = create(db_session=session, service_feedback_in=feedback_in)
    assert feedback


def test_get(session, service_feedback):
    from dispatch.feedback.service.service import get

    t_feedback = get(db_session=session, service_feedback_id=service_feedback.id)
    assert t_feedback.id == service_feedback.id


def test_get_all(session):
    from dispatch.feedback.service.service import get_all

    t_feedbacks = get_all(db_session=session).all()
    assert t_feedbacks


def test_update(session, service_feedback):
    from dispatch.feedback.service.service import update
    from dispatch.feedback.service.models import ServiceFeedbackUpdate

    feedback_text = "Changed my mind. The shift was difficult"

    feedback_in = ServiceFeedbackUpdate(id=service_feedback.id, feedback=feedback_text)
    feedback = update(
        db_session=session, service_feedback=service_feedback, service_feedback_in=feedback_in
    )

    assert feedback.feedback == feedback_text


def test_delete(session, service_feedback):
    from dispatch.feedback.service.service import delete, get

    delete(db_session=session, service_feedback_id=service_feedback.id)
    assert not get(db_session=session, service_feedback_id=service_feedback.id)
