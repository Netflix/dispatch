from datetime import datetime, timedelta
import logging
from typing import Generator, Optional, Sequence, Union, NewType, NamedTuple
import re

import jsonpath_ng
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.case.models import Case
from dispatch.entity.models import Entity, EntityCreate, EntityUpdate, EntityRead
from dispatch.entity_type import service as entity_type_service
from dispatch.entity_type.models import EntityType
from dispatch.signal.models import Signal, SignalInstance


log = logging.getLogger(__name__)


def get(*, db_session: Session, entity_id: int) -> Optional[Entity]:
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


def get_by_name_or_raise(
    *, db_session: Session, project_id: int, entity_in=EntityRead
) -> EntityRead:
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


def get_by_value(*, db_session: Session, project_id: int, value: str) -> Optional[Entity]:
    """Gets a entity by its value."""
    return (
        db_session.query(Entity)
        .filter(Entity.value == value)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session: Session, project_id: int):
    """Gets all entities by their project."""
    return db_session.query(Entity).filter(Entity.project_id == project_id)


def get_all_by_signal(*, db_session: Session, signal_id: int) -> list[Entity]:
    """Gets all entities for a specific signal."""
    return (
        db_session.query(Entity)
        .join(Entity.signal_instances)
        .join(SignalInstance.signal)
        .filter(Signal.id == signal_id)
        .all()
    )


def get_all_desc_by_signal(*, db_session: Session, signal_id: int) -> list[Entity]:
    """Gets all entities for a specific signal in descending order."""
    return (
        db_session.query(Entity)
        .join(Entity.signal_instances)
        .join(SignalInstance.signal)
        .filter(Signal.id == signal_id)
        .order_by(desc(Entity.created_at))
        .all()
    )


def create(*, db_session: Session, entity_in: EntityCreate) -> Entity:
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


def get_by_value_or_create(*, db_session: Session, entity_in: EntityCreate) -> Entity:
    """Gets or creates a new entity."""
    # prefer the entity id if available
    if entity_in.id:
        q = db_session.query(Entity).filter(Entity.id == entity_in.id)
    else:
        q = db_session.query(Entity).filter_by(
            value=entity_in.value, entity_type_id=entity_in.entity_type.id
        )

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_in=entity_in)


def update(*, db_session: Session, entity: Entity, entity_in: EntityUpdate) -> Entity:
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


def delete(*, db_session: Session, entity_id: int):
    """Deletes an existing entity."""
    entity = db_session.query(Entity).filter(Entity.id == entity_id).one()
    db_session.delete(entity)
    db_session.commit()


def get_cases_with_entity(db_session: Session, entity_id: int, days_back: int) -> list[Case]:
    """Searches for cases with the same entity within a given timeframe."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    cases = (
        db_session.query(Case)
        .join(Case.signal_instances)
        .join(SignalInstance.entities)
        .filter(Entity.id == entity_id, SignalInstance.created_at >= start_date)
        .all()
    )
    return cases


def get_case_count_with_entity(db_session: Session, entity_id: int, days_back: int) -> int:
    """Calculate the count of cases with a given Entity by it's ID."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    count = (
        db_session.query(Case)
        .join(Case.signal_instances)
        .join(SignalInstance.entities)
        .filter(Entity.id == entity_id, SignalInstance.created_at >= start_date)
        .count()
    )
    return count


def get_signal_instances_with_entity(
    db_session: Session, entity_id: int, days_back: int
) -> list[SignalInstance]:
    """Searches for signal instances with the same entity within a given timeframe."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Query for signal instances containing the entity within the search window
    signal_instances = (
        db_session.query(SignalInstance)
        .options(joinedload(SignalInstance.signal))
        .join(SignalInstance.entities)
        .filter(SignalInstance.created_at >= start_date, Entity.id == entity_id)
        .all()
    )

    return signal_instances


def get_signal_instances_with_entities(
    db_session: Session, signal_id: int, entity_ids: list[int], days_back: int
) -> list[SignalInstance]:
    """Searches a signal instance with the same entities within a given timeframe."""
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Query for signal instances containing the entity within the search window
    signal_instances = (
        db_session.query(SignalInstance)
        .options(joinedload(SignalInstance.signal))
        .join(SignalInstance.entities)
        .filter(SignalInstance.created_at >= start_date)
        .filter(SignalInstance.signal_id == signal_id)
        .filter(Entity.id.in_(entity_ids))
        .all()
    )

    return signal_instances


EntityTypePair = NewType(
    "EntityTypePair",
    NamedTuple(
        "EntityTypePairTuple",
        [
            ("entity_type", EntityType),
            ("regex", Union[re.Pattern[str], None]),
            ("json_path", Union[jsonpath_ng.JSONPath, None]),
        ],
    ),
)


def find_entities(
    db_session: Session, signal_instance: SignalInstance, entity_types: Sequence[EntityType]
) -> list[Entity]:
    """
    Find entities in a SignalInstance based on a list of EntityTypes.

    Args:
        db_session (Session): The database session to use for entity creation.
        signal_instance (SignalInstance): The SignalInstance to extract entities from.
        entity_types (Sequence[EntityType]): A list of EntityTypes to search for in the SignalInstance.

    Returns:
        list[Entity]: A list of entities found in the SignalInstance.
    """

    def _find_entities_by_jsonpath_expression(
        signal_instance: SignalInstance,
        entity_type_pairs: list[EntityTypePair],
    ) -> Generator[EntityCreate, None, None]:
        """
        Yield entities found in a SignalInstance by searching its fields using regular expressions and JSONPath expressions.

        Args:
            signal_instance: The SignalInstance to extract entities from.
            entity_type_pairs: A list of (entity_type, entity_regex, jpath) tuples to search for.

        Yields:
            EntityCreate: An entity found in the SignalInstance.
        """
        for entity_type, _, jpath in entity_type_pairs:
            if jpath:
                try:
                    matches = jpath.find(signal_instance.raw)
                    for match in matches:
                        if isinstance(match.value, str):
                            yield EntityCreate(
                                value=match.value,
                                entity_type=entity_type,
                                project=signal_instance.project,
                            )

                except KeyError:
                    log.warning(
                        f"Unable to extract entity {str(jpath)} is not a valid JSONPath for Instance {signal_instance.id}."
                        f"A KeyError usually occurs when the JSONPath includes a list index lookup against a dictionary value."
                        f"  Example: dictionary[0].value"
                    )
                    continue
                except Exception as e:  # Add this to handle general exceptions
                    log.exception(
                        f"An error occurred while extracting entity {str(jpath)} from Instance {signal_instance.id}: {str(e)}"
                    )
                    continue

    # Create a list of (entity type, regular expression, jpath) tuples
    entity_type_pairs = [
        (
            type,
            re.compile(type.regular_expression) if type.regular_expression else None,
            jsonpath_ng.parse(type.jpath) if type.jpath else None,
        )
        for type in entity_types
        if isinstance(type.regular_expression, str) or type.jpath is not None
    ]

    entities = []

    entities.extend(_find_entities_by_jsonpath_expression(signal_instance, entity_type_pairs))

    # Filter out duplicate entities
    entities = list(set(entities))

    entities_out = [
        get_by_value_or_create(db_session=db_session, entity_in=entity_in) for entity_in in entities
    ]

    return entities_out
