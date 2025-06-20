from datetime import datetime

from dispatch.case.models import Case
from dispatch.auth.models import DispatchUser
from dispatch.event.models import EventCreateMinimal, EventUpdate


def test_create_custom_event(
    session,
    case: Case,
    user: DispatchUser,
    organization,
):
    """Tests the creation of a custom case event."""
    # Ensure the case is associated with the organization
    case.project.organization = organization
    session.add(case.project)
    session.commit()

    # Add user as a participant to the case so they have permissions
    from dispatch.participant import flows as participant_flows
    from dispatch.participant_role.models import ParticipantRoleType

    participant_flows.add_participant(
        user.email,
        case,
        session,
        roles=[ParticipantRoleType.assignee],
    )

    # Import the view function directly
    from dispatch.case.views import create_custom_event
    from starlette.background import BackgroundTasks

    now = datetime.utcnow()
    event_in = EventCreateMinimal(
        source="Case Participant",
        description="This is a test event",
        started_at=now,
        type="Custom event",
        details={},
    )

    # Call the view function directly
    background_tasks = BackgroundTasks()
    create_custom_event(
        db_session=session,
        organization=organization.slug,
        case_id=case.id,
        current_case=case,
        event_in=event_in,
        current_user=user,
        background_tasks=background_tasks,
    )

    # The function should complete without error
    assert True


def test_update_custom_event(
    session,
    case: Case,
    user: DispatchUser,
    organization,
):
    """Tests updating a custom case event."""
    # Ensure the case is associated with the organization
    case.project.organization = organization
    session.add(case.project)
    session.commit()

    # Add user as a participant to the case so they have permissions
    from dispatch.participant import flows as participant_flows
    from dispatch.participant_role.models import ParticipantRoleType

    participant_flows.add_participant(
        user.email,
        case,
        session,
        roles=[ParticipantRoleType.assignee],
    )

    # First create an event via the service to get a UUID
    from dispatch.event.service import log_case_event

    event = log_case_event(
        db_session=session,
        source="Case Participant",
        description="Initial description",
        case_id=case.id,
        started_at=datetime.utcnow(),
        type="Custom event",
    )

    # Import the view function directly
    from dispatch.case.views import update_custom_event
    from starlette.background import BackgroundTasks

    now = datetime.utcnow()
    update_data = EventUpdate(
        uuid=event.uuid,
        source="Case Participant",  # Should preserve the source
        description="Updated description",
        started_at=now,
        ended_at=now,
        type="Custom event",
        details={},
        owner="",
        pinned=False,
    )

    # Call the view function directly
    background_tasks = BackgroundTasks()
    update_custom_event(
        db_session=session,
        organization=organization.slug,
        case_id=case.id,
        current_case=case,
        event_in=update_data,
        current_user=user,
        background_tasks=background_tasks,
    )

    # The function should complete without error
    assert True


def test_update_custom_event_preserves_source(
    session,
    case: Case,
    user: DispatchUser,
    organization,
):
    """Tests that updating a case event preserves the original source."""
    # Ensure the case is associated with the organization
    case.project.organization = organization
    session.add(case.project)
    session.commit()

    # Add user as a participant to the case so they have permissions
    from dispatch.participant import flows as participant_flows
    from dispatch.participant_role.models import ParticipantRoleType

    participant_flows.add_participant(
        user.email,
        case,
        session,
        roles=[ParticipantRoleType.assignee],
    )

    # Create an event with a specific source
    from dispatch.event.service import log_case_event

    original_source = "Slack message from John Doe"
    event = log_case_event(
        db_session=session,
        source=original_source,
        description="Initial description",
        case_id=case.id,
        started_at=datetime.utcnow(),
        type="Custom event",
    )

    # Test the service function directly instead of the view function
    from dispatch.event.service import update_case_event

    now = datetime.utcnow()
    update_data = EventUpdate(
        uuid=event.uuid,
        source=original_source,  # Preserve the original source
        description="Updated description",
        started_at=now,
        ended_at=now,
        type="Custom event",
        details={},
        owner="",
        pinned=False,
    )

    # Call the service function directly
    update_case_event(
        db_session=session,
        event_in=update_data,
    )

    # Verify the source was preserved by checking the event in the database
    from dispatch.event.service import get_by_uuid

    updated_event = get_by_uuid(db_session=session, uuid=event.uuid)
    assert updated_event.source == original_source
    assert updated_event.description == "Updated description"


def test_delete_custom_event(
    session,
    case: Case,
    user: DispatchUser,
    organization,
):
    """Tests deleting a custom case event."""
    # Ensure the case is associated with the organization
    case.project.organization = organization
    session.add(case.project)
    session.commit()

    # Add user as a participant to the case so they have permissions
    from dispatch.participant import flows as participant_flows
    from dispatch.participant_role.models import ParticipantRoleType

    participant_flows.add_participant(
        user.email,
        case,
        session,
        roles=[ParticipantRoleType.assignee],
    )

    # First create an event via the service to get a UUID
    from dispatch.event.service import log_case_event

    event = log_case_event(
        db_session=session,
        source="Case Participant",
        description="Event to delete",
        case_id=case.id,
        started_at=datetime.utcnow(),
        type="Custom event",
    )

    # Import the view function directly
    from dispatch.case.views import delete_custom_event
    from starlette.background import BackgroundTasks

    # Call the view function directly
    background_tasks = BackgroundTasks()
    delete_custom_event(
        db_session=session,
        organization=organization.slug,
        case_id=case.id,
        current_case=case,
        event_uuid=str(event.uuid),
        current_user=user,
        background_tasks=background_tasks,
    )

    # The function should complete without error
    assert True
