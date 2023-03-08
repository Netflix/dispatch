from dispatch.auth.models import DispatchUser
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.entity import service as entity_service
from dispatch.project.models import Project
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstanceCreate


def create_signal_instance(
    db_session: SessionLocal,
    project: Project,
    signal_instance_data: dict,
    current_user: DispatchUser = None,
):
    """Creates a signal and a case if necessary."""
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

    signal_instance_in = SignalInstanceCreate(raw=signal_instance_data, project=signal.project)

    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )

    entities = entity_service.find_entities(
        db_session=db_session,
        signal_instance=signal_instance,
        entity_types=signal.entity_types,
    )
    signal_instance.entities = entities

    signal_instance.signal = signal
    db_session.commit()

    if signal_service.apply_filter_actions(db_session=db_session, signal_instance=signal_instance):
        # create a case if not duplicate or snoozed
        case_in = CaseCreate(
            title=signal.name,
            description=signal.description,
            case_priority=signal.case_priority,
            project=project,
            case_type=signal.case_type,
        )
        case = case_service.create(
            db_session=db_session, case_in=case_in, current_user=current_user
        )

        signal_instance.case = case
        db_session.commit()
        return case_flows.case_new_create_flow(
            db_session=db_session, organization_slug=None, case_id=case.id
        )
