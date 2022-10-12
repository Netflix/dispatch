import hashlib
from signal import signal
from typing import Optional
from datetime import datetime, timedelta
from dispatch.enums import RuleMode
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service


from .models import Signal, SignalCreate, SignalInstance, SignalInstanceCreate


def get(*, db_session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).first()


def create(*, db_session, signal_in: SignalCreate) -> Signal:
    """Creates a new signal."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_in.project
    )

    signal = Signal(**signal_in.dict(exclude={"project", "tags"}), project=project)

    tags = []
    for t in signal_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    signal.tags = tags

    db_session.add(signal)
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


def deduplicate(*, db_session, signal_instance: SignalInstance):
    """Find any matching duplication rules and match signals."""
    duplicate = False
    rule = signal_instance.signal.duplication_rule
    if not rule:
        return duplicate

    if rule.status != RuleMode.active:
        return duplicate

    window = datetime.now() - timedelta(seconds=rule.window)

    fingerprint = create_instance_fingerprint(rule.tag_types, signal_instance.tags)

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
        signal_instance.duplication_rule_id = rule.id

    signal_instance.fingerprint = fingerprint
    db_session.commit()
    return duplicate


def supress(*, db_session, signal_instance: SignalInstance):
    """Find any matching suppression rules and match instances."""
    supressed = False

    rule = signal_instance.signal.supression_rule
    if not rule:
        return supressed

    if rule.status != RuleMode.active:
        return supressed

    if rule.expiration:
        if rule.expiration <= datetime.now():
            return supressed

    rule_tag_ids = sorted([t.id for t in rule.tags])
    signal_tag_ids = sorted([t.id for t in signal_instance.tags])

    if rule_tag_ids == signal_tag_ids:
        supressed = True
        signal_instance.suppression_rule_id = rule.id

    db_session.commit()
    return supressed
