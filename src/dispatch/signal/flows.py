import logging
from datetime import timedelta

from cachetools import TTLCache
from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.models import CaseCreate
from dispatch.entity import service as entity_service
from dispatch.entity_type import service as entity_type_service
from dispatch.exceptions import DispatchException
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.service import flows as service_flows
from dispatch.signal import flows as signal_flows
from dispatch.signal import service as signal_service
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import SignalFilterAction, SignalInstance, SignalInstanceCreate
from dispatch.workflow import flows as workflow_flows
from dispatch.entity_type.models import EntityScopeEnum

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
    # fetch `all` entities that should be associated with all signal definitions
    entity_types = entity_type_service.get_all(
        db_session=db_session, scope=EntityScopeEnum.all
    ).all()
    entity_types = signal_instance.signal.entity_types + entity_types

    if entity_types:
        entities = entity_service.find_entities(
            db_session=db_session,
            signal_instance=signal_instance,
            entity_types=entity_types,
        )
        signal_instance.entities = entities
        db_session.commit()

    # we don't need to continue if a filter action took place
    if signal_service.filter_signal(
        db_session=db_session,
        signal_instance=signal_instance,
    ):
        # If a case and convesation exists and the signal was deduplicated,
        # we need to update the corresponding signal message
        if (
            signal_instance.case_id
            and signal_instance.case.conversation
            and _should_update_signal_message(signal_instance)
        ):
            update_signal_message(
                db_session=db_session,
                signal_instance=signal_instance,
            )
        return signal_instance

    # limited support for canary signals, just store the instance and return
    if signal_instance.canary:
        return signal_instance

    if not signal_instance.signal.create_case:
        return signal_instance

    # processes overrides for case creation
    # we want the following order of precedence:
    # 1. signal instance overrides
    # 2. signal definition overrides
    # 3. case type defaults

    if signal_instance.case_priority:
        case_priority = signal_instance.case_priority
    else:
        case_priority = signal_instance.signal.case_priority

    # if the signal has provided a case type use it's values instead of the definitions
    conversation_target = None
    if signal_instance.case_type:
        case_type = signal_instance.case_type
        if signal_instance.signal.conversation_target:
            conversation_target = signal_instance.case_type.conversation_target
    else:
        case_type = signal_instance.signal.case_type

        if signal_instance.signal.conversation_target:
            conversation_target = signal_instance.signal.conversation_target

    assignee = None
    if signal_instance.signal.oncall_service:
        email = service_flows.resolve_oncall(
            service=signal_instance.signal.oncall_service, db_session=db_session
        )
        assignee = {"individual": {"email": email}}

    # create a case if not duplicate or snoozed and case creation is enabled
    case_in = CaseCreate(
        title=signal_instance.signal.name,
        description=signal_instance.signal.description,
        case_priority=case_priority,
        project=signal_instance.project,
        case_type=case_type,
        assignee=assignee,
    )
    case = case_service.create(db_session=db_session, case_in=case_in, current_user=current_user)
    signal_instance.case = case

    db_session.commit()

    case_flows.case_new_create_flow(
        db_session=db_session,
        organization_slug=None,
        service_id=None,
        conversation_target=conversation_target,
        case_id=case.id,
        create_all_resources=False,
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
        raise DispatchException("No signal definition defined.")

    if not signal.enabled:
        raise DispatchException("Signal definition is not enabled.")

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
                    validated_email = validate_email(entity.value, check_deliverability=False)
                except EmailNotValidError as e:
                    log.warning(
                        f"Discovered entity value in Signal {signal_instance.signal.id} that did not appear to be a valid email: {e}"
                    )
                else:
                    users_to_engage.append(
                        {
                            "user": validated_email.email,
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
        log.warning("No conversation plugin is active.")
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


def update_signal_message(db_session: Session, signal_instance: SignalInstance) -> None:
    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=signal_instance.case.project.id,
        plugin_type="conversation",
    )
    if not plugin:
        log.warning("No conversation plugin is active.")
        return

    plugin.instance.update_signal_message(
        case_id=signal_instance.case_id,
        conversation_id=signal_instance.case.conversation.channel_id,
        db_session=db_session,
        thread_id=signal_instance.case.signal_thread_ts,
    )


_last_nonupdated_signal_cache = TTLCache(maxsize=4, ttl=60)


def _should_update_signal_message(signal_instance: SignalInstance) -> bool:
    """
    Determine if the signal message should be updated based on the filter action and time since the last update.
    """
    global _last_nonupdated_signal_cache

    case_id = str(signal_instance.case_id)

    if case_id not in _last_nonupdated_signal_cache:
        _last_nonupdated_signal_cache[case_id] = signal_instance
        return True

    last_nonupdated_signal = _last_nonupdated_signal_cache[case_id]
    time_since_last_update = signal_instance.created_at - last_nonupdated_signal.created_at

    if (
        signal_instance.filter_action == SignalFilterAction.deduplicate
        and signal_instance.case.signal_thread_ts  # noqa
        and time_since_last_update >= timedelta(seconds=5)  # noqa
    ):
        _last_nonupdated_signal_cache[case_id] = signal_instance
        return True
    else:
        return False
