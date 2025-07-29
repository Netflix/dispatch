import pytest
import json
from json.decoder import JSONDecodeError
from sqlalchemy_filters.exceptions import BadFilterFormat
from dispatch.database.service import (
    Operator,
    Filter,
    search_filter_sort_paginate,
    restricted_incident_filter,
    apply_filters,
)
from dispatch.incident.models import Incident
from dispatch.enums import UserRoles, Visibility
from dispatch.case.models import Case
from dispatch.database.service import restricted_case_filter


# Test the Filter class and related functions
def test_operator_invalid():
    """Tests that invalid operators raise BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Operator("invalid_operator")


def test_filter_missing_field():
    """Tests that missing field raises BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Filter({})


def test_filter_invalid_spec():
    """Tests that invalid filter spec raises BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Filter(None)


# Test search_filter_sort_paginate
def test_search_filter_sort_paginate_basic(session, user):
    """Tests basic functionality of search_filter_sort_paginate."""
    result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=user, role=UserRoles.member
    )

    assert isinstance(result, dict)
    assert "items" in result
    assert "itemsPerPage" in result
    assert "page" in result
    assert "total" in result


def test_basic_pagination(session, incidents, admin_user):
    """Test basic pagination functionality."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        page=1,
        items_per_page=2,
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert result["page"] == 1
    assert result["itemsPerPage"] == 2
    assert len(result["items"]) == 2


def test_simple_filter_specification(session, incidents, admin_user):
    """Test filtering with simple filter specification."""
    filter_spec = {"field": "visibility", "op": "==", "value": "open"}

    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        filter_spec=json.dumps(filter_spec),
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert all(incident.visibility == Visibility.open for incident in result["items"])


def test_sorting_functionality(session, incidents, user):
    """Test sorting functionality."""
    # Create a unique prefix for our test incidents to ensure isolation
    import uuid
    import json

    test_prefix = f"SORT_TEST_{uuid.uuid4().hex[:8]}_"

    # Create test incidents with predictable titles for sorting
    from dispatch.incident.models import Incident
    from dispatch.enums import Visibility

    test_incidents = []
    test_titles = [f"{test_prefix}Alpha", f"{test_prefix}Beta", f"{test_prefix}Charlie"]

    for title in test_titles:
        incident = Incident(
            title=title,
            description="Test incident for sorting",
            visibility=Visibility.open,
            project_id=incidents[0].project_id,  # Use same project as fixture incidents
        )
        session.add(incident)
        test_incidents.append(incident)

    session.commit()

    try:
        # Use filter instead of search to find our test incidents
        filter_spec = {"field": "title", "op": "like", "value": f"{test_prefix}%"}

        result = search_filter_sort_paginate(
            db_session=session,
            model="Incident",
            filter_spec=json.dumps(filter_spec),  # Filter to only our test incidents
            sort_by=["title"],
            descending=[True],
            current_user=user,
        )

        titles = [incident.title for incident in result["items"]]
        expected_titles = sorted(test_titles, reverse=True)

        assert titles == expected_titles, f"Expected {expected_titles}, got {titles}"

    finally:
        # Clean up our test incidents
        for incident in test_incidents:
            session.delete(incident)
        session.commit()


def test_unlimited_pagination(session, incidents, admin_user):
    """Test pagination with unlimited items per page."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        items_per_page=-1,
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert len(result["items"]) == result["total"]  # All items


def test_empty_query_string(session, incidents, admin_user):
    """Test behavior with empty query string."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        query_str="",
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert len(result["items"]) > 0  # Should return all items


def test_invalid_filter_spec(session, incidents, user):
    """Test behavior with invalid filter specification."""
    with pytest.raises(JSONDecodeError):  # Adjust exception type as needed
        search_filter_sort_paginate(
            db_session=session,
            model="Incident",
            filter_spec="invalid_json",
            current_user=user,
        )


def test_pagination_out_of_bounds(session, incidents, user):
    """Test pagination when page number is out of bounds."""
    result = search_filter_sort_paginate(
        db_session=session, model="Incident", page=999, items_per_page=5, current_user=user
    )

    assert len(result["items"]) == 0
    assert result["page"] == 999


def test_role_based_filtering(session, incidents, user, admin_user):
    """Test filtering based on user role."""
    # Test admin access
    admin_result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=admin_user, role=UserRoles.admin
    )

    # Test member access
    member_result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=user, role=UserRoles.member
    )

    assert len(admin_result["items"]) >= len(member_result["items"])


# Test restricted filters
def test_restricted_incident_filter_with_test_data(session, user, admin_user):
    """Test incident filtering with comprehensive test data setup."""
    from dispatch.incident.models import Incident
    from dispatch.participant.models import Participant
    from dispatch.individual.models import IndividualContact
    from dispatch.enums import Visibility, UserRoles
    from dispatch.project.models import Project
    import uuid

    # Store original user email to restore later
    original_user_email = getattr(user, "email", "test@example.com")

    # Create unique identifiers to avoid conflicts
    timestamp = int(__import__("time").time() * 1000000)  # microsecond precision
    test_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"

    # Create unique test data
    project_name = f"test_project_{test_id}"
    user_email = f"test_user_{test_id}@example.com"
    other_email = f"other_user_{test_id}@example.com"

    project = None  # Initialize to avoid unbound variable error

    # Ensure clean session state
    session.expire_all()

    try:
        # Create test project
        project = Project(name=project_name, default=False)
        session.add(project)
        session.flush()  # Use flush instead of commit to get ID within transaction

        # Create test individual contacts
        regular_user_contact = IndividualContact(
            email=user_email, name="Regular User", project_id=project.id
        )
        other_user_contact = IndividualContact(
            email=other_email, name="Other User", project_id=project.id
        )
        session.add_all([regular_user_contact, other_user_contact])
        session.flush()

        # Create test incidents with unique titles
        test_prefix = f"TEST_{test_id}"
        incidents_to_create = [
            Incident(
                title=f"{test_prefix}_Open_Incident_1",
                description="Description",
                visibility=Visibility.open,
                project_id=project.id,
            ),
            Incident(
                title=f"{test_prefix}_Open_Incident_2",
                description="Description",
                visibility=Visibility.open,
                project_id=project.id,
            ),
            Incident(
                title=f"{test_prefix}_Restricted_User_Participant",
                description="Description",
                visibility=Visibility.restricted,
                project_id=project.id,
            ),
            Incident(
                title=f"{test_prefix}_Restricted_No_Participant",
                description="Description",
                visibility=Visibility.restricted,
                project_id=project.id,
            ),
        ]

        session.add_all(incidents_to_create)
        session.flush()

        # Get the created incidents
        created_incidents = (
            session.query(Incident).filter(Incident.title.like(f"{test_prefix}%")).all()
        )

        restricted_user_participant = next(
            i for i in created_incidents if "User_Participant" in i.title
        )

        # Create participants - user is participant in one restricted incident
        user_participant = Participant(
            incident_id=restricted_user_participant.id,
            individual_contact_id=regular_user_contact.id,
        )
        session.add(user_participant)
        session.flush()

        # Temporarily change user email for testing
        user.email = user_email

        # Test admin role - should see all incidents (filter by project to avoid other test data)
        admin_query = session.query(Incident).filter(Incident.project_id == project.id)
        admin_filtered = restricted_incident_filter(admin_query, admin_user, UserRoles.admin)
        admin_results = admin_filtered.all()
        assert (
            len(admin_results) == 4
        ), f"Admin should see all 4 incidents, got {len(admin_results)}"

        # Test owner role - should see all incidents
        owner_query = session.query(Incident).filter(Incident.project_id == project.id)
        owner_filtered = restricted_incident_filter(owner_query, user, UserRoles.owner)
        owner_results = owner_filtered.all()
        assert (
            len(owner_results) == 4
        ), f"Owner should see all 4 incidents, got {len(owner_results)}"

        # Test manager role - should see all incidents
        manager_query = session.query(Incident).filter(Incident.project_id == project.id)
        manager_filtered = restricted_incident_filter(manager_query, user, UserRoles.manager)
        manager_results = manager_filtered.all()
        assert (
            len(manager_results) == 4
        ), f"Manager should see all 4 incidents, got {len(manager_results)}"

        # Test member role - should see open incidents + restricted where user is participant
        member_query = session.query(Incident).filter(Incident.project_id == project.id)
        member_filtered = restricted_incident_filter(member_query, user, UserRoles.member)
        member_results = member_filtered.all()
        assert (
            len(member_results) == 3
        ), f"Member should see 3 incidents (2 open + 1 restricted as participant), got {len(member_results)}"

        # Verify member sees correct incidents
        member_titles = {incident.title for incident in member_results}
        expected_titles = {
            f"{test_prefix}_Open_Incident_1",
            f"{test_prefix}_Open_Incident_2",
            f"{test_prefix}_Restricted_User_Participant",
        }
        assert (
            member_titles == expected_titles
        ), f"Member should see {expected_titles}, got {member_titles}"

    finally:
        # Always restore original user email
        user.email = original_user_email

        # Clean up test data in reverse order
        try:
            if project and hasattr(project, "id"):
                # Clean up participants
                session.query(Participant).filter(
                    Participant.incident_id.in_(
                        session.query(Incident.id).filter(Incident.project_id == project.id)
                    )
                ).delete(synchronize_session=False)

                # Clean up incidents
                session.query(Incident).filter(Incident.project_id == project.id).delete(
                    synchronize_session=False
                )

                # Clean up contacts
                session.query(IndividualContact).filter(
                    IndividualContact.project_id == project.id
                ).delete(synchronize_session=False)

                # Clean up project
                session.query(Project).filter(Project.id == project.id).delete(
                    synchronize_session=False
                )

                session.flush()
        except Exception as cleanup_error:
            # If cleanup fails, at least try to rollback
            session.rollback()
            print(f"Warning: Cleanup failed: {cleanup_error}")


def test_restricted_case_filter_with_test_data(session, user, admin_user):
    """Test case filtering with comprehensive test data setup."""
    from dispatch.case.models import Case
    from dispatch.participant.models import Participant
    from dispatch.individual.models import IndividualContact
    from dispatch.enums import Visibility, UserRoles
    from dispatch.project.models import Project
    import uuid

    # Store original user email to restore later
    original_user_email = getattr(user, "email", "test@example.com")

    # Create unique identifiers to avoid conflicts
    timestamp = int(__import__("time").time() * 1000000)  # microsecond precision
    test_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"

    # Create unique test data
    project_name = f"test_case_project_{test_id}"
    user_email = f"test_case_user_{test_id}@example.com"
    other_email = f"other_case_user_{test_id}@example.com"

    project = None  # Initialize to avoid unbound variable error

    # Ensure clean session state
    session.expire_all()

    try:
        # Create test project
        project = Project(name=project_name, default=False)
        session.add(project)
        session.flush()  # Use flush instead of commit to get ID within transaction

        # Create test individual contacts
        regular_user_contact = IndividualContact(
            email=user_email, name="Regular User", project_id=project.id
        )
        other_user_contact = IndividualContact(
            email=other_email, name="Other User", project_id=project.id
        )
        session.add_all([regular_user_contact, other_user_contact])
        session.flush()

        # Create test cases with unique titles
        test_prefix = f"CASE_TEST_{test_id}"
        cases_to_create = [
            Case(
                title=f"{test_prefix}_Open_Case_1",
                description="Description",
                visibility=Visibility.open,
                project_id=project.id,
            ),
            Case(
                title=f"{test_prefix}_Open_Case_2",
                description="Description",
                visibility=Visibility.open,
                project_id=project.id,
            ),
            Case(
                title=f"{test_prefix}_Restricted_User_Participant",
                description="Description",
                visibility=Visibility.restricted,
                project_id=project.id,
            ),
            Case(
                title=f"{test_prefix}_Restricted_No_Participant",
                description="Description",
                visibility=Visibility.restricted,
                project_id=project.id,
            ),
        ]

        session.add_all(cases_to_create)
        session.flush()

        # Get the created cases
        created_cases = session.query(Case).filter(Case.title.like(f"{test_prefix}%")).all()

        restricted_user_participant = next(
            c for c in created_cases if "User_Participant" in c.title
        )

        # Create participants - user is participant in one restricted case
        user_participant = Participant(
            case_id=restricted_user_participant.id, individual_contact_id=regular_user_contact.id
        )
        session.add(user_participant)
        session.flush()

        # Temporarily change user email for testing
        user.email = user_email

        # Test admin role - should see all cases
        admin_query = session.query(Case).filter(Case.project_id == project.id)
        admin_filtered = restricted_case_filter(admin_query, admin_user, UserRoles.admin)
        admin_results = admin_filtered.all()
        assert len(admin_results) == 4, f"Admin should see all 4 cases, got {len(admin_results)}"

        # Test owner role - should see all cases
        owner_query = session.query(Case).filter(Case.project_id == project.id)
        owner_filtered = restricted_case_filter(owner_query, user, UserRoles.owner)
        owner_results = owner_filtered.all()
        assert len(owner_results) == 4, f"Owner should see all 4 cases, got {len(owner_results)}"

        # Test manager role - should see all cases
        manager_query = session.query(Case).filter(Case.project_id == project.id)
        manager_filtered = restricted_case_filter(manager_query, user, UserRoles.manager)
        manager_results = manager_filtered.all()
        assert (
            len(manager_results) == 4
        ), f"Manager should see all 4 cases, got {len(manager_results)}"

        # Test member role - should see open cases + restricted where user is participant
        member_query = session.query(Case).filter(Case.project_id == project.id)
        member_filtered = restricted_case_filter(member_query, user, UserRoles.member)
        member_results = member_filtered.all()
        assert (
            len(member_results) == 3
        ), f"Member should see 3 cases (2 open + 1 restricted as participant), got {len(member_results)}"

        # Verify member sees correct cases
        member_titles = {case.title for case in member_results}
        expected_titles = {
            f"{test_prefix}_Open_Case_1",
            f"{test_prefix}_Open_Case_2",
            f"{test_prefix}_Restricted_User_Participant",
        }
        assert (
            member_titles == expected_titles
        ), f"Member should see {expected_titles}, got {member_titles}"

    finally:
        # Always restore original user email
        user.email = original_user_email

        # Clean up test data in reverse order
        try:
            if project and hasattr(project, "id"):
                # Clean up participants
                session.query(Participant).filter(
                    Participant.case_id.in_(
                        session.query(Case.id).filter(Case.project_id == project.id)
                    )
                ).delete(synchronize_session=False)

                # Clean up cases
                session.query(Case).filter(Case.project_id == project.id).delete(
                    synchronize_session=False
                )

                # Clean up contacts
                session.query(IndividualContact).filter(
                    IndividualContact.project_id == project.id
                ).delete(synchronize_session=False)

                # Clean up project
                session.query(Project).filter(Project.id == project.id).delete(
                    synchronize_session=False
                )

                session.flush()
        except Exception as cleanup_error:
            # If cleanup fails, at least try to rollback
            session.rollback()
            print(f"Warning: Cleanup failed: {cleanup_error}")


def test_participant_based_filtering_edge_cases(session, user):
    """Test edge cases in participant-based filtering logic."""
    from dispatch.incident.models import Incident
    from dispatch.participant.models import Participant
    from dispatch.individual.models import IndividualContact
    from dispatch.enums import Visibility, UserRoles
    from dispatch.project.models import Project
    import uuid

    # Store original user email to restore later
    original_user_email = getattr(user, "email", "test@example.com")

    # Create unique identifiers to avoid conflicts
    timestamp = int(__import__("time").time() * 1000000)  # microsecond precision
    test_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"

    # Create unique test data
    project_name = f"test_edge_project_{test_id}"
    user_email = f"edge_test_user_{test_id}@example.com"
    other_email = f"edge_other_user_{test_id}@example.com"

    project = None  # Initialize to avoid unbound variable error

    # Ensure clean session state
    session.expire_all()

    try:
        # Create test project
        project = Project(name=project_name, default=False)
        session.add(project)
        session.flush()  # Use flush instead of commit to get ID within transaction

        # Create test individual contacts
        user_contact = IndividualContact(email=user_email, name="Test User", project_id=project.id)
        other_contact = IndividualContact(
            email=other_email, name="Other User", project_id=project.id
        )
        session.add_all([user_contact, other_contact])
        session.flush()

        # Test case: Multiple participants, user is one of them
        test_prefix = f"EDGE_TEST_{test_id}"
        restricted_incident = Incident(
            title=f"{test_prefix}_Multi_Participant_Restricted_Incident",
            description="Description",
            visibility=Visibility.restricted,
            project_id=project.id,
        )
        session.add(restricted_incident)
        session.flush()

        # Create multiple participants including our user
        user_participant = Participant(
            incident_id=restricted_incident.id, individual_contact_id=user_contact.id
        )
        other_participant = Participant(
            incident_id=restricted_incident.id, individual_contact_id=other_contact.id
        )
        session.add_all([user_participant, other_participant])
        session.flush()

        # Temporarily change user email for testing
        user.email = user_email

        # Test that user can see restricted incident even with multiple participants
        query = session.query(Incident).filter(Incident.project_id == project.id)
        filtered_query = restricted_incident_filter(query, user, UserRoles.member)
        results = filtered_query.all()

        assert len(results) == 1, f"Should see 1 incident, got {len(results)}"
        assert results[0].title == f"{test_prefix}_Multi_Participant_Restricted_Incident"

        # Test user not in participants cannot see restricted incident
        non_participant_email = f"nonparticipant_{test_id}@example.com"
        non_participant_user = user.__class__(email=non_participant_email)
        query = session.query(Incident).filter(Incident.project_id == project.id)
        filtered_query = restricted_incident_filter(query, non_participant_user, UserRoles.member)
        results = filtered_query.all()

        assert len(results) == 0, f"Non-participant should see 0 incidents, got {len(results)}"

    finally:
        # Always restore original user email
        user.email = original_user_email

        # Clean up test data in reverse order
        try:
            if project and hasattr(project, "id"):
                # Clean up participants
                session.query(Participant).filter(
                    Participant.incident_id.in_(
                        session.query(Incident.id).filter(Incident.project_id == project.id)
                    )
                ).delete(synchronize_session=False)

                # Clean up incidents
                session.query(Incident).filter(Incident.project_id == project.id).delete(
                    synchronize_session=False
                )

                # Clean up contacts
                session.query(IndividualContact).filter(
                    IndividualContact.project_id == project.id
                ).delete(synchronize_session=False)

                # Clean up project
                session.query(Project).filter(Project.id == project.id).delete(
                    synchronize_session=False
                )

                session.flush()
        except Exception as cleanup_error:
            # If cleanup fails, at least try to rollback
            session.rollback()
            print(f"Warning: Cleanup failed: {cleanup_error}")


# Simplified tests for basic role checks (keeping for backwards compatibility)
def test_restricted_incident_filter_member(session, user):
    """Tests incident filtering for member role."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.member
    )

    assert filtered_query is not None


def test_restricted_incident_filter_admin(session, user):
    """Tests incident filtering for admin role."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.admin
    )

    assert filtered_query is not None


def test_restricted_incident_filter_owner(session, user):
    """Tests incident filtering for owner role - should have unrestricted access."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.owner
    )

    assert filtered_query is not None


def test_restricted_incident_filter_manager(session, user):
    """Tests incident filtering for manager role - should have unrestricted access."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.manager
    )

    assert filtered_query is not None


def test_restricted_case_filter_member(session, user):
    """Tests case filtering for member role."""
    query = session.query(Case)
    filtered_query = restricted_case_filter(query=query, current_user=user, role=UserRoles.member)

    assert filtered_query is not None


def test_restricted_case_filter_admin(session, user):
    """Tests case filtering for admin role."""
    query = session.query(Case)
    filtered_query = restricted_case_filter(query=query, current_user=user, role=UserRoles.admin)

    assert filtered_query is not None


def test_restricted_case_filter_owner(session, user):
    """Tests case filtering for owner role - should have unrestricted access."""
    query = session.query(Case)
    filtered_query = restricted_case_filter(query=query, current_user=user, role=UserRoles.owner)

    assert filtered_query is not None


def test_restricted_case_filter_manager(session, user):
    """Tests case filtering for manager role - should have unrestricted access."""
    query = session.query(Case)
    filtered_query = restricted_case_filter(query=query, current_user=user, role=UserRoles.manager)

    assert filtered_query is not None


# Test apply_filters
def test_apply_filters_basic(session):
    """Tests basic filter application."""
    query = session.query(Incident)
    filter_spec = {"field": "title", "op": "==", "value": "Test"}

    filtered_query = apply_filters(query, filter_spec)
    assert filtered_query is not None


def test_apply_filters_complex(session):
    """Tests complex filter application with boolean operations."""
    query = session.query(Incident)
    filter_spec = {
        "and": [
            {"field": "title", "op": "==", "value": "Test"},
            {"field": "visibility", "op": "==", "value": "open"},
        ]
    }

    filtered_query = apply_filters(query, filter_spec)
    assert filtered_query is not None
