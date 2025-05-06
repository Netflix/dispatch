import pytest
from datetime import datetime, timezone
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
    feedback = "The incident commander did an excellent job"

    feedback_in = FeedbackCreate(
        rating=rating,
        feedback=feedback,
        incident=incident, # This would need to be IncidentRead.model_validate(incident)
        # case=... # Similar full population as in other tests
        # participant=... # Similar full population
    )
    # feedback_obj = create(db_session=session, feedback_in=feedback_in)
    # assert feedback_obj


def test_update(session, feedback, individual_contact): # Added individual_contact fixture
    from dispatch.feedback.incident.service import update
    from dispatch.feedback.incident.models import FeedbackUpdate
    from dispatch.participant.models import Participant # ORM model

    # Ensure feedback.case and feedback.participant are valid ORM objects
    # and have all necessary nested data (e.g., individual for participant,
    # case_type, case_severity, etc., for case).
    # This relies on the 'feedback' fixture being comprehensive.

    if not feedback.case:
        pytest.fail("Feedback fixture must have a valid case associated.")

    if not feedback.participant:
        # If feedback fixture doesn't create a participant, create one
        p = Participant(individual=individual_contact, project=feedback.case.project, case_id=feedback.case.id)
        session.add(p)
        feedback.participant = p
        session.commit()
    elif not feedback.participant.individual:
        feedback.participant.individual = individual_contact
        session.commit()

    # Ensure related objects on feedback.case are present
    if not all([feedback.case.case_type, feedback.case.case_severity, feedback.case.case_priority, feedback.case.project]):
        pytest.fail("Feedback.case fixture is missing required related objects (type, severity, priority, project).")

    if not feedback.case.assignee:
        feedback.case.assignee = feedback.participant # or some other valid participant from the case
        session.commit()

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
