from dispatch.auth.models import DispatchUser
from dispatch.case.models import Case, CaseCreate, CaseUpdate
from dispatch.case.severity.models import CaseSeverity
from dispatch.case.priority.models import CasePriority
from dispatch.case.type.models import CaseType


def test_get(session, case: Case):
    from dispatch.case.service import get

    t_case = get(db_session=session, case_id=case.id)
    assert t_case.id == case.id


def test_get_by_name(session, case: Case):
    from dispatch.case.service import get_by_name

    t_case = get_by_name(db_session=session, project_id=case.project.id, name=case.name)
    assert t_case.name == case.name


def test_get_all(session, case: Case):
    from dispatch.case.service import get_all

    t_cases = get_all(db_session=session, project_id=case.project.id).all()
    assert t_cases


def test_get_all_by_status(session, new_case: Case):
    from dispatch.case.service import get_all_by_status
    from dispatch.case.enums import CaseStatus

    # Some case
    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        status=CaseStatus.new,
    )
    assert t_cases

    # None case
    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        status=CaseStatus.closed,
    )
    assert not t_cases


def test_create(session, participant, case_type, case_severity, case_priority, project, user):
    from dispatch.case.service import create as create_case
    from dispatch.enums import Visibility

    case_type.project = project
    case_severity.project = project
    case_priority.project = project
    session.add(case_type)
    session.add(case_severity)
    session.add(case_priority)
    session.commit()

    # No assignee, No oncall_service, resolves current_user to assignee

    case_in = CaseCreate(
        title="A",
        description="B",
        resolution=None,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
    )
    case_out = create_case(db_session=session, case_in=case_in, current_user=user)
    assert case_out
    assert case_out.assignee.individual.email == user.email


def test_create__no_conversation_target(
    session, participant, case_type, case_severity, case_priority, project, user
):
    """Assert that a case with a dedicated channel can be created without a conversation_target."""
    from dispatch.case.service import create as create_case
    from dispatch.enums import Visibility

    case_type.project = project
    case_type.conversation_target = None
    case_severity.project = project
    case_priority.project = project
    session.add(case_type)
    session.add(case_severity)
    session.add(case_priority)
    session.commit()

    # No assignee, No oncall_service, resolves current_user to assignee

    case_in = CaseCreate(
        title="A",
        description="B",
        resolution=None,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
        dedicated_channel=True,
    )

    assert create_case(db_session=session, case_in=case_in, current_user=user)


def test_create__fails_with_no_conversation_target(
    session, participant, case_type, case_severity, case_priority, project, user
):
    """Assert that a case without a dedicated channel cannot be created without a conversation_target."""
    from dispatch.case.service import create as create_case
    from dispatch.enums import Visibility

    case_type.project = project
    case_type.conversation_target = None
    case_severity.project = project
    case_priority.project = project
    session.add(case_type)
    session.add(case_severity)
    session.add(case_priority)
    session.commit()

    # No assignee, No oncall_service, resolves current_user to assignee

    case_in = CaseCreate(
        title="A",
        description="B",
        resolution=None,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
    )
    try:
        case_in = create_case(db_session=session, case_in=case_in, current_user=user)
        assert not case_in
    except Exception as e:
        assert "conversation target" in str(e)


def test_update(session, case: Case, project):
    from dispatch.case.service import update as update_case
    from dispatch.case.enums import CaseStatus
    from dispatch.enums import Visibility

    current_user = DispatchUser(email="test@netflix.com")
    case.case_type = CaseType(name="Test", project=project)
    case.case_severity = CaseSeverity(name="Low", project=project)
    case.case_priority = CasePriority(name="Low", project=project)
    case.project = project
    case.visibility = Visibility.open

    case_in = CaseUpdate(
        title="XXX",
        description="YYY",
        resolution="True Positive",
        status=CaseStatus.closed,
        visibility=Visibility.restricted,
    )

    case_out = update_case(
        db_session=session, case=case, case_in=case_in, current_user=current_user
    )
    assert case_out.title == "XXX"
    assert case_out.description == "YYY"
    assert case_out.resolution == "True Positive"
    assert case_out.status == CaseStatus.closed
    assert case_out.visibility == Visibility.restricted


def test_delete(session, case: Case):
    from dispatch.case.service import delete as case_delete
    from dispatch.case.service import get as case_get

    case_delete(
        db_session=session,
        case_id=case.id,
    )

    t_case = case_get(db_session=session, case_id=case.id)
    assert not t_case
