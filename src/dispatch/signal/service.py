import logging
import json
import uuid
from datetime import datetime, timedelta, timezone
from queue import Queue
import time
from typing import Optional, Union

from fastapi import HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import true

from dispatch.auth.models import DispatchUser
from dispatch.case.priority import service as case_priority_service
from dispatch.case.type import service as case_type_service
from dispatch.case.type.models import CaseType
from dispatch.database.core import get_organization_session, get_session
from dispatch.database.service import apply_filter_specific_joins, apply_filters
from dispatch.entity import service as entity_service
from dispatch.entity.models import Entity
from dispatch.entity_type import service as entity_type_service
from dispatch.entity_type.models import EntityScopeEnum
from dispatch.entity_type.models import EntityType
from dispatch.exceptions import NotFoundError
from dispatch.organization.service import get_all as get_all_organizations
from dispatch.project import service as project_service
from dispatch.service import service as service_service
from dispatch.signal.flows import signal_flows
from dispatch.tag import service as tag_service
from dispatch.workflow import service as workflow_service
from sqlalchemy.exc import IntegrityError

from .exceptions import (
    SignalNotDefinedException,
    SignalNotIdentifiedException,
)

from .models import (
    assoc_signal_entity_types,
    Signal,
    SignalCreate,
    SignalEngagement,
    SignalEngagementCreate,
    SignalEngagementRead,
    SignalFilter,
    SignalFilterAction,
    SignalFilterCreate,
    SignalFilterMode,
    SignalFilterRead,
    SignalFilterUpdate,
    SignalInstance,
    SignalInstanceCreate,
    SignalUpdate,
)

log = logging.getLogger(__name__)


def create_signal_engagement(
    *, db_session: Session, creator: DispatchUser, signal_engagement_in: SignalEngagementCreate
) -> SignalEngagement:
    """Creates a new signal filter."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_engagement_in.project
    )

    entity_type = entity_type_service.get(
        db_session=db_session, entity_type_id=signal_engagement_in.entity_type.id
    )

    signal_engagement = SignalEngagement(
        name=signal_engagement_in.name,
        description=signal_engagement_in.description,
        message=signal_engagement_in.message,
        require_mfa=signal_engagement_in.require_mfa,
        entity_type=entity_type,
        creator=creator,
        project=project,
    )
    db_session.add(signal_engagement)
    db_session.commit()
    return signal_engagement


def get_signal_engagement(
    *, db_session: Session, signal_engagement_id: int
) -> Optional[SignalEngagement]:
    """Gets a signal engagement by id."""
    return (
        db_session.query(SignalEngagement)
        .filter(SignalEngagement.id == signal_engagement_id)
        .one_or_none()
    )


def get_all_by_entity_type(*, db_session: Session, entity_type_id: int) -> list[SignalInstance]:
    """Fetches all signal instances associated with a given entity type."""
    return (
        db_session.query(SignalInstance)
        .join(SignalInstance.signal)
        .join(assoc_signal_entity_types)
        .join(EntityType)
        .filter(assoc_signal_entity_types.c.entity_type_id == entity_type_id)
        .all()
    )


def get_signal_engagement_by_name(
    *, db_session, project_id: int, name: str
) -> Optional[SignalEngagement]:
    """Gets a signal engagement by its name."""
    return (
        db_session.query(SignalEngagement)
        .filter(SignalEngagement.project_id == project_id)
        .filter(SignalEngagement.name == name)
        .first()
    )


def get_signal_engagement_by_name_or_raise(
    *, db_session: Session, project_id: int, signal_engagement_in=SignalEngagementRead
) -> SignalEngagement:
    signal_engagement = get_signal_engagement_by_name(
        db_session=db_session, project_id=project_id, name=signal_engagement_in.name
    )

    if not signal_engagement:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Signal Engagement not found.",
                        signal_engagement=signal_engagement_in.name,
                    ),
                    loc="signalEngagement",
                )
            ],
            model=SignalEngagementRead,
        )
    return signal_engagement


def create_signal_instance(*, db_session: Session, signal_instance_in: SignalInstanceCreate):
    """Creates a new signal instance."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=signal_instance_in.project
    )

    if not signal_instance_in.signal:
        external_id = signal_instance_in.external_id

        # this assumes the external_ids are uuids
        if not external_id:
            msg = "A detection external id must be provided in order to get the signal definition."
            raise SignalNotIdentifiedException(msg)

        signal_definition = (
            db_session.query(Signal).filter(Signal.external_id == external_id).one_or_none()
        )

    if not signal_definition:
        # we get the default signal definition
        signal_definition = get_default(
            db_session=db_session,
            project_id=project.id,
        )
        msg = f"Default signal definition used for signal instance with external id {external_id}"
        log.warn(msg)

    if not signal_definition:
        msg = f"No signal definition could be found by external id {external_id}, and no default exists."
        raise SignalNotDefinedException(msg)

    signal_instance_in.signal = signal_definition

    try:
        signal_instance = create_instance(
            db_session=db_session, signal_instance_in=signal_instance_in
        )
        signal_instance.signal = signal_definition
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        signal_instance = update_instance(
            db_session=db_session, signal_instance_in=signal_instance_in
        )
        # Note: we can do this because it's still relatively cheap, if we add more logic here
        # this will need to be moved to a background function (similar to case creation)
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
    return signal_instance


def create_signal_filter(
    *, db_session: Session, creator: DispatchUser, signal_filter_in: SignalFilterCreate
) -> SignalFilter:
    """Creates a new signal filter."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_filter_in.project
    )

    signal_filter = SignalFilter(
        **signal_filter_in.dict(
            exclude={
                "project",
            }
        ),
        creator=creator,
        project=project,
    )
    db_session.add(signal_filter)
    db_session.commit()
    return signal_filter


def update_signal_filter(
    *, db_session: Session, signal_filter: SignalFilter, signal_filter_in: SignalFilterUpdate
) -> SignalFilter:
    """Updates an existing signal filter."""

    signal_filter_data = signal_filter.dict()
    update_data = signal_filter_in.dict(
        skip_defaults=True,
        exclude={},
    )

    for field in signal_filter_data:
        if field in update_data:
            setattr(signal_filter, field, update_data[field])

    db_session.add(signal_filter)
    db_session.commit()
    return signal_filter


def delete_signal_filter(*, db_session: Session, signal_filter_id: int) -> int:
    """Deletes an existing signal filter."""
    signal_filter = db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_id).one()
    db_session.delete(signal_filter)
    db_session.commit()
    return signal_filter_id


def get_signal_filter_by_name_or_raise(
    *, db_session: Session, project_id: int, signal_filter_in=SignalFilterRead
) -> SignalFilter:
    signal_filter = get_signal_filter_by_name(
        db_session=db_session, project_id=project_id, name=signal_filter_in.name
    )

    if not signal_filter:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Signal Filter not found.", entity_type=signal_filter_in.name
                    ),
                    loc="signalFilter",
                )
            ],
            model=SignalFilterRead,
        )
    return signal_filter


def get_signal_filter_by_name(*, db_session, project_id: int, name: str) -> Optional[SignalFilter]:
    """Gets a signal filter by its name."""
    return (
        db_session.query(SignalFilter)
        .filter(SignalFilter.project_id == project_id)
        .filter(SignalFilter.name == name)
        .first()
    )


def get_signal_filter(*, db_session: Session, signal_filter_id: int) -> SignalFilter:
    """Gets a single signal filter."""
    return db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_id).one_or_none()


def get_signal_instance(
    *, db_session: Session, signal_instance_id: int | str
) -> Optional[SignalInstance]:
    """Gets a signal instance by its UUID."""
    return (
        db_session.query(SignalInstance)
        .filter(SignalInstance.id == signal_instance_id)
        .one_or_none()
    )


def get(*, db_session: Session, signal_id: Union[str, int]) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).one_or_none()


def get_default(*, db_session: Session, project_id: int) -> Optional[Signal]:
    """Gets the default signal definition."""
    return (
        db_session.query(Signal)
        .filter(Signal.project_id == project_id, Signal.default == true())
        .one_or_none()
    )


def get_by_primary_or_external_id(
    *, db_session: Session, signal_id: Union[str, int]
) -> Optional[Signal]:
    """Gets a signal by id or external_id."""
    if is_valid_uuid(signal_id):
        signal = db_session.query(Signal).filter(Signal.external_id == signal_id).one_or_none()
    else:
        signal = (
            db_session.query(Signal)
            .filter(or_(Signal.id == signal_id, Signal.external_id == signal_id))
            .one_or_none()
        )
    return signal


def get_by_variant_or_external_id(
    *, db_session: Session, project_id: int, external_id: str = None, variant: str = None
) -> Optional[Signal]:
    """Gets a signal by its variant or external id."""
    if variant:
        return (
            db_session.query(Signal)
            .filter(Signal.project_id == project_id, Signal.variant == variant)
            .one_or_none()
        )
    return (
        db_session.query(Signal)
        .filter(Signal.project_id == project_id, Signal.external_id == external_id)
        .one_or_none()
    )


def get_all_by_conversation_target(
    *, db_session: Session, project_id: int, conversation_target: str
) -> list[Signal]:
    """Gets all signals for a given conversation target (e.g. #conversation-channel)"""
    return (
        db_session.query(Signal)
        .join(CaseType)
        .filter(
            CaseType.project_id == project_id,
            CaseType.conversation_target == conversation_target,
            Signal.case_type_id == CaseType.id,
        )
        .all()
    )


def create(*, db_session: Session, signal_in: SignalCreate) -> Signal:
    """Creates a new signal."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_in.project
    )

    signal = Signal(
        **signal_in.dict(
            exclude={
                "case_priority",
                "case_type",
                "entity_types",
                "filters",
                "oncall_service",
                "project",
                "source",
                "tags",
                "workflows",
            }
        ),
        project=project,
    )

    tags = []
    for t in signal_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))
    signal.tags = tags

    entity_types = []
    for e in signal_in.entity_types:
        entity_type = entity_type_service.get(db_session=db_session, entity_type_id=e.id)
        entity_types.append(entity_type)

    signal.entity_types = entity_types

    engagements = []
    for eng in signal_in.engagements:
        signal_engagement = get_signal_engagement_by_name(
            db_session=db_session, project_id=project.id, signal_engagement_in=eng
        )
        engagements.append(signal_engagement)

    signal.engagements = engagements

    filters = []
    for f in signal_in.filters:
        signal_filter = get_signal_filter_by_name(
            db_session=db_session, project_id=project.id, signal_filter_in=f
        )
        filters.append(signal_filter)

    signal.filters = filters

    workflows = []
    for w in signal_in.workflows:
        workflow = workflow_service.get_by_name_or_raise(db_session=db_session, workflow_in=w)
        workflows.append(workflow)

    signal.workflows = workflows

    if signal_in.case_priority:
        case_priority = case_priority_service.get_by_name_or_default(
            db_session=db_session, project_id=project.id, case_priority_in=signal_in.case_priority
        )
        signal.case_priority = case_priority

    if signal_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=signal_in.oncall_service.id
        )
        signal.oncall_service = oncall_service

    if signal_in.case_type:
        case_type = case_type_service.get_by_name_or_default(
            db_session=db_session, project_id=project.id, case_type_in=signal_in.case_type
        )
        signal.case_type = case_type

    db_session.add(signal)
    db_session.commit()
    return signal


def update(*, db_session: Session, signal: Signal, signal_in: SignalUpdate) -> Signal:
    """Updates a signal."""
    signal_data = signal.dict()
    update_data = signal_in.dict(
        skip_defaults=True,
        exclude={
            "project",
            "case_type",
            "case_priority",
            "source",
            "engagements",
            "filters",
            "entity_types",
            "tags",
        },
    )

    for field in signal_data:
        if field in update_data:
            setattr(signal, field, update_data[field])

    if signal_in.tags:
        tags = []
        for t in signal_in.tags:
            tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))
        signal.tags = tags

    if signal_in.entity_types:
        entity_types = []
        for e in signal_in.entity_types:
            entity_type = entity_type_service.get(db_session=db_session, entity_type_id=e.id)
            entity_types.append(entity_type)

        signal.entity_types = entity_types

    if signal_in.engagements:
        engagements = []
        for eng in signal_in.engagements:
            signal_engagement = get_signal_engagement_by_name_or_raise(
                db_session=db_session, project_id=signal.project.id, signal_engagement_in=eng
            )
            engagements.append(signal_engagement)

        signal.engagements = engagements

    is_filters_updated = {filter.id for filter in signal.filters} != {
        filter.id for filter in signal_in.filters
    }

    if is_filters_updated:
        filters = []
        for f in signal_in.filters:
            signal_filter = get_signal_filter_by_name_or_raise(
                db_session=db_session, project_id=signal.project.id, signal_filter_in=f
            )
            filters.append(signal_filter)

        signal.filters = filters

    if signal_in.workflows:
        workflows = []
        for w in signal_in.workflows:
            workflow = workflow_service.get_by_name_or_raise(db_session=db_session, workflow_in=w)
            workflows.append(workflow)

        signal.workflows = workflows

    if signal_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=signal_in.oncall_service.id
        )
        signal.oncall_service = oncall_service

    if signal_in.case_priority:
        case_priority = case_priority_service.get_by_name_or_default(
            db_session=db_session,
            project_id=signal.project.id,
            case_priority_in=signal_in.case_priority,
        )
        signal.case_priority = case_priority

    if signal_in.case_type:
        case_type = case_type_service.get_by_name_or_default(
            db_session=db_session, project_id=signal.project.id, case_type_in=signal_in.case_type
        )
        signal.case_type = case_type

    db_session.commit()
    return signal


def delete(*, db_session: Session, signal_id: int):
    """Deletes a signal definition."""
    signal = db_session.query(Signal).filter(Signal.id == signal_id).one()
    db_session.delete(signal)
    db_session.commit()
    return signal_id


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val), version=4)
        return True
    except ValueError:
        return False


def create_instance(
    *, db_session: Session, signal_instance_in: SignalInstanceCreate
) -> SignalInstance:
    """Creates a new signal instance."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_instance_in.project
    )

    signal = get(db_session=db_session, signal_id=signal_instance_in.signal.id)

    # we round trip the raw data to json-ify date strings
    signal_instance = SignalInstance(
        **signal_instance_in.dict(
            exclude={
                "case",
                "case_priority",
                "case_type",
                "entities",
                "external_id",
                "project",
                "raw",
                "signal",
            }
        ),
        raw=json.loads(json.dumps(signal_instance_in.raw)),
        project=project,
        signal=signal,
    )

    # if the signal has an existing uuid we propgate it as our primary key
    if signal_instance_in.raw:
        if signal_instance_in.raw.get("id"):
            signal_instance.id = signal_instance_in.raw["id"]

    if signal_instance.id and not is_valid_uuid(signal_instance.id):
        msg = f"Invalid signal id format. Expecting UUID format. Received {signal_instance.id}."
        log.warn(msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": msg}],
        ) from None

    if signal_instance_in.case_priority:
        case_priority = case_priority_service.get_by_name_or_default(
            db_session=db_session,
            project_id=project.id,
            case_priority_in=signal_instance_in.case_priority,
        )
        signal_instance.case_priority = case_priority

    if signal_instance_in.case_type:
        case_type = case_type_service.get_by_name_or_default(
            db_session=db_session,
            project_id=project.id,
            case_type_in=signal_instance_in.case_type,
        )
        signal_instance.case_type = case_type

    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def update_instance(
    *, db_session: Session, signal_instance_in: SignalInstanceCreate
) -> SignalInstance:
    """Updates an existing signal instance."""
    if signal_instance_in.raw:
        if signal_instance_in.raw.get("id"):
            signal_instance_id = signal_instance_in.raw["id"]

    signal_instance = get_signal_instance(
        db_session=db_session, signal_instance_id=signal_instance_id
    )
    signal_instance.raw = json.loads(json.dumps(signal_instance_in.raw))

    db_session.commit()
    return signal_instance


def filter_snooze(*, db_session: Session, signal_instance: SignalInstance) -> SignalInstance:
    """Filters a signal instance for snoozing.

    Args:
        db_session (Session): Database session.
        signal_instance (SignalInstance): Signal instance to be filtered.

    Returns:
        SignalInstance: The filtered signal instance.
    """
    for f in signal_instance.signal.filters:
        if f.mode != SignalFilterMode.active:
            continue

        if f.action != SignalFilterAction.snooze:
            continue

        if f.expiration.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            continue

        query = db_session.query(SignalInstance).filter(
            SignalInstance.signal_id == signal_instance.signal_id
        )
        query = apply_filter_specific_joins(SignalInstance, f.expression, query)
        query = apply_filters(query, f.expression)
        # an expression is not required for snoozing, if absent we snooze regardless of entity
        if f.expression:
            instances = query.filter(SignalInstance.id == signal_instance.id).all()

            if instances:
                signal_instance.filter_action = SignalFilterAction.snooze
                break
        else:
            signal_instance.filter_action = SignalFilterAction.snooze
            break

    return signal_instance


def filter_dedup(*, db_session: Session, signal_instance: SignalInstance) -> SignalInstance:
    """Filters a signal instance for deduplication.

    Args:
        db_session (Session): Database session.
        signal_instance (SignalInstance): Signal instance to be filtered.

    Returns:
        SignalInstance: The filtered signal instance.
    """
    for f in signal_instance.signal.filters:
        if f.mode != SignalFilterMode.active:
            continue

        if f.action != SignalFilterAction.deduplicate:
            continue

        query = db_session.query(SignalInstance).filter(
            SignalInstance.signal_id == signal_instance.signal_id
        )
        query = apply_filter_specific_joins(SignalInstance, f.expression, query)
        query = apply_filters(query, f.expression)

        window = datetime.now(timezone.utc) - timedelta(minutes=f.window)
        query = query.filter(SignalInstance.created_at >= window)
        query = query.join(SignalInstance.entities).filter(
            Entity.id.in_([e.id for e in signal_instance.entities])
        )
        query = query.filter(SignalInstance.id != signal_instance.id)

        # get the earliest instance
        query = query.order_by(asc(SignalInstance.created_at))
        instances = query.all()

        if instances:
            # associate with existing case
            signal_instance.case_id = instances[0].case_id
            signal_instance.filter_action = SignalFilterAction.deduplicate
            break
    # apply default deduplication rule
    else:
        default_dedup_window = datetime.now(timezone.utc) - timedelta(hours=1)
        instance = (
            db_session.query(SignalInstance)
            .filter(
                SignalInstance.signal_id == signal_instance.signal_id,
                SignalInstance.created_at >= default_dedup_window,
                SignalInstance.id != signal_instance.id,
                SignalInstance.case_id.isnot(None),  # noqa
            )
            .with_entities(SignalInstance.case_id)
            .order_by(desc(SignalInstance.created_at))
            .first()
        )
        if instance:
            signal_instance.case_id = instance.case_id
            signal_instance.filter_action = SignalFilterAction.deduplicate

    return signal_instance


def filter_signal(*, db_session: Session, signal_instance: SignalInstance) -> bool:
    """
    Apply filter actions to the signal instance.

    The function first checks if the signal instance is snoozed. If not snoozed,
    it checks for a deduplication rule set on the signal instance. If no
    deduplication rule is set, a default deduplication rule is applied,
    grouping all signal instances together for a 1-hour window, regardless of
    the entities in the signal instance.

    Args:
        db_session (Session): Database session.
        signal_instance (SignalInstance): Signal instance to be filtered.

    Returns:
        bool: True if the signal instance is filtered, False otherwise.
    """
    filtered = False

    signal_instance = filter_snooze(db_session=db_session, signal_instance=signal_instance)

    # we only dedupe if we haven't been snoozed
    if not signal_instance.filter_action:
        signal_instance = filter_dedup(db_session=db_session, signal_instance=signal_instance)

    if not signal_instance.filter_action:
        signal_instance.filter_action = SignalFilterAction.none
    else:
        filtered = True

    db_session.commit()
    return filtered


MAX_SIGNAL_INSTANCES = 500
LOOP_DELAY = 60  # seconds


def get_unprocessed_signal_instance_ids(session: Session) -> list[int]:
    """Retrieves IDs of unprocessed signal instances from the database.

    Args:
        session (Session): The database session.

    Returns:
        list[int]: A list of signal instance IDs that need processing.
    """
    return (
        session.query(SignalInstance.id)
        .filter(SignalInstance.filter_action == None)  # noqa
        .filter(SignalInstance.case_id == None)  # noqa
        .order_by(SignalInstance.created_at.asc())
        .limit(MAX_SIGNAL_INSTANCES)
        .all()
    )


def process_signal(db_session: Session, signal_instance_id: int) -> None:
    """Processes a single signal instance.

    Args:
        db_session (Session): The database session.
        signal_instance_id (int): The ID of the signal instance to process.
    """
    try:
        signal_flows.signal_instance_create_flow(
            db_session=db_session,
            signal_instance_id=signal_instance_id,
        )
    except Exception as e:
        log.exception(f"Error processing signal instance {signal_instance_id}: {e}")


def process_organization_signals(organization_slug: str) -> None:
    """Processes all unprocessed signals for a given organization using a FIFO queue.

    Args:
        organization_slug (str): The slug of the organization whose signals need to be processed.
    """
    with get_organization_session(organization_slug) as db_session:
        signal_queue = Queue(maxsize=MAX_SIGNAL_INSTANCES)
        signal_instance_ids = get_unprocessed_signal_instance_ids(db_session)

        for signal_id in signal_instance_ids:
            signal_queue.put(signal_id)

        while not signal_queue.empty():
            signal_instance_id = signal_queue.get()
            process_signal(db_session, signal_instance_id)
            signal_queue.task_done()


def main_processing_loop() -> None:
    """Main processing loop that iterates through all organizations and processes their signals."""
    while True:
        try:
            with get_session() as session:
                organizations = get_all_organizations(db_session=session)
                for organization in organizations:
                    log.info(f"Processing signals in {organization.slug}")
                    try:
                        process_organization_signals(organization.slug)
                    except Exception as e:
                        log.exception(
                            f"Error processing signals for organization {organization.slug}: {e}"
                        )
        except Exception as e:
            log.exception(f"Error in main signal processing loop: {e}")
        finally:
            time.sleep(LOOP_DELAY)
