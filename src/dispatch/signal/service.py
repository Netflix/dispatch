import json
import hashlib
import re
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from dispatch.enums import RuleMode
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service
from dispatch.tag_type import service as tag_type_service
from dispatch.case.type import service as case_type_service
from dispatch.case.priority import service as case_priority_service
from dispatch.entity_type import service as entity_type_service
from dispatch.entity import service as entity_service
from dispatch.entity.models import Entity, EntityCreate
from dispatch.entity_type.models import EntityType

from .models import (
    Signal,
    SignalCreate,
    SignalUpdate,
    SignalInstance,
    SuppressionRule,
    DuplicationRule,
    SignalInstanceCreate,
    DuplicationRuleCreate,
    DuplicationRuleUpdate,
    SuppressionRuleCreate,
    SuppressionRuleUpdate,
)


def create_duplication_rule(
    *, db_session, duplication_rule_in: DuplicationRuleCreate
) -> DuplicationRule:
    """Creates a new duplication rule."""
    rule = DuplicationRule(**duplication_rule_in.dict(exclude={"tag_types"}))

    tag_types = []
    for t in duplication_rule_in.tag_types:
        tag_types.append(tag_type_service.get(db_session=db_session, tag_type_id=t.id))

    rule.tag_types = tag_types
    db_session.add(rule)
    db_session.commit()
    return rule


def update_duplication_rule(
    *, db_session, duplication_rule_in: DuplicationRuleUpdate
) -> DuplicationRule:
    """Updates an 1existing duplication rule."""
    rule = (
        db_session.query(DuplicationRule).filter(DuplicationRule.id == duplication_rule_in.id).one()
    )

    tag_types = []
    for t in duplication_rule_in.tag_types:
        tag_types.append(tag_type_service.get(db_session=db_session, tag_type_id=t.id))

    rule.tag_types = tag_types
    rule.window = duplication_rule_in.window
    db_session.add(rule)
    db_session.commit()
    return rule


def create_suppression_rule(
    *, db_session, suppression_rule_in: SuppressionRuleCreate
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


def update_suppression_rule(
    *, db_session, suppression_rule_in: SuppressionRuleUpdate
) -> SuppressionRule:
    """Updates an existing supression rule."""
    rule = (
        db_session.query(SuppressionRule).filter(SuppressionRule.id == suppression_rule_in.id).one()
    )

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
                "suppression_rule",
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

    if signal_in.suppression_rule:
        suppression_rule = create_suppression_rule(
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

    if entity_types := signal_in.entity_types:
        for entity_type in entity_types:
            if entity_type.id:
                entity_type = entity_type_service.get(
                    db_session=db_session, entity_type_id=entity_type.id
                )
                signal.entity_types.append(entity_type)

    if signal_in.duplication_rule:
        if signal_in.duplication_rule.id:
            update_duplication_rule(
                db_session=db_session, duplication_rule_in=signal_in.duplication_rule
            )
        else:
            duplication_rule = create_duplication_rule(
                db_session=db_session, duplication_rule_in=signal_in.duplication_rule
            )
            signal.duplication_rule = duplication_rule

    if signal_in.suppression_rule:
        if signal_in.suppression_rule.id:
            update_suppression_rule(
                db_session=db_session, suppression_rule_in=signal_in.suppression_rule
            )
        else:
            suppression_rule = create_suppression_rule(
                db_session=db_session, suppression_rule_in=signal_in.suppression_rule
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

    tags = []
    for t in signal_instance_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    signal_instance.tags = tags

    db_session.add(signal_instance)
    db_session.commit()
    return signal_instance


def create_instance_fingerprint(duplication_rule, signal_instance: SignalInstance) -> str:
    """Given a list of tag_types and tags creates a hash of their values."""
    fingerprint = hashlib.sha1(str(signal_instance.raw).encode("utf-8")).hexdigest()

    # use tags if we have them
    if duplication_rule:
        if signal_instance.tags:
            tag_type_names = [t.name for t in duplication_rule.tag_types]
            hash_values = []
            for tag in signal_instance.tags:
                if tag.tag_type.name in tag_type_names:
                    hash_values.append(tag.tag_type.name)
            fingerprint = hashlib.sha1("-".join(sorted(hash_values)).encode("utf-8")).hexdigest()

    return fingerprint


def deduplicate(
    *, db_session, signal_instance: SignalInstance, duplication_rule: DuplicationRule
) -> bool:
    """Find any matching duplication rules and match signals."""
    duplicate = False

    # always fingerprint
    fingerprint = create_instance_fingerprint(duplication_rule, signal_instance)
    signal_instance.fingerprint = fingerprint
    db_session.commit()

    if not duplication_rule:
        return duplicate

    if duplication_rule.mode != RuleMode.active:
        return duplicate

    window = datetime.now(timezone.utc) - timedelta(seconds=duplication_rule.window)
    fingerprint = create_instance_fingerprint(duplication_rule.tag_types, signal_instance)

    instances = (
        db_session.query(SignalInstance)
        .filter(Signal.id == signal_instance.signal.id)
        .filter(SignalInstance.id != signal_instance.id)
        .filter(SignalInstance.created_at >= window)
        .filter(SignalInstance.fingerprint == fingerprint)
        .all()
    )

    if instances:
        duplicate = True
        # TODO find the earliest created instance
        signal_instance.case_id = instances[0].case_id
        signal_instance.duplication_rule_id = duplication_rule.id

    db_session.commit()
    return duplicate


def supress(
    *, db_session, signal_instance: SignalInstance, suppression_rule: SuppressionRule
) -> bool:
    """Find any matching suppression rules and match instances."""
    supressed = False

    if not suppression_rule:
        return supressed

    if suppression_rule.mode != RuleMode.active:
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


def find_entities(
    db_session: Session, signal_instance: SignalInstance, entity_types: Sequence[EntityType]
) -> list[Entity]:
    """Find entities of the given types in the raw data of a signal instance.

    Args:
        db_session (Session): SQLAlchemy database session.
        signal_instance (SignalInstance): SignalInstance to search for entities in.
        entity_types (list[EntityType]): List of EntityType objects to search for.

    Returns:
        list[Entity]: List of Entity objects found.

    Example:
        >>> signal_instance = SignalInstance(
        ...     raw={
        ...         "name": "John Smith",
        ...         "email": "john.smith@example.com",
        ...         "phone": "555-555-1212",
        ...         "address": {
        ...             "street": "123 Main St",
        ...             "city": "Anytown",
        ...             "state": "CA",
        ...             "zip": "12345"
        ...         },
        ...         "notes": "Customer is interested in buying a product."
        ...     }
        ... )
        >>> entity_types = [
        ...     EntityType(name="Name", field="name", regular_expression=r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
        ...     EntityType(name="Phone", field=None, regular_expression=r"\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\b"),
        ... ]
        >>> entities = find_entities(db_session, signal_instance, entity_types)

    Notes:
        This function uses depth-first search to traverse the raw data of the signal instance. It searches for
        the regular expressions specified in the EntityType objects in the values of the dictionary, list, and
        string objects encountered during the traversal. The search can be limited to a specific key in the
        dictionary objects by specifying a value for the 'field' attribute of the EntityType object.
    """

    def search(key, val, entity_type_pairs):
        # Create a list to hold any entities that are found in this value
        entities = []

        # If this value has been searched before, return the cached entities
        if id(val) in cache:
            return cache[id(val)]

        # If the value is a dictionary, search its key-value pairs recursively
        if isinstance(val, dict):
            for subkey, subval in val.items():
                entities.extend(search(subkey, subval, entity_type_pairs))

        # If the value is a list, search its items recursively
        elif isinstance(val, list):
            for item in val:
                entities.extend(search(None, item, entity_type_pairs))

        # If the value is a string, search it for entity matches
        elif isinstance(val, str):
            for entity_type, entity_regex, field in entity_type_pairs:
                import time

                time.sleep(3)
                # If a field was specified for this entity type, only search that field
                if not field or key == field:
                    print(f"Checking {val} for {entity_type.name} using {entity_regex} in {field=}")
                    # Search the string for matches to the entity type's regular expression
                    if match := entity_regex.search(val):
                        print(f"Found match {match.group(0)} for {entity_type.name} in {field=}")
                        # If a match was found, create a new Entity object for it
                        entity = EntityCreate(
                            value=match.group(0),
                            entity_type=entity_type,
                            project=signal_instance.project,
                        )
                        # Add the entity to the list of entities found in this value
                        entities.append(entity)

        # Cache the entities found for this value
        cache[id(val)] = entities

        return entities

    # Create a list of (entity type, regular expression, field) tuples
    entity_type_pairs = [
        (type, re.compile(type.regular_expression), type.field)
        for type in entity_types
        if isinstance(type.regular_expression, str)
    ]

    # Initialize a cache of previously searched values
    cache = {}

    # Traverse the signal data using depth-first search
    entities = [
        entity
        for key, val in signal_instance.raw.items()
        for entity in search(key, val, entity_type_pairs)
    ]

    # Create the entities in the database and add them to the signal instance
    entities_out = [
        entity_service.get_or_create(db_session=db_session, entity_in=entity_in)
        for entity_in in entities
    ]

    # Return the list of entities found
    return entities_out
