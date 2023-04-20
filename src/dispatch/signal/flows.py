from dispatch.auth.models import DispatchUser
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.entity import service as entity_service
from dispatch.project.models import Project
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstanceCreate
from dispatch.workflow import flows as workflow_flows


def signal_instance_create_flow(
    signal_instance_id: int,
    db_session: SessionLocal = None,
    current_user: DispatchUser = None,
):
    """Create flow used by the API."""
    signal_instance = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=signal_instance_id
    )

    entities = entity_service.find_entities(
        db_session=db_session,
        signal_instance=signal_instance,
        entity_types=signal_instance.signal.entity_types,
    )
    signal_instance.entities = entities
    db_session.commit()

    # we don't need to continue if a filter action took place
    if signal_service.filter_signal(db_session=db_session, signal_instance=signal_instance):
        return signal_instance

    if not signal_instance.signal.create_case:
        return signal_instance

    # create a case if not duplicate or snoozed
    if signal_instance.case_priority:
        case_priority = signal_instance.case_priority
    else:
        case_priority = signal_instance.signal.case_priority

    if signal_instance.case_type:
        case_type = signal_instance.case_type
    else:
        case_type = signal_instance.signal.case_type

    case_in = CaseCreate(
        title=signal_instance.signal.name,
        description=signal_instance.signal.description,
        case_priority=case_priority,
        project=signal_instance.project,
        case_type=case_type,
    )
    case = case_service.create(db_session=db_session, case_in=case_in, current_user=current_user)
    signal_instance.case = case

    db_session.commit()

    service_id = None
    if signal_instance.signal.oncall_service:
        service_id = signal_instance.signal.oncall_service.external_id

    conversation_target = None
    if signal_instance.signal.conversation_target:
        conversation_target = signal_instance.signal.conversation_target

    case_flows.case_new_create_flow(
        db_session=db_session,
        organization_slug=None,
        service_id=service_id,
        conversation_target=conversation_target,
        case_id=case.id,
    )

    # run workflows if not duplicate or snoozed
    if workflows := signal_instance.signal.workflows:
        for workflow in workflows:
            workflow_flows.signal_workflow_run_flow(
                current_user=current_user,
                db_session=db_session,
                signal_instance=signal_instance,
                workflow=workflow,
            )

    return signal_instance


def create_signal_instance(
    db_session: SessionLocal,
    project: Project,
    signal_instance_data: dict,
    current_user: DispatchUser = None,
):
    """Create flow used by the scheduler."""
    signal = signal_service.get_by_variant_or_external_id(
        db_session=db_session,
        project_id=project.id,
        external_id=signal_instance_data.get("id"),
        variant=signal_instance_data["variant"],
    )

    if not signal:
        raise Exception("No signal definition defined.")

    if not signal.enabled:
        raise Exception("Signal definition is not enabled.")

    signal_instance_in = SignalInstanceCreate(
        raw=signal_instance_data, signal=signal, project=signal.project
    )

    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )
    return signal_instance
