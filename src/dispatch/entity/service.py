from datetime import datetime, timedelta
from typing import Optional, Sequence
import re

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session, joinedload

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.case.models import Case
from dispatch.entity.models import Entity, EntityCreate, EntityUpdate, EntityRead
from dispatch.entity_type import service as entity_type_service
from dispatch.entity_type.models import EntityType
from dispatch.signal.models import SignalInstance


def get(*, db_session, entity_id: int) -> Optional[Entity]:
    """Gets a entity by its id."""
    return db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Entity]:
    """Gets a entity by its project and name."""
    return (
        db_session.query(Entity)
        .filter(Entity.name == name)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, entity_in=EntityRead) -> EntityRead:
    """Returns the entity specified or raises ValidationError."""
    entity = get_by_name(db_session=db_session, project_id=project_id, name=entity_in.name)

    if not entity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Entity not found.",
                        entity=entity_in.name,
                    ),
                    loc="entity",
                )
            ],
            model=EntityRead,
        )

    return entity


def get_by_value(*, db_session, project_id: int, value: str) -> Optional[Entity]:
    """Gets a entity by its value."""
    return (
        db_session.query(Entity)
        .filter(Entity.value == value)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int):
    """Gets all entities by their project."""
    return db_session.query(Entity).filter(Entity.project_id == project_id)


def create(*, db_session, entity_in: EntityCreate) -> Entity:
    """Creates a new entity."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=entity_in.project
    )
    entity_type = entity_type_service.get_or_create(
        db_session=db_session, entity_type_in=entity_in.entity_type
    )
    entity = Entity(
        **entity_in.dict(exclude={"entity_type", "project"}),
        project=project,
        entity_type=entity_type,
    )
    entity.entity_type = entity_type
    entity.project = project
    db_session.add(entity)
    db_session.commit()
    return entity


def get_by_value_or_create(*, db_session, entity_in: EntityCreate) -> Entity:
    """Gets or creates a new entity."""
    # prefer the entity id if available
    if entity_in.id:
        q = db_session.query(Entity).filter(Entity.id == entity_in.id)
    else:
        q = db_session.query(Entity).filter_by(value=entity_in.value)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_in=entity_in)


def update(*, db_session, entity: Entity, entity_in: EntityUpdate) -> Entity:
    """Updates an existing entity."""
    entity_data = entity.dict()
    update_data = entity_in.dict(skip_defaults=True, exclude={"entity_type"})

    for field in entity_data:
        if field in update_data:
            setattr(entity, field, update_data[field])

    if entity_in.entity_type is not None:
        entity_type = entity_type_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=entity.project.id,
            entity_type_in=entity_in.entity_type,
        )
        entity.entity_type = entity_type

    db_session.commit()
    return entity


def delete(*, db_session, entity_id: int):
    """Deletes an existing entity."""
    entity = db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()
    db_session.delete(entity)
    db_session.commit()


def get_cases_with_entity(db: Session, entity_id: int, days_back: int) -> list[Case]:
    """Searches for cases with the same entity within a given timeframe."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Query for signal instances containing the entity within the search window
    cases = (
        db.query(Case)
        .join(Case.signal_instances)
        .join(SignalInstance.entities)
        .filter(Entity.id == entity_id, SignalInstance.created_at >= start_date)
        .all()
    )
    return cases


def get_signal_instances_with_entity(
    db: Session, entity_id: int, days_back: int
) -> list[SignalInstance]:
    """Searches for signal instances with the same entity within a given timeframe."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Query for signal instances containing the entity within the search window
    signal_instances = (
        db.query(SignalInstance)
        .options(joinedload(SignalInstance.signal))
        .join(SignalInstance.entities)
        .filter(SignalInstance.created_at >= start_date, Entity.id == entity_id)
        .all()
    )

    return signal_instances


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

    def _search(key, val, entity_type_pairs):
        # Create a list to hold any entities that are found in this value
        entities = []

        # If this value has been searched before, return the cached entities
        if id(val) in cache:
            return cache[id(val)]

        # If the value is a dictionary, search its key-value pairs recursively
        if isinstance(val, dict):
            for subkey, subval in val.items():
                entities.extend(_search(subkey, subval, entity_type_pairs))

        # If the value is a list, search its items recursively
        elif isinstance(val, list):
            for item in val:
                entities.extend(_search(None, item, entity_type_pairs))

        # If the value is a string, search it for entity matches
        elif isinstance(val, str):
            for entity_type, entity_regex, field in entity_type_pairs:
                # If a field was specified for this entity type, only search that field
                if not field or key == field:
                    # Search the string for matches to the entity type's regular expression
                    if match := entity_regex.search(val):
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
        for entity in _search(key, val, entity_type_pairs)
    ]

    # Create the entities in the database and add them to the signal instance
    entities_out = [
        get_by_value_or_create(db_session=db_session, entity_in=entity_in) for entity_in in entities
    ]

    # Return the list of entities found
    return entities_out
