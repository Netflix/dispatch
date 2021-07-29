from typing import List, Optional

from dispatch.project import service as project_service
from dispatch.term import service as term_service

from .models import Definition, DefinitionCreate, DefinitionUpdate


def get(*, db_session, definition_id: int) -> Optional[Definition]:
    """Gets a definition by its id."""
    return db_session.query(Definition).filter(Definition.id == definition_id).first()


def get_by_text(*, db_session, text: str) -> Optional[Definition]:
    """Gets a definition by its text."""
    return db_session.query(Definition).filter(Definition.text == text).first()


def get_all(*, db_session) -> List[Optional[Definition]]:
    """Gets all definitions."""
    return db_session.query(Definition)


def create(*, db_session, definition_in: DefinitionCreate) -> Definition:
    """Creates a new definition."""
    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t) for t in definition_in.terms
    ]

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=definition_in.project
    )
    definition = Definition(
        **definition_in.dict(exclude={"terms", "project"}), project=project, terms=terms
    )
    db_session.add(definition)
    db_session.commit()
    return definition


def create_all(*, db_session, definitions_in: List[DefinitionCreate]) -> List[Definition]:
    """Creates a definitions in bulk."""
    definitions = [Definition(text=d.text) for d in definitions_in]
    db_session.bulk_save_insert(definitions)
    db_session.commit()
    db_session.refresh()
    return definitions


def update(*, db_session, definition: Definition, definition_in: DefinitionUpdate) -> Definition:
    """Updates a definition."""
    definition_data = definition.dict()

    terms = [
        term_service.get_or_create(db_session=db_session, term_in=t) for t in definition_in.terms
    ]
    update_data = definition_in.dict(skip_defaults=True, exclude={"terms"})

    for field in definition_data:
        if field in update_data:
            setattr(definition, field, update_data[field])

    definition.terms = terms

    db_session.commit()
    return definition


def delete(*, db_session, definition_id: int):
    """Deletes a definition."""
    definition = db_session.query(Definition).filter(Definition.id == definition_id).first()
    definition.terms = []
    db_session.delete(definition)
    db_session.commit()


def upsert(*, db_session, definition_in: DefinitionCreate) -> Definition:
    """Gets or creates a new definition."""
    # we only care about unique columns
    q = db_session.query(Definition).filter(Definition.text == definition_in.text)
    instance = q.first()

    # there are no updatable fields
    if instance:
        return instance

    return create(db_session=db_session, definition_in=definition_in)
