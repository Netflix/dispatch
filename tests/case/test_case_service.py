from dispatch.auth.models import DispatchUser
from dispatch.case.models import Case, CaseCreate, CaseRead


def test_get(session, case: Case):
    from dispatch.case.service import get

    t_case = get(db_session=session, case_id=case.id)
    assert t_case.id == case.id


def test_get_by_name(session, case: Case):
    from dispatch.case.service import get_by_name

    t_case = get_by_name(db_session=session, project_id=case.project.id, name=case.name)
    assert t_case.name == case.name


def test_get_by_name_or_raise():
    pass


def test_get_all(session, case: Case):
    from dispatch.case.service import get_all

    t_cases = get_all(db_session=session, project_id=case.project.id).all()
    assert t_cases


def test_get_all_by_status(session, new_case: Case):
    from dispatch.case.service import get_all_by_status
    from dispatch.case.enums import CaseStatus

    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        status=CaseStatus.new,
    )
    assert t_cases


def test_get_all_by_status_none(session, new_case: Case):
    from dispatch.case.service import get_all_by_status
    from dispatch.case.enums import CaseStatus

    t_cases = get_all_by_status(
        db_session=session,
        project_id=new_case.project.id,
        status=CaseStatus.closed,
    )
    assert not t_cases


def test_get_all_last_x_hours_by_status():
    pass


# TODO: (wshel) get CaseRead factory working
def test_create(session, case: Case, project):
    from dispatch.case.service import create as create_case
    from dispatch.case.type.service import create as create_type
    from dispatch.case.type.models import CaseTypeCreate

    name = "WOW"

    create_type_in = CaseTypeCreate(
        name=name,
        project=project,
    )
    create_type(db_session=session, case_type_in=create_type_in)

    case = create_case(db_session=session, case_in=case)
    assert case
