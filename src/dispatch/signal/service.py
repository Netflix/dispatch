import json
import uuid
import hashlib
from typing import Optional

from sqlalchemy import asc

from dispatch.auth.models import DispatchUser
from dispatch.case.priority import service as case_priority_service
from dispatch.case.type import service as case_type_service
from dispatch.database.service import apply_filters, apply_filter_specific_joins
from dispatch.project import service as project_service

from .models import (
    Signal,
    SignalCreate,
    SignalFilter,
    SignalFilterAction,
    SignalFilterCreate,
    SignalFilterMode,
    SignalFilterUpdate,
    SignalInstance,
    SignalInstanceCreate,
    SignalUpdate,
)


def create_signal_filter(
    *, db_session, creator: DispatchUser, signal_filter_in: SignalFilterCreate
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


def create_suppression_rule(
    *, db_session, suppression_rule_in: SuppressionRuleCreate
) -> SuppressionRule:
    """Creates a new suppression rule."""
    rule = SuppressionRule(**suppression_rule_in.dict(exclude={"tags"}))

    tags = []
    for t in suppression_rule_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    rule.tags = tags
    db_session.add(rule)
    db_session.commit()
    return rule


def update_suppression_rule(
    *, db_session, suppression_rule_in: SuppressionRuleUpdate
) -> SuppressionRule:
    """Updates an existing suppression rule."""
    rule = (
        db_session.query(SuppressionRule).filter(SuppressionRule.id == suppression_rule_in.id).one()
    )

    for field in signal_filter_data:
        if field in update_data:
            setattr(signal_filter, field, update_data[field])

    db_session.add(signal_filter)
    db_session.commit()
    return signal_filter


def delete_signal_filter(*, db_session, signal_filter_id: int) -> int:
    """Deletes an existing signal filter."""
    signal_filter = db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_id).one()
    db_session.delete(signal_filter)
    db_session.commit()
    return signal_filter_id


def get_signal_filter_by_name(*, db_session, project_id: int, name: str) -> Optional[SignalFilter]:
    """Gets a signal filter by it's name."""
    return (
        db_session.query(SignalFilter)
        .filter(SignalFilter.project_id == project_id)
        .filter(SignalFilter.name == name)
        .first()
    )


def get_signal_filter(*, db_session, signal_filter_id: int) -> SignalFilter:
    """Gets a single signal filter."""
    return db_session.query(SignalFilter).filter(SignalFilter.id == signal_filter_id).one_or_none()


def get(*, db_session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).one_or_none()


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

    for f in signal_in.filters:
        signal_filter = get_signal_filter_by_name(db_session=db_session, signal_filter_in=f)
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
        signal_filter = get_signal_filter_by_name(
            db_session=db_session, project_id=signal.project.id, name=f.name
        )
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
        **signal_instance_in.dict(exclude={"case", "signal", "project", "entities", "raw"}),
        raw=json.loads(signal_instance_in.raw.json()),
        project=project,
    )

    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def apply_filter_actions(*, db_session, signal_instance: SignalInstance):
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
