import json
from typing import Optional
from datetime import datetime, timedelta, timezone
from dispatch.project import service as project_service
from dispatch.case.type import service as case_type_service
from dispatch.case.priority import service as case_priority_service

from .models import (
    Signal,
    SignalCreate,
    SignalUpdate,
    SignalInstance,
    SignalInstanceCreate,
    SignalFilterMode,
    SignalFilter,
    SignalFilterCreate,
    SignalFilterUpdate,
    SignalFilterRead,
)


def create_signal_filter(*, db_session, signal_filter_in: SignalFilterCreate) -> SignalFilter:
    """Creates a new suppression filter."""
    filter = SignalFilter(**signal_filter_in.dict())

    db_session.add(filter)
    db_session.commit()
    return filter


def update_signal_filter(*, db_session, signal_filter_in: SignalFilterUpdate) -> SignalFilter:
    """Updates an existing suppression filter."""
    filter = db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_in.id).one()

    db_session.add(filter)
    db_session.commit()
    return filter


def get(*, db_session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).one()


def get_by_variant_or_external_id(
    *, db_session, project_id: int, external_id: str = None, variant: str = None
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


def create(*, db_session, signal_in: SignalCreate) -> Signal:
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
            }
        ),
        project=project,
    )

    for f in signal_in.filter:
        signal_filter = create_signal_filter(db_session=db_session, signal_filter_in=f)
        signal.filters.append(signal_filter)

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


def update(*, db_session, signal: Signal, signal_in: SignalUpdate) -> Signal:
    """Creates a new signal."""
    signal_data = signal.dict()
    update_data = signal_in.dict(
        skip_defaults=True,
        exclude={
            "project",
            "case_type",
            "case_priority",
            "source",
            "filters",
        },
    )

    for field in signal_data:
        if field in update_data:
            setattr(signal, field, update_data[field])

    for f in signal_in.filters:
        if signal_in.suppression_filter.id:
            update_signal_filter(db_session=db_session, signal_filter_in=f)
        else:
            signal_filter = create_signal_filter(db_session=db_session, signal_filter_in=f)
            signal.filters.append(signal_filter)

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


def delete(*, db_session, signal_id: int):
    """Deletes a signal definition."""
    signal = db_session.query(Signal).filter(Signal.id == signal_id).one()
    db_session.delete(signal)
    db_session.commit()
    return signal_id


def create_instance(*, db_session, signal_instance_in: SignalInstanceCreate) -> SignalInstance:
    """Creates a new signal instance."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_instance_in.project
    )

    # we round trip the raw data to json-ify date strings
    signal_instance = SignalInstance(
        **signal_instance_in.dict(exclude={"project", "tags", "raw"}),
        raw=json.loads(signal_instance_in.raw.json()),
        project=project,
    )

    # signal_instance.tags = find_instance_tags(signal_instance.raw)
    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def deduplicate(
    *, db_session, signal_instance: SignalInstance, duplication_filter: SignalFilter
) -> bool:
    """Find any matching duplication filters and match signals."""
    if duplication_filter.mode != SignalFilterMode.active:
        return

    window = datetime.now(timezone.utc) - timedelta(seconds=duplication_filter.window)

    instances = (
        db_session.query(SignalInstance)
        .filter(Signal.id == signal_instance.signal.id)
        .filter(SignalInstance.id != signal_instance.id)
        .filter(SignalInstance.created_at >= window)
        .all()
    )

    if instances:
        # TODO find the earliest created instance
        signal_instance.case_id = instances[0].case_id
        signal_instance.duplication_filter_id = duplication_filter.id

    db_session.commit()
    return True


def suppress(
    *, db_session, signal_instance: SignalInstance, suppression_filter: SignalFilter
) -> bool:
    """Find any matching suppression filters and match instances."""
    supressed = False

    if not suppression_filter:
        return supressed

    if suppression_filter.mode != SignalFilterMode.active:
        return supressed

    if suppression_filter.expiration:
        if suppression_filter.expiration <= datetime.now():
            return supressed

    # TODO apply filter logic

    db_session.commit()
    return supressed
