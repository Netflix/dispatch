from dispatch.auth.models import DispatchUser
from dispatch.case.models import Case, CaseCreate, CaseUpdate
from dispatch.case.severity.models import CaseSeverity
from dispatch.case.priority.models import CasePriority
from dispatch.case.type.models import CaseType
from dispatch.case.enums import CaseStatus, CaseResolutionReason
from dispatch.enums import Visibility


def test_get(session, case: Case):
    from dispatch.case.service import get

    case_id = getattr(case, 'id', None)
    if case_id is None:
        raise AssertionError("case.id is None; cannot run test_get.")
    if hasattr(case_id, '__int__'):
        case_id = int(case_id)
    t_case = get(db_session=session, case_id=case_id)
    if t_case is not None and getattr(t_case, 'id', None) is not None:
        assert isinstance(t_case.id, int)
        assert t_case.id == case_id
    else:
        assert t_case is not None, "Returned case is None."


def test_get_by_name(session, case: Case):
    from dispatch.case.service import get_by_name

    case_name = getattr(case, 'name', None)
    if case_name is None:
        raise AssertionError("case.name is None; cannot run test_get_by_name.")
    if hasattr(case_name, '__str__'):
        case_name = str(case_name)
    t_case = get_by_name(db_session=session, project_id=case.project.id, name=case_name)
    if t_case is not None and getattr(t_case, 'name', None) is not None:
        assert isinstance(t_case.name, str)
        assert t_case.name == case_name
    else:
        assert t_case is not None, "Returned case is None."


def test_get_all(session, case: Case):
    from dispatch.case.service import get_all

    t_cases = list(get_all(db_session=session, project_id=case.project.id))
    assert t_cases is not None and len(t_cases) > 0, "No cases returned."


def test_get_all_by_status(session, new_case: Case):
    from dispatch.case.service import get_all_by_status
    from dispatch.case.enums import CaseStatus

    # Some case
    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        statuses=[CaseStatus.new],
    )
    assert t_cases

    # None case
    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        statuses=[CaseStatus.closed],
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
        resolution_reason=CaseResolutionReason.false_positive,
        status=CaseStatus.new,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
        assignee=participant,
        dedicated_channel=True,
        tags=[],
        event=False,
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
        resolution_reason=CaseResolutionReason.false_positive,
        status=CaseStatus.new,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
        assignee=participant,
        dedicated_channel=True,
        tags=[],
        event=False,
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
        resolution_reason=CaseResolutionReason.false_positive,
        status=CaseStatus.new,
        visibility=Visibility.open,
        case_type=case_type,
        case_severity=case_severity,
        case_priority=case_priority,
        reporter=participant,
        project=project,
        assignee=participant,
        dedicated_channel=False,
        tags=[],
        event=False,
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

    case_in = CaseUpdate(
        title="XXX",
        description="YYY",
        resolution="True Positive",
        resolution_reason=CaseResolutionReason.user_acknowledge,
        status=CaseStatus.closed,
        visibility=Visibility.restricted,
        assignee=case.assignee,
        case_priority=case.case_priority,
        case_severity=case.case_severity,
        case_type=case.case_type,
        tags=[],
        reporter=case.reporter,
    )

    case_out = update_case(
        db_session=session, case=case, case_in=case_in, current_user=current_user
    )
    if case_out is not None:
        assert getattr(case_out, 'title', None) == "XXX"
        assert getattr(case_out, 'description', None) == "YYY"
        assert getattr(case_out, 'resolution', None) == "True Positive"
        assert getattr(case_out, 'status', None) == CaseStatus.closed
        assert getattr(case_out, 'visibility', None) == Visibility.restricted


def test_delete(session, case: Case):
    from dispatch.case.service import delete as case_delete
    from dispatch.case.service import get as case_get

    case_id = getattr(case, 'id', None)
    if case_id is None:
        raise AssertionError("case.id is None; cannot run test_delete.")
    if hasattr(case_id, '__int__'):
        case_id = int(case_id)
    case_delete(
        db_session=session,
        case_id=case_id,
    )

    t_case = case_get(db_session=session, case_id=case_id)
    assert not t_case
