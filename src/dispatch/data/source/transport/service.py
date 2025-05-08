from pydantic import ValidationError

from dispatch.project import service as project_service

from .models import (
    SourceTransport,
    SourceTransportCreate,
    SourceTransportUpdate,
    SourceTransportRead,
)


def get(*, db_session, source_transport_id: int) -> SourceTransport | None:
    """Gets a source transport by its id."""
    return (
        db_session.query(SourceTransport)
        .filter(SourceTransport.id == source_transport_id)
        .one_or_none()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> SourceTransport | None:
    """Gets a source transport by its name."""
    return (
        db_session.query(SourceTransport)
        .filter(SourceTransport.name == name)
        .filter(SourceTransport.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_transport_in=SourceTransportRead
) -> SourceTransportRead:
    """Returns the source transport specified or raises ValidationError."""
    source = get_by_name(
        db_session=db_session, project_id=project_id, name=source_transport_in.name
    )

    if not source:
        raise ValidationError([
            {
                "loc": ("source",),
                "msg": f"SourceTransport not found: {source_transport_in.name}",
                "type": "value_error",
                "input": source_transport_in.name,
            }
        ])

    return source


def get_all(*, db_session, project_id: int) -> list[SourceTransport | None]:
    """Gets all source transports."""
    return db_session.query(SourceTransport).filter(SourceTransport.project_id == project_id)


def create(*, db_session, source_transport_in: SourceTransportCreate) -> SourceTransport:
    """Creates a new source transport."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_transport_in.project
    )
    source_transport = SourceTransport(
        **source_transport_in.dict(exclude={"project"}), project=project
    )
    db_session.add(source_transport)
    db_session.commit()
    return source_transport


def get_or_create(*, db_session, source_transport_in: SourceTransportCreate) -> SourceTransport:
    """Gets or creates a new source transport."""
    # prefer the source id if available
    if source_transport_in.id:
        q = db_session.query(SourceTransport).filter(SourceTransport.id == source_transport_in.id)
    else:
        q = db_session.query(SourceTransport).filter_by(name=source_transport_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(
        db_session=db_session,
        source_transport_in=source_transport_in,
    )


def update(
    *,
    db_session,
    source_transport: SourceTransport,
    source_transport_in: SourceTransportUpdate,
) -> SourceTransport:
    """Updates an existing source transport."""
    source_transport_data = source_transport.dict()
    update_data = source_transport_in.dict(exclude_unset=True, exclude={})

    for field in source_transport_data:
        if field in update_data:
            setattr(source_transport, field, update_data[field])

    db_session.commit()
    return source_transport


def delete(*, db_session, source_transport_id: int):
    """Deletes an existing source transport."""
    source_transport = (
        db_session.query(SourceTransport)
        .filter(SourceTransport.id == source_transport_id)
        .one_or_none()
    )
    db_session.delete(source_transport)
    db_session.commit()
