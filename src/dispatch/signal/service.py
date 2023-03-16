import json
from sqlalchemy_utils import cast_if

from datetime import datetime, timedelta, timezone
from typing import Optional, Literal

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy import asc, String
from sqlalchemy.orm import Session


from dispatch.auth.models import DispatchUser
from dispatch.case.priority import service as case_priority_service
from dispatch.case.type import service as case_type_service
from dispatch.case.type.models import CaseType
from dispatch.database.service import apply_filter_specific_joins, apply_filters
from dispatch.entity_type import service as entity_type_service
from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service
from dispatch.workflow import service as workflow_service

from .models import (
    Signal,
    SignalCreate,
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
    """Gets a signal filter by it's name."""
    return (
        db_session.query(SignalFilter)
        .filter(SignalFilter.project_id == project_id)
        .filter(SignalFilter.name == name)
        .first()
    )


def get_signal_filter(*, db_session: Session, signal_filter_id: int) -> SignalFilter:
    """Gets a single signal filter."""
    return db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_id).one_or_none()


def get_signal_instance(*, db_session: Session, signal_instance_id: int | str):
    """Gets a signal instance by it's UUID."""
    return (
        db_session.query(SignalInstance)
        .filter(SignalInstance.id == cast_if(signal_instance_id, String))
        .one_or_none()
    )


def get(*, db_session: Session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).one_or_none()


def get_by_variant_or_external_id(
    *, db_session: Session, project_id: int, external_id: str = None, variant: str = None
) -> Optional[Signal]:
    """Gets a signal it's external id (and variant if supplied)."""
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
    """Gets all signals for a given conversation target. (e.g. #conversation-channel)"""
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
                "project",
                "case_type",
                "case_priority",
                "source",
                "filters",
                "tags",
                "entity_types",
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
        entity_type = entity_type_service.get_by_name_or_raise(
            db_session=db_session, project_id=project.id, entity_type_in=e
        )
        entity_types.append(entity_type)

    signal.entity_types = entity_types

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
            "filters",
            "entity_types",
            "tags",
        },
    )

    for field in signal_data:
        if field in update_data:
            setattr(signal, field, update_data[field])

    tags = []
    for t in signal_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))
    signal.tags = tags

    entity_types = []
    for e in signal_in.entity_types:
        entity_type = entity_type_service.get_by_name_or_raise(
            db_session=db_session, project_id=signal.project.id, entity_type_in=e
        )
        entity_types.append(entity_type)

    signal.entity_types = entity_types

    filters = []
    for f in signal_in.filters:
        signal_filter = get_signal_filter_by_name_or_raise(
            db_session=db_session, project_id=signal.project.id, signal_filter_in=f
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
            db_session=db_session,
            project_id=signal.case_type.project.id,
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


def create_instance(
    *, db_session: Session, signal_instance_in: SignalInstanceCreate
) -> SignalInstance:
    """Creates a new signal instance."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_instance_in.project
    )

    # we round trip the raw data to json-ify date strings
    signal_instance = SignalInstance(
        **signal_instance_in.dict(exclude={"case", "signal", "project", "entities", "raw"}),
        raw=json.loads(json.dumps(signal_instance_in.raw)),
        project=project,
    )

    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def apply_filter_actions(
    *, db_session: Session, signal_instance: SignalInstance
) -> Literal[True] | None:
    """Applies any matching filter actions associated with this instance."""

    for f in signal_instance.signal.filters:
        if f.mode != SignalFilterMode.active:
            continue

        query = db_session.query(SignalInstance).filter(
            SignalInstance.signal_id == signal_instance.signal_id
        )
        query = apply_filter_specific_joins(SignalInstance, f.expression, query)
        query = apply_filters(query, f.expression)

        # order matters, check for snooze before deduplication
        # we check to see if the current instances match's it's signals snooze filter
        if f.action == SignalFilterAction.snooze:
            if f.expiration.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
                continue

            instances = query.filter(SignalInstance.id == signal_instance.id).all()

            if instances:
                signal_instance.filter_action = SignalFilterAction.snooze
                return

        elif f.action == SignalFilterAction.deduplicate:
            window = datetime.now(timezone.utc) - timedelta(seconds=f.window)
            query = query.filter(SignalInstance.created_at >= window)

            # get the earliest instance
            query = query.order_by(asc(SignalInstance.created_at))
            instances = query.all()

            if instances:
                # associate with existing case
                signal_instance.case_id = instances[0].case_id
                signal_instance.filter_action = SignalFilterAction.deduplicate
                return
    return True
