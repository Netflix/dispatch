def test_get(session, case_type):
    from dispatch.case.type.service import get

    t_case_type = get(db_session=session, case_type_id=case_type.id)
    assert t_case_type.id == case_type.id


def test_get_by_name(session, case_type):
    from dispatch.case.type.service import get_by_name

    t_case_type = get_by_name(
        db_session=session, project_id=case_type.project.id, name=case_type.name
    )
    assert t_case_type.name == case_type.name


def test_get_all(session, project, case_types):
    from dispatch.case.type.service import get_all

    t_case_types = get_all(db_session=session, project_id=case_types[0].project.id).all()
    assert t_case_types


def test_create(session, project, document):
    from dispatch.case.type.service import create
    from dispatch.case.type.models import CaseTypeCreate

    name = "XXX"

    case_type_in = CaseTypeCreate(
        name=name,
        template_document=document,
        project=project,
    )

    case_type = create(db_session=session, case_type_in=case_type_in)
    assert case_type


def test_update(session, case_type):
    from dispatch.case.type.service import update
    from dispatch.case.type.models import CaseTypeUpdate

    name = "Updated case type name"

    case_type_in = CaseTypeUpdate(name=name)
    case_type = update(
        db_session=session,
        case_type=case_type,
        case_type_in=case_type_in,
    )
    assert case_type.name == name


def test_update_cost_model(session, case, case_type, cost_model, case_cost, case_cost_type):
    """Updating the cost model field should immediately update the case cost of all cases with this case type."""
    from dispatch.case.models import CaseStatus
    from dispatch.case.type.service import update
    from dispatch.case_cost import service as case_cost_service
    from dispatch.case_cost_type import service as case_cost_type_service
    from dispatch.case.type.models import CaseTypeUpdate
    import datetime

    name = "Updated case type name"

    case_type_in = CaseTypeUpdate(name=name)
    current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    # Initial setup.
    case.status = CaseStatus.new
    case.case_type = case_type
    case.project = case_type.project

    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False

    case_cost_type.project = case_type.project
    case_cost_type.default = True

    case_cost.project = case_type.project
    case_cost.case_id = case.id
    case_cost.case_cost_type = case_cost_type

    cost_model.project = case_type.project
    case_type_in.cost_model = cost_model

    case_type = update(
        db_session=session,
        case_type=case_type,
        case_type_in=case_type_in,
    )
    assert case_type.name == name

    # Assert that the case cost was updated
    case_cost = case_cost_service.get_default_case_response_cost(db_session=session, case=case)
    assert case_cost
    assert case_cost.updated_at > current_time


def test_delete(session, case_type):
    from dispatch.case.type.service import delete, get

    delete(db_session=session, case_type_id=case_type.id)
    assert not get(db_session=session, case_type_id=case_type.id)
