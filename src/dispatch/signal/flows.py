import logging

from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.auth import service as user_service
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.models import CaseCreate
from dispatch.entity import service as entity_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.signal import service as signal_service
from dispatch.signal import flows as signal_flows
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import SignalInstance, SignalInstanceCreate
from dispatch.workflow import flows as workflow_flows

log = logging.getLogger(__name__)


def signal_instance_create_flow(
    signal_instance_id: int,
    db_session: Session = None,
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
    case_in = CaseCreate(
        title=signal_instance.signal.name,
        description=signal_instance.signal.description,
        case_priority=signal_instance.signal.case_priority,
        project=signal_instance.project,
        case_type=signal_instance.signal.case_type,
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

    if signal_instance.signal.engagements and entities:
        signal_flows.engage_signal_identity(
            db_session=db_session,
            signal_instance=signal_instance,
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
    db_session: Session,
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


def engage_signal_identity(db_session: Session, signal_instance: SignalInstance) -> None:
    """Engage the signal identity."""

    users_to_engage = []
    engagements = signal_instance.signal.engagements
    for engagement in engagements:
        for entity in signal_instance.entities:
            if engagement.entity_type_id == entity.entity_type_id:
                try:
                    email = validate_email(entity.value, check_deliverability=False)
                    email = email.normalized
                except EmailNotValidError as e:
                    log.warning(
                        f"Discovered entity value in Signal {signal_instance.signal.id} that did not appear to be a valid email: {e}"
                    )
                else:
                    users_to_engage.append(
                        {
                            "user": entity.value,
                            "engagement": engagement,
                        }
                    )

    if not users_to_engage:
        log.warning(
            f"Engagement configured for Signal {signal_instance.signal.id} but no users found in instance: {signal_instance.id}."
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=signal_instance.case.project.id,
        plugin_type="conversation",
    )
    if not plugin:
        log.warning("No contact plugin is active.")
        return

    for reachout in users_to_engage:
        email = reachout.get("user")
        case_flows.case_add_or_reactivate_participant_flow(
            db_session=db_session,
            user_email=email,
            case_id=signal_instance.case.id,
            add_to_conversation=True,
        )

        user = user_service.get_or_create(
            db_session=db_session,
            organization=signal_instance.case.project.organization.slug,
            user_in=UserRegister(email=email),
        )

        response = plugin.instance.create_engagement_threaded(
            signal_instance=signal_instance,
            case=signal_instance.case,
            conversation_id=signal_instance.case.conversation.channel_id,
            thread_id=signal_instance.case.conversation.thread_id,
            user=user,
            engagement=reachout.get("engagement"),
            engagement_status=SignalEngagementStatus.new,
        )
        signal_instance.engagement_thread_ts = response.get("timestamp")
        db_session.commit()
