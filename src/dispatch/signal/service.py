import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from collections import defaultdict

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import asc, desc, or_, func, and_, select, cast
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import true
from sqlalchemy.dialects.postgresql import JSONB

from dispatch.auth.models import DispatchUser
from dispatch.case.models import Case
from dispatch.case.priority import service as case_priority_service
from dispatch.case.type import service as case_type_service
from dispatch.case.type.models import CaseType
from dispatch.database.service import apply_filter_specific_joins, apply_filters
from dispatch.entity.models import Entity
from dispatch.entity_type import service as entity_type_service
from dispatch.entity_type.models import EntityType
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.individual import service as individual_service
from dispatch.project import service as project_service
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.workflow import service as workflow_service

from .exceptions import (
    SignalNotDefinedException,
    SignalNotIdentifiedException,
)
from .models import (
    assoc_signal_instance_entities,
    Signal,
    SignalCreate,
    SignalEngagement,
    SignalEngagementCreate,
    SignalEngagementRead,
    SignalEngagementUpdate,
    SignalFilter,
    SignalFilterAction,
    SignalFilterCreate,
    SignalFilterMode,
    SignalFilterRead,
    SignalFilterUpdate,
    SignalInstance,
    SignalInstanceCreate,
    SignalStats,
    SignalUpdate,
    assoc_signal_entity_types,
)

log = logging.getLogger(__name__)


def get_signal_engagement(
    *, db_session: Session, signal_engagement_id: int
) -> Optional[SignalEngagement]:
    """Gets a signal engagement by id."""
    return (
        db_session.query(SignalEngagement)
        .filter(SignalEngagement.id == signal_engagement_id)
        .one_or_none()
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
    *, db_session: Session, project_id: int, signal_engagement_in: SignalEngagementRead
) -> SignalEngagement:
    """Gets a signal engagement by its name or raises an error if not found."""
    signal_engagement = get_signal_engagement_by_name(
        db_session=db_session, project_id=project_id, name=signal_engagement_in.name
    )

    if not signal_engagement:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Signal engagement not found.",
                        signal_engagement=signal_engagement_in.name,
                    ),
                    loc="signalEngagement",
                )
            ],
            model=SignalEngagementRead,
        )
    return signal_engagement


def create_signal_engagement(
    *, db_session: Session, creator: DispatchUser, signal_engagement_in: SignalEngagementCreate
) -> SignalEngagement:
    """Creates a new signal engagement."""
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


def update_signal_engagement(
    *,
    db_session: Session,
    signal_engagement: SignalEngagement,
    signal_engagement_in: SignalEngagementUpdate,
) -> SignalEngagement:
    """Updates an existing signal engagement."""
    signal_engagement_data = signal_engagement.dict()
    update_data = signal_engagement_in.dict(
        skip_defaults=True,
        exclude={},
    )

    for field in signal_engagement_data:
        if field in update_data:
            setattr(signal_engagement, field, update_data[field])

    db_session.add(signal_engagement)
    db_session.commit()
    return signal_engagement


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

    signal_instance = create_instance(db_session=db_session, signal_instance_in=signal_instance_in)
    signal_instance.signal = signal_definition
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
    *, db_session: Session, project_id: int, signal_filter_in: SignalFilterRead
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


excluded_attributes = {
    "case_priority",
    "case_type",
    "engagements",
    "entity_types",
    "filters",
    "oncall_service",
    "project",
    "source",
    "tags",
    "workflows",
}


def create(
    *, db_session: Session, signal_in: SignalCreate, user: DispatchUser | None = None
) -> Signal:
    """Creates a new signal."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_in.project
    )

    updates = defaultdict(list)

    signal = Signal(
        **signal_in.dict(exclude=excluded_attributes),
        project=project,
    )

    for field in signal_in.dict(exclude=excluded_attributes):
        attr = getattr(signal, field)
        if attr and not isinstance(attr, datetime):
            updates[field] = attr

    tags = []
    for t in signal_in.tags:
        tag = tag_service.get_or_create(db_session=db_session, tag_in=t)
        tags.append(tag)
        updates["tags"].append(f"{tag.tag_type.name}/{tag.name}")
    signal.tags = tags

    entity_types = []
    for e in signal_in.entity_types:
        entity_type = entity_type_service.get(db_session=db_session, entity_type_id=e.id)
        entity_types.append(entity_type)
        updates["entity_types"].append(entity_type.name)
    signal.entity_types = entity_types

    engagements = []
    for signal_engagement_in in signal_in.engagements:
        signal_engagement = get_signal_engagement_by_name(
            db_session=db_session, project_id=project.id, name=signal_engagement_in.name
        )
        engagements.append(signal_engagement)
        updates["engagements"].append(signal_engagement.name)
    signal.engagements = engagements

    filters = []
    for f in signal_in.filters:
        signal_filter = get_signal_filter_by_name(
            db_session=db_session, project_id=project.id, name=f.name
        )
        filters.append(signal_filter)
        updates["filters"].append(signal_filter.name)
    signal.filters = filters

    workflows = []
    for w in signal_in.workflows:
        workflow = workflow_service.get_by_name_or_raise(db_session=db_session, workflow_in=w)
        workflows.append(workflow)
        updates["workflows"].append(workflow.name)
    signal.workflows = workflows

    if signal_in.case_priority:
        case_priority = case_priority_service.get_by_name_or_default(
            db_session=db_session, project_id=project.id, case_priority_in=signal_in.case_priority
        )
        signal.case_priority = case_priority
        updates["case_priority"] = case_priority.name

    if signal_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=signal_in.oncall_service.id
        )
        signal.oncall_service = oncall_service
        updates["oncall_service"] = oncall_service.name

    if signal_in.case_type:
        case_type = case_type_service.get_by_name_or_default(
            db_session=db_session, project_id=project.id, case_type_in=signal_in.case_type
        )
        signal.case_type = case_type
        updates["case_type"] = case_type.name

    db_session.add(signal)
    db_session.commit()

    if user:
        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=user.email, project_id=signal.project.id
        )
    else:
        individual = None

    event_service.log_signal_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Signal created",
        details=updates,
        individual_id=individual.id if individual else None,
        dispatch_user_id=user.id if user else None,
        signal_id=signal.id,
        owner=user.email if user else None,
        pinned=True,
    )
    return signal


def update(
    *,
    db_session: Session,
    signal: Signal,
    signal_in: SignalUpdate,
    user: DispatchUser | None = None,
) -> Signal:
    """Updates a signal."""
    signal_data = signal.dict()
    update_data = signal_in.dict(
        skip_defaults=True,
        exclude=excluded_attributes,
    )

    updates = defaultdict(list)

    for field in signal_data:
        if field in update_data:
            if signal_data[field] != update_data[field] and not isinstance(
                signal_data[field], datetime
            ):
                updates[field] = f"{signal_data[field]} -> {update_data[field]}"
            setattr(signal, field, update_data[field])

    if signal_in.tags:
        tags = []
        for t in signal_in.tags:
            tag = tag_service.get_or_create(db_session=db_session, tag_in=t)
            if tag not in signal.tags:
                updates["tags-added"].append(f"{tag.tag_type.name}/{tag.name}")
            tags.append(tag)
        for t in signal.tags:
            if t not in tags:
                updates["tags-removed"].append(f"{t.tag_type.name}/{t.name}")
        signal.tags = tags

    if signal_in.entity_types:
        entity_types = []
        for e in signal_in.entity_types:
            entity_type = entity_type_service.get(db_session=db_session, entity_type_id=e.id)
            if entity_type not in signal.entity_types:
                updates["entity_types-added"].append(entity_type.name)
            entity_types.append(entity_type)
        for et in signal.entity_types:
            if et not in entity_types:
                updates["entity_types-removed"].append(et.name)
        signal.entity_types = entity_types

    if signal_in.engagements:
        engagements = []
        for signal_engagement_in in signal_in.engagements:
            signal_engagement = get_signal_engagement_by_name_or_raise(
                db_session=db_session,
                project_id=signal.project.id,
                signal_engagement_in=signal_engagement_in,
            )
            if signal_engagement not in signal.engagements:
                updates["engagements-added"].append(signal_engagement.name)
            engagements.append(signal_engagement)
        for se in signal.engagements:
            if se not in engagements:
                updates["engagements-removed"].append(se.name)
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
            if signal_filter not in signal.filters:
                updates["filters-added"].append(signal_filter.name)
            filters.append(signal_filter)
        for f in signal.filters:
            if f not in filters:
                updates["filters-removed"].append(f.name)
        signal.filters = filters

    if signal_in.workflows:
        workflows = []
        for w in signal_in.workflows:
            workflow = workflow_service.get_by_name_or_raise(db_session=db_session, workflow_in=w)
            if workflow not in signal.workflows:
                updates["workflows-added"].append(workflow.name)
            workflows.append(workflow)
        for w in signal.workflows:
            if w not in workflows:
                updates["workflows-removed"].append(w.name)
        signal.workflows = workflows

    if signal_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=signal_in.oncall_service.id
        )
        if signal.oncall_service != oncall_service:
            from_service = signal.oncall_service.name if signal.oncall_service else "None"
            to_service = oncall_service.name if oncall_service else "None"
            updates["oncall_service"] = f"{from_service} -> {to_service}"
        signal.oncall_service = oncall_service

    if signal_in.case_priority:
        case_priority = case_priority_service.get_by_name_or_default(
            db_session=db_session,
            project_id=signal.project.id,
            case_priority_in=signal_in.case_priority,
        )
        if signal.case_priority != case_priority:
            from_case_priority = signal.case_priority.name if signal.case_priority else "None"
            to_case_priority = case_priority.name if case_priority else "None"
            updates["case_priority"] = f"{from_case_priority} -> {to_case_priority}"
        signal.case_priority = case_priority

    if signal_in.case_type:
        case_type = case_type_service.get_by_name_or_default(
            db_session=db_session, project_id=signal.project.id, case_type_in=signal_in.case_type
        )
        if signal.case_type != case_type:
            from_case_type = signal.case_type.name if signal.case_type else "None"
            to_case_type = case_type.name if case_type else "None"
            updates["case_type"] = f"{from_case_type} -> {to_case_type}"
        signal.case_type = case_type

    db_session.commit()

    # only log if something changed
    if updates:
        individual = (
            individual_service.get_by_email_and_project(
                db_session=db_session, email=user.email, project_id=signal.project.id
            )
            if user
            else None
        )

        event_service.log_signal_event(
            db_session=db_session,
            source="Dispatch Core App",
            description="Signal updated",
            details=updates,
            individual_id=individual.id if individual else None,
            dispatch_user_id=user.id if user else None,
            signal_id=signal.id,
            owner=user.email if user else None,
            pinned=True,
        )

    return signal


def delete(*, db_session: Session, signal_id: int):
    """Deletes a signal definition."""
    signal = db_session.query(Signal).filter(Signal.id == signal_id).one()
    db_session.delete(signal)
    db_session.commit()
    return signal_id


def is_valid_uuid(value) -> bool:
    """
    Checks if the provided value is a valid UUID.

    Args:
        val: The value to be checked.

    Returns:
        bool: True if the value is a valid UUID, False otherwise.
    """
    try:
        uuid.UUID(str(value), version=4)
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

    # remove non-serializable entities from the raw JSON:
    signal_instance_in_raw = signal_instance_in.raw.copy()
    if signal_instance_in.oncall_service:
        signal_instance_in_raw.pop("oncall_service")

    # we round trip the raw data to json-ify date strings
    signal_instance = SignalInstance(
        **signal_instance_in.dict(
            exclude={
                "case",
                "case_priority",
                "case_type",
                "entities",
                "external_id",
                "oncall_service",
                "project",
                "raw",
                "signal",
            }
        ),
        raw=json.loads(json.dumps(signal_instance_in_raw)),
        project=project,
        signal=signal,
    )

    # if the signal has an existing uuid we propgate it as our primary key
    if signal_instance_in.raw:
        if signal_instance_in.raw.get("id"):
            signal_instance.id = signal_instance_in.raw["id"]

    if signal_instance.id and not is_valid_uuid(signal_instance.id):
        msg = f"Invalid signal id format. Expecting UUIDv4 format. Signal id: {signal_instance.id}. Signal name/variant: {signal_instance.raw['name'] if signal_instance and signal_instance.raw and signal_instance.raw.get('name') else signal_instance.raw['variant']}"
        log.exception(msg)
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

    if signal_instance_in.oncall_service:
        oncall_service = service_service.get_by_name(
            db_session=db_session,
            project_id=project.id,
            name=signal_instance_in.oncall_service.name,
        )
        signal_instance.oncall_service = oncall_service

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
        if not f.mode:
            log.warning(f"Signal filter {f.name} has no mode")
            continue

        if f.mode != SignalFilterMode.active:
            continue

        if not f.action:
            log.warning(f"Signal filter {f.name} has no action")
            continue

        if f.action != SignalFilterAction.snooze:
            continue

        if not f.expiration:
            log.warning(f"Signal filter {f.name} has no expiration date")
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
    if not signal_instance.signal.filters:
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
        .limit(500)
        .all()
    )


def get_instances_in_case(db_session: Session, case_id: int) -> Query:
    """
    Retrieves signal instances associated with a given case.

    Args:
        db_session (Session): The database session.
        case_id (int): The ID of the case.

    Returns:
        Query: A SQLAlchemy query object for the signal instances associated with the case.
    """
    return (
        db_session.query(SignalInstance, Signal)
        .join(Signal)
        .with_entities(SignalInstance.id, Signal)
        .filter(SignalInstance.case_id == case_id)
        .order_by(SignalInstance.created_at)
    )


def get_cases_for_signal(db_session: Session, signal_id: int, limit: int = 10) -> Query:
    """
    Retrieves cases associated with a given signal.

    Args:
        db_session (Session): The database session.
        signal_id (int): The ID of the signal.
        limit (int, optional): The maximum number of cases to retrieve. Defaults to 10.

    Returns:
        Query: A SQLAlchemy query object for the cases associated with the signal.
    """
    return (
        db_session.query(Case)
        .join(SignalInstance)
        .filter(SignalInstance.signal_id == signal_id)
        .order_by(desc(Case.created_at))
        .limit(limit)
    )


def get_cases_for_signal_by_resolution_reason(
    db_session: Session, signal_id: int, resolution_reason: str, limit: int = 10
) -> Query:
    """
    Retrieves cases associated with a given signal and resolution reason.

    Args:
        db_session (Session): The database session.
        signal_id (int): The ID of the signal.
        resolution_reason (str): The resolution reason to filter cases by.
        limit (int, optional): The maximum number of cases to retrieve. Defaults to 10.

    Returns:
        Query: A SQLAlchemy query object for the cases associated with the signal and resolution reason.
    """
    return (
        db_session.query(Case)
        .join(SignalInstance)
        .filter(SignalInstance.signal_id == signal_id)
        .filter(Case.resolution_reason == resolution_reason)
        .order_by(desc(Case.created_at))
        .limit(limit)
    )


def get_signal_stats(
    *,
    db_session: Session,
    entity_value: str,
    entity_type_id: int,
    signal_id: int | None = None,
    num_days: int | None = None,
) -> Optional[SignalStats]:
    """
    Gets signal statistics for a given named entity and type.

    If signal_id is provided, only returns stats for that specific signal definition.
    """
    entity_subquery = (
        db_session.query(
            func.jsonb_build_array(
                func.jsonb_build_object(
                    "or",
                    func.jsonb_build_array(
                        func.jsonb_build_object(
                            "model", "Entity", "field", "id", "op", "==", "value", Entity.id
                        )
                    ),
                )
            )
        )
        .filter(and_(Entity.value == entity_value, Entity.entity_type_id == entity_type_id))
        .as_scalar()
    )

    active_count = func.count().filter(SignalFilter.expiration > func.current_date())
    expired_count = func.count().filter(SignalFilter.expiration <= func.current_date())

    query = db_session.query(
        active_count.label("active_count"), expired_count.label("expired_count")
    ).filter(cast(SignalFilter.expression, JSONB).op("@>")(entity_subquery))

    snooze_result = db_session.execute(query).fetchone()

    # Calculate the date threshold based on num_days
    date_threshold = datetime.utcnow() - timedelta(days=num_days) if num_days is not None else None

    count_with_snooze = func.count().filter(SignalInstance.filter_action == "snooze")
    count_without_snooze = func.count().filter(
        (SignalInstance.filter_action != "snooze") | (SignalInstance.filter_action.is_(None))
    )

    query = (
        select(
            [
                count_with_snooze.label("count_with_snooze"),
                count_without_snooze.label("count_without_snooze"),
            ]
        )
        .select_from(
            assoc_signal_instance_entities.join(
                Entity, assoc_signal_instance_entities.c.entity_id == Entity.id
            ).join(
                SignalInstance,
                assoc_signal_instance_entities.c.signal_instance_id == SignalInstance.id,
            )
        )
        .where(
            and_(
                Entity.value == entity_value,
                Entity.entity_type_id == entity_type_id,
                SignalInstance.signal_id == signal_id if signal_id else True,
                SignalInstance.created_at >= date_threshold if date_threshold else True,
            )
        )
    )

    signal_result = db_session.execute(query).fetchone()

    return SignalStats(
        num_signal_instances_alerted=signal_result.count_without_snooze,
        num_signal_instances_snoozed=signal_result.count_with_snooze,
        num_snoozes_active=snooze_result.active_count,
        num_snoozes_expired=snooze_result.expired_count,
    )
