import logging
import time
from datetime import timedelta

from cachetools import TTLCache
from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import CaseCreate
from dispatch.database.core import get_organization_session, get_session
from dispatch.entity import service as entity_service
from dispatch.entity_type import service as entity_type_service
from dispatch.entity_type.models import EntityScopeEnum
from dispatch.enums import Visibility
from dispatch.exceptions import DispatchException
from dispatch.individual.models import IndividualContactRead
from dispatch.messaging.strings import CASE_RESOLUTION_DEFAULT
from dispatch.organization.service import get_all as get_all_organizations
from dispatch.participant.models import ParticipantUpdate
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.service import flows as service_flows
from dispatch.signal import flows as signal_flows
from dispatch.signal import service as signal_service
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import SignalFilterAction, SignalInstance, SignalInstanceCreate
from dispatch.workflow import flows as workflow_flows

log = logging.getLogger(__name__)

# Constants for signal processing
BATCH_SIZE = 50  # Process signals in batches of 50
LOOP_DELAY = 60  # seconds
MAX_PROCESSING_TIME = (
    300  # Maximum time to process signals before refreshing organization list (5 minutes)
)


def signal_instance_create_flow(
    signal_instance_id: int,
    db_session: Session = None,
    current_user: DispatchUser = None,
):
    """Create flow used by the API."""
    signal_instance = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=signal_instance_id
    )
    if signal_instance is None:
        log.error("signal_instance is None for id: %%s", signal_instance_id)
        return None
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
        # If a case and conversation exists and the signal was deduplicated,
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

    # set signal instance attributes with priority given to signal instance specification, then signal, then case type.
    if signal_instance.case_type:
        case_type = signal_instance.case_type
    else:
        case_type = signal_instance.signal.case_type

    if signal_instance.case_priority:
        case_priority = signal_instance.case_priority
    else:
        case_priority = signal_instance.signal.case_priority

    if signal_instance.oncall_service:
        oncall_service = signal_instance.oncall_service
    elif signal_instance.signal.oncall_service:
        oncall_service = signal_instance.signal.oncall_service
    elif case_type.oncall_service:
        oncall_service = case_type.oncall_service
    else:
        oncall_service = None

    if signal_instance.conversation_target:
        conversation_target = signal_instance.conversation_target
    elif signal_instance.signal.conversation_target:
        conversation_target = signal_instance.signal.conversation_target
    elif case_type.conversation_target:
        conversation_target = case_type.conversation_target
    else:
        conversation_target = None

    assignee = None
    if oncall_service:
        email = service_flows.resolve_oncall(service=oncall_service, db_session=db_session)
        if email:
            assignee = ParticipantUpdate(
                individual=IndividualContactRead(
                    id=1,
                    email=str(email),
                ),
                location=None,
                team=None,
                department=None,
                added_reason=None,
            )

    # create a case if not duplicate or snoozed and case creation is enabled
    case_severity = (
        getattr(signal_instance, "case_severity", None)
        or getattr(signal_instance.signal, "case_severity", None)
        or getattr(case_type, "case_severity", None)
    )

    reporter = None
    if current_user and hasattr(current_user, "email"):
        reporter = ParticipantUpdate(
            individual=IndividualContactRead(
                id=1,
                email=str(current_user.email),
            ),
            location=None,
            team=None,
            department=None,
            added_reason=None,
        )

    case_in = CaseCreate(
        title=signal_instance.signal.name,
        description=signal_instance.signal.description,
        resolution=CASE_RESOLUTION_DEFAULT,
        resolution_reason=None,
        status=CaseStatus.new,
        visibility=Visibility.open,
        case_priority=case_priority,
        case_severity=case_severity,
        project=signal_instance.project,
        case_type=case_type,
        assignee=assignee,
        dedicated_channel=False,
        reporter=reporter,
    )
    case = case_service.create(db_session=db_session, case_in=case_in, current_user=current_user)
    signal_instance.case = case

    db_session.commit()

    # Ensure valid types for case_new_create_flow arguments
    org_slug = None
    svc_id = None
    conv_target = conversation_target if isinstance(conversation_target, str) else None
    case_flows.case_new_create_flow(
        db_session=db_session,
        organization_slug=org_slug,
        service_id=svc_id,
        conversation_target=conv_target,
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
        **signal_instance_data,
        raw=signal_instance_data,
        signal=signal,
        project=signal.project,
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
                        f"A user subject included in a signal for {signal_instance.signal.name} (id: {signal_instance.signal.id}) contains an invalid email address: {e}. Investigate why this detection included a user subject with an invalid email in the signal."
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
            f"Engagement configured for signal {signal_instance.signal.name} (id: {signal_instance.signal.id}), but no users found in instance with id {signal_instance.id}."
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


# Cache structure: {case_id: {"created_at": datetime, "filter_action": SignalFilterAction}}
_last_nonupdated_signal_cache = TTLCache(maxsize=4, ttl=60)


def _should_update_signal_message(signal_instance: SignalInstance) -> bool:
    """
    Determine if the signal message should be updated based on the filter action and time since the last update.
    """
    global _last_nonupdated_signal_cache

    case_id = str(signal_instance.case_id)

    if case_id not in _last_nonupdated_signal_cache:
        # Store only the necessary data, not the entire object
        _last_nonupdated_signal_cache[case_id] = {
            "created_at": signal_instance.created_at,
            "filter_action": signal_instance.filter_action,
        }
        return True

    last_cached_data = _last_nonupdated_signal_cache[case_id]
    time_since_last_update = signal_instance.created_at - last_cached_data["created_at"]

    if (
        signal_instance.filter_action == SignalFilterAction.deduplicate
        and signal_instance.case.signal_thread_ts  # noqa
        and time_since_last_update >= timedelta(seconds=5)  # noqa
    ):
        # Update the cache with the new data
        _last_nonupdated_signal_cache[case_id] = {
            "created_at": signal_instance.created_at,
            "filter_action": signal_instance.filter_action,
        }
        return True
    else:
        return False


def process_signal_batch(db_session: Session, signal_instance_ids: list[int]) -> None:
    """Process a batch of signal instances.

    Args:
        db_session (Session): The database session.
        signal_instance_ids (list[int]): List of signal instance IDs to process.
    """
    for signal_instance_id in signal_instance_ids:
        try:
            signal_flows.signal_instance_create_flow(
                db_session=db_session,
                signal_instance_id=signal_instance_id,
            )
            # Commit after each successful processing to ensure progress is saved
            db_session.commit()
        except Exception as e:
            log.exception(f"Error processing signal instance {signal_instance_id}: {e}")
            # Ensure transaction is rolled back on error
            db_session.rollback()


def process_organization_signals(organization_slug: str) -> None:
    """Processes all unprocessed signals for a given organization using batched processing.

    Args:
        organization_slug (str): The slug of the organization whose signals need to be processed.
    """
    try:
        with get_organization_session(organization_slug) as db_session:
            # Get unprocessed signal IDs
            signal_instance_ids = signal_service.get_unprocessed_signal_instance_ids(db_session)

            if not signal_instance_ids:
                log.debug(f"No unprocessed signals found for organization {organization_slug}")
                return

            log.info(
                f"Processing {len(signal_instance_ids)} signals for organization {organization_slug}"
            )

            # Process signals in batches
            for i in range(0, len(signal_instance_ids), BATCH_SIZE):
                batch = signal_instance_ids[i : i + BATCH_SIZE]
                process_signal_batch(db_session, batch)

                # Log progress for large batches
                if len(signal_instance_ids) > BATCH_SIZE:
                    log.info(
                        f"Processed {min(i + BATCH_SIZE, len(signal_instance_ids))}/{len(signal_instance_ids)} signals for {organization_slug}"
                    )
    except SQLAlchemyError as e:
        log.exception(f"Database error while processing signals for {organization_slug}: {e}")
    except Exception as e:
        log.exception(f"Error processing signals for organization {organization_slug}: {e}")


def main_processing_loop() -> None:
    """Main processing loop that iterates through all organizations and processes their signals.

    Uses time-based batching to ensure the organization list is refreshed periodically.
    """
    while True:
        try:
            # Get organizations in a dedicated session that will be properly closed
            organizations = []
            with get_session() as session:
                organizations = list(get_all_organizations(db_session=session))

            if not organizations:
                log.warning("No organizations found to process signals for")
                time.sleep(LOOP_DELAY)
                continue

            start_time = time.time()

            # Process each organization with its own session
            for organization in organizations:
                # Check if we've been processing for too long and should refresh org list
                if time.time() - start_time > MAX_PROCESSING_TIME:
                    log.info("Processing time limit reached, refreshing organization list")
                    break

                log.info(f"Processing signals for organization {organization.slug}")
                process_organization_signals(organization.slug)

        except Exception as e:
            log.exception(f"Error in main signal processing loop: {e}")
        finally:
            time.sleep(LOOP_DELAY)
