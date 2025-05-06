from datetime import datetime, timezone

def test_get(session, case_cost_type):
    from dispatch.case_cost_type.service import get

    t_case_cost_type = get(db_session=session, case_cost_type_id=case_cost_type.id)
    assert t_case_cost_type.id == case_cost_type.id


def test_get_all(session, case_cost_types):
    from dispatch.case_cost_type.service import get_all

    t_case_cost_types = get_all(db_session=session)
    assert t_case_cost_types


def test_create(session, project):
    from dispatch.case_cost_type.service import create
    from dispatch.case_cost_type.models import CaseCostTypeCreate

    name = "name"
    description = "description"
    category = "category"
    details = {}
    default = True
    editable = False

    case_cost_type_in = CaseCostTypeCreate(
        name=name,
        description=description,
        category=category,
        details=details,
        default=default,
        editable=editable,
        project=project,
        created_at=datetime.now(timezone.utc),
    )
    case_cost_type = create(db_session=session, case_cost_type_in=case_cost_type_in)
    assert case_cost_type


def test_update(session, case_cost_type):
    from dispatch.case_cost_type.service import update
    from dispatch.case_cost_type.models import CaseCostTypeUpdate

    name = "Updated name"

    case_cost_type_in = CaseCostTypeUpdate(
        name=name,
        created_at=case_cost_type.created_at,
        editable=case_cost_type.editable,
    )
    case_cost_type = update(
        db_session=session,
        case_cost_type=case_cost_type,
        case_cost_type_in=case_cost_type_in,
    )
    assert case_cost_type.name == name


def test_delete(session, case_cost_type):
    from dispatch.case_cost_type.service import delete, get

    delete(db_session=session, case_cost_type_id=case_cost_type.id)
    assert not get(db_session=session, case_cost_type_id=case_cost_type.id)
