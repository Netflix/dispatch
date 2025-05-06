""" Tests oncall service feedback """

from datetime import datetime, timezone
from dispatch.feedback.service.enums import ServiceFeedbackRating
from dispatch.individual.models import IndividualContactReadMinimal
from dispatch.project.models import ProjectRead


def test_create(session, participant, project):
    from dispatch.feedback.service.service import create
    from dispatch.feedback.service.models import ServiceFeedbackCreate

    feedback = "Not a difficult shift"
    hours = 5
    rating = ServiceFeedbackRating.no_effort

    feedback_in = ServiceFeedbackCreate(
        individual=IndividualContactReadMinimal(id=participant.individual.id),
        rating=rating,
        feedback=feedback,
        hours=hours,
        schedule="test_schedule",
        shift_start_at=datetime.now(timezone.utc),
        shift_end_at=datetime.now(timezone.utc),
        details=[],
        project=ProjectRead(
            id=project.id,
            name=project.name,
            display_name=getattr(project, 'display_name', ''),
            owner_email=getattr(project, 'owner_email', None),
            owner_conversation=getattr(project, 'owner_conversation', None),
            annual_employee_cost=getattr(project, 'annual_employee_cost', 50000),
            business_year_hours=getattr(project, 'business_year_hours', 2080),
            description=getattr(project, 'description', None),
            default=getattr(project, 'default', False),
            color=getattr(project, 'color', None),
            send_daily_reports=getattr(project, 'send_daily_reports', True),
            send_weekly_reports=getattr(project, 'send_weekly_reports', False),
            weekly_report_notification_id=getattr(project, 'weekly_report_notification_id', None),
            enabled=getattr(project, 'enabled', True),
            storage_folder_one=getattr(project, 'storage_folder_one', None),
            storage_folder_two=getattr(project, 'storage_folder_two', None),
            storage_use_folder_one_as_primary=getattr(project, 'storage_use_folder_one_as_primary', True),
            storage_use_title=getattr(project, 'storage_use_title', False),
            allow_self_join=getattr(project, 'allow_self_join', True),
            select_commander_visibility=getattr(project, 'select_commander_visibility', True),
            report_incident_instructions=getattr(project, 'report_incident_instructions', None),
            report_incident_title_hint=getattr(project, 'report_incident_title_hint', None),
            report_incident_description_hint=getattr(project, 'report_incident_description_hint', None),
            snooze_extension_oncall_service=getattr(project, 'snooze_extension_oncall_service', None),
        ),
        created_at=datetime.now(timezone.utc)
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


def test_update(session, service_feedback, individual_contact):
    from dispatch.feedback.service.service import update
    from dispatch.feedback.service.models import ServiceFeedbackUpdate

    feedback_text = "Changed my mind. The shift was difficult"

    # Use the individual_contact fixture if service_feedback.individual is None
    has_individual = service_feedback.individual is not None
    individual_id = service_feedback.individual.id if has_individual else individual_contact.id

    feedback_in = ServiceFeedbackUpdate(
        id=service_feedback.id,
        feedback=feedback_text,
        hours=5,
        schedule="test_schedule",
        shift_start_at=datetime.now(timezone.utc),
        shift_end_at=datetime.now(timezone.utc),
        details=[],
        individual=IndividualContactReadMinimal(id=individual_id),
        project=ProjectRead(
            id=service_feedback.project.id,
            name=service_feedback.project.name,
            display_name=getattr(service_feedback.project, 'display_name', ''),
            owner_email=getattr(service_feedback.project, 'owner_email', None),
            owner_conversation=getattr(service_feedback.project, 'owner_conversation', None),
            annual_employee_cost=getattr(service_feedback.project, 'annual_employee_cost', 50000),
            business_year_hours=getattr(service_feedback.project, 'business_year_hours', 2080),
            description=getattr(service_feedback.project, 'description', None),
            default=getattr(service_feedback.project, 'default', False),
            color=getattr(service_feedback.project, 'color', None),
            send_daily_reports=getattr(service_feedback.project, 'send_daily_reports', True),
            send_weekly_reports=getattr(service_feedback.project, 'send_weekly_reports', False),
            weekly_report_notification_id=getattr(service_feedback.project, 'weekly_report_notification_id', None),
            enabled=getattr(service_feedback.project, 'enabled', True),
            storage_folder_one=getattr(service_feedback.project, 'storage_folder_one', None),
            storage_folder_two=getattr(service_feedback.project, 'storage_folder_two', None),
            storage_use_folder_one_as_primary=getattr(service_feedback.project, 'storage_use_folder_one_as_primary', True),
            storage_use_title=getattr(service_feedback.project, 'storage_use_title', False),
            allow_self_join=getattr(service_feedback.project, 'allow_self_join', True),
            select_commander_visibility=getattr(service_feedback.project, 'select_commander_visibility', True),
            report_incident_instructions=getattr(service_feedback.project, 'report_incident_instructions', None),
            report_incident_title_hint=getattr(service_feedback.project, 'report_incident_title_hint', None),
            report_incident_description_hint=getattr(service_feedback.project, 'report_incident_description_hint', None),
            snooze_extension_oncall_service=getattr(service_feedback.project, 'snooze_extension_oncall_service', None),
        ),
        created_at=service_feedback.created_at
    )
    feedback = update(
        db_session=session, service_feedback=service_feedback, service_feedback_in=feedback_in
    )

    assert feedback.feedback == feedback_text


def test_delete(session, service_feedback):
    from dispatch.feedback.service.service import delete, get

    delete(db_session=session, service_feedback_id=service_feedback.id)
    assert not get(db_session=session, service_feedback_id=service_feedback.id)
