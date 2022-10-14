import hashlib
from typing import Optional
from datetime import datetime, timedelta
from dispatch.enums import RuleMode
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service
from dispatch.tag_type import service as tag_type_service
from dispatch.case.type import service as case_type_service
from dispatch.case.priority import service as case_priority_service

from .models import (
    Signal,
    SignalCreate,
    SignalUpdate,
    SignalInstance,
    SuppressionRule,
    DuplicationRule,
    SignalInstanceCreate,
    DuplicationRuleBase,
    SuppressionRuleBase,
)


def create_duplication_rule(
    *, db_session, duplication_rule_in: DuplicationRuleBase
) -> DuplicationRule:
    """Creates a new duplication rule."""
    rule = DuplicationRule(**duplication_rule_in.dict(exclude={"tag_types"}))

    tag_types = []
    for t in duplication_rule_in.tag_types:
        tag_types.append(tag_type_service.get(db_session=db_session, tag_type_in=t))

    rule.tag_types = tag_types
    db_session.add(rule)
    db_session.commit()
    return rule


def create_supression_rule(
    *, db_session, suppression_rule_in: SuppressionRuleBase
) -> SuppressionRule:
    """Creates a new supression rule."""
    rule = SuppressionRule(**suppression_rule_in.dict(exclude={"tags"}))

    tags = []
    for t in suppression_rule_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    rule.tags = tags
    db_session.add(rule)
    db_session.commit()
    return rule


def get(*, db_session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).one()


def get_by_external_id_and_variant(
    *, db_session, external_id: str, variant: str = None
) -> Optional[Signal]:
    """Gets a signal it's external id (and variant if supplied)."""
    if variant:
        return (
            db_session.query(Signal)
            .filter(Signal.external_id == external_id)
            .filter(Signal.variant == variant)
            .one()
        )
    return db_session.query(Signal).filter(Signal.external_id == external_id).one()


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
                "supression_rule",
                "duplication_rule",
            }
        ),
        project=project,
    )

    if signal_in.duplication_rule:
        duplication_rule = create_duplication_rule(
            db_session=db_session, duplication_rule_in=signal_in.duplication_rule
        )
        signal.duplication_rule = duplication_rule

    if signal_in.supression_rule:
        suppression_rule = create_supression_rule(
            db_session=db_session, suppression_rule_in=signal.suppression_rule
        )
        signal.suppression_rule = suppression_rule

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

    update_data = signal_in.dict(skip_defaults=True)

    for field in signal_data:
        if field in update_data:
            setattr(signal, field, update_data[field])

    if signal_in.duplication_rule:
        duplication_rule = create_duplication_rule(
            db_session=db_session, duplication_rule_in=signal_in.duplication_rule
        )
        signal.duplication_rule = duplication_rule

    if signal_in.supression_rule:
        suppression_rule = create_supression_rule(
            db_session=db_session, suppression_rule_in=signal.suppression_rule
        )
        signal.suppression_rule = suppression_rule

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


def create_instance(*, db_session, signal_instance_in: SignalInstanceCreate) -> SignalInstance:
    """Creates a new signal instance."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_instance_in.project
    )

    signal_instance = SignalInstance(
        **signal_instance_in.dict(exclude={"project", "tags"}), project=project
    )

    tags = []
    for t in signal_instance_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    signal_instance.tags = tags

    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def create_instance_fingerprint(tag_types, tags):
    """Given a list of tag_types and tags creates a hash of their values."""
    tag_values = []
    tag_type_names = [t.name for t in tag_types]
    for tag in tags:
        if tag.tag_type.name in tag_type_names:
            tag_values = tag.tag_type.name

    return hashlib.sha1("-".join(sorted(tag_values)))


def deduplicate(*, db_session, signal_instance: SignalInstance, duplication_rule: DuplicationRule):
    """Find any matching duplication rules and match signals."""
    duplicate = False
    if not duplication_rule:
        return duplicate

    if duplication_rule.status != RuleMode.active:
        return duplicate

    window = datetime.now() - timedelta(seconds=duplication_rule.window)

    fingerprint = create_instance_fingerprint(duplication_rule.tag_types, signal_instance.tags)

    instances = (
        db_session.query(SignalInstance)
        .filter(Signal.id == signal_instance.signal.id)
        .filter(SignalInstance.created_at >= window)
        .filter(SignalInstance.fingerprint == signal_instance.fingerprint)
        .all()
    )

    if instances:
        duplicate = True
        # TODO find the earliest created instance
        signal_instance.case_id = instances[0].case_id
        signal_instance.duplication_rule_id = duplication_rule.id

    signal_instance.fingerprint = fingerprint
    db_session.commit()
    return duplicate


def supress(*, db_session, signal_instance: SignalInstance, suppression_rule: SuppressionRule):
    """Find any matching suppression rules and match instances."""
    supressed = False

    if not suppression_rule:
        return supressed

    if suppression_rule.status != RuleMode.active:
        return supressed

    if suppression_rule.expiration:
        if suppression_rule.expiration <= datetime.now():
            return supressed

    rule_tag_ids = sorted([t.id for t in suppression_rule.tags])
    signal_tag_ids = sorted([t.id for t in signal_instance.tags])

    if rule_tag_ids == signal_tag_ids:
        supressed = True
        signal_instance.suppression_rule_id = suppression_rule.id

    db_session.commit()
    return supressed
