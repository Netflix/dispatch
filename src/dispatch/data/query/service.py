from pydantic import ValidationError

from dispatch.project import service as project_service
from dispatch.tag import service as tag_service
from dispatch.data.source import service as source_service

from .models import Query, QueryCreate, QueryUpdate, QueryRead


def get(*, db_session, query_id: int) -> Query | None:
    """Gets a query by its id."""
    return db_session.query(Query).filter(Query.id == query_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Query | None:
    """Gets a query by its name."""
    return (
        db_session.query(Query)
        .filter(Query.name == name)
        .filter(Query.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, query_in: QueryRead, project_id: int) -> QueryRead:
    """Returns the query specified or raises ValidationError."""
    query = get_by_name(db_session=db_session, name=query_in.name, project_id=project_id)

    if not query:
        raise ValidationError([
            {
                "loc": ("query",),
                "msg": f"Query not found: {query_in.name}",
                "type": "value_error",
                "input": query_in.name,
            }
        ])

    return query


def get_all(*, db_session):
    """Gets all queries."""
    return db_session.query(Query)


def create(*, db_session, query_in: QueryCreate) -> Query:
    """Creates a new query."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=query_in.project
    )

    source = source_service.get_by_name_or_raise(
        db_session=db_session, project_id=project.id, source_in=query_in.source
    )

    tags = []
    for t in query_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    query = Query(
        **query_in.dict(exclude={"project", "tags", "source"}),
        source=source,
        tags=tags,
        project=project,
    )
    db_session.add(query)
    db_session.commit()
    return query


def get_or_create(*, db_session, query_in: QueryCreate) -> Query:
    """Gets or creates a new query."""
    # prefer the query id if available
    if query_in.id:
        q = db_session.query(Query).filter(Query.id == query_in.id)
    else:
        q = db_session.query(Query).filter_by(name=query_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, query_in=query_in)


def update(*, db_session, query: Query, query_in: QueryUpdate) -> Query:
    """Updates an existing query."""
    query_data = query.dict()
    update_data = query_in.dict(exclude_unset=True, exclude={})

    source = source_service.get_by_name_or_raise(
        db_session=db_session, project_id=query.project.id, source_in=query_in.source
    )

    tags = []
    for t in query_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    for field in query_data:
        if field in update_data:
            setattr(query, field, update_data[field])

    query.tags = tags
    query.source = source
    db_session.commit()
    return query


def delete(*, db_session, query_id: int):
    """Deletes an existing query."""
    query = db_session.query(Query).filter(Query.id == query_id).one_or_none()
    db_session.delete(query)
    db_session.commit()
