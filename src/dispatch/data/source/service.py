from typing import Optional, List
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.incident import service as incident_service
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.data.query import service as query_service
from dispatch.data.source.environment import service as environment_service
from dispatch.data.source.data_format import service as data_format_service
from dispatch.data.source.status import service as status_service
from dispatch.data.source.type import service as type_service
from dispatch.data.source.transport import service as transport_service


from .models import Source, SourceCreate, SourceUpdate, SourceRead


def get(*, db_session, source_id: int) -> Optional[Source]:
    """Gets a source by its id."""
    return db_session.query(Source).filter(Source.id == source_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Source]:
    """Gets a source by its name."""
    return (
        db_session.query(Source)
        .filter(Source.name == name)
        .filter(Source.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id, source_in: SourceRead) -> SourceRead:
    """Returns the source specified or raises ValidationError."""
    source = get_by_name(db_session=db_session, project_id=project_id, name=source_in.name)

    if not source:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Source not found.",
                        source=source_in.name,
                    ),
                    loc="source",
                )
            ],
            model=SourceRead,
        )

    return source


def get_all(*, db_session, project_id: int) -> List[Optional[Source]]:
    """Gets all sources."""
    return db_session.query(Source).filter(Source.project_id == project_id)


def create(*, db_session, source_in: SourceCreate) -> Source:
    """Creates a new source."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_in.project
    )

    source = Source(
        **source_in.dict(
            exclude={
                "project",
                "owner",
                "tags",
                "incidents",
                "queries",
                "source_environment",
                "source_data_format",
                "source_transport",
                "source_status",
                "source_type",
            }
        ),
        project=project,
    )

    if source_in.owner:
        source.owner = service_service.get_by_name_or_raise(
            db_session=db_session, project_id=project.id, service_in=source_in.owner
        )

    tags = []
    for t in source_in.tags:
        tags.append(
            tag_service.get_by_name_or_raise(db_session=db_session, tag_in=t, project_id=project.id)
        )
    source.tags = tags

    incidents = []
    for i in source_in.incidents:
        incidents.append(
            incident_service.get_by_name_or_raise(
                db_session=db_session, incident_in=i, project_id=project.id
            )
        )
    source.incidents = incidents

    queries = []
    for q in source_in.queries:
        queries.append(
            query_service.get_by_name_or_raise(
                db_session=db_session, query_in=q, project_id=project.id
            )
        )
    source.queries = queries

    if source_in.source_environment:
        source.source_environment = environment_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=project.id,
            source_environment_in=source_in.source_environment,
        )

    if source_in.source_type:
        source.source_type = type_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=project.id,
            source_type_in=source_in.source_type,
        )

    if source_in.source_transport:
        source.source_transport = transport_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=project.id,
            source_transport_in=source_in.source_transport,
        )

    if source_in.source_data_format:
        source.source_data_format = data_format_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=project.id,
            source_data_format_in=source_in.source_data_format,
        )

    if source_in.source_status:
        source.source_status = status_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=project.id,
            source_status_in=source_in.source_status,
        )

    db_session.add(source)
    db_session.commit()
    return source


def get_or_create(*, db_session, source_in: SourceCreate) -> Source:
    """Gets or creates a new source."""
    # prefer the source id if available
    if source_in.id:
        q = db_session.query(Source).filter(Source.id == source_in.id)
    else:
        q = db_session.query(Source).filter_by(name=source_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, source_in=source_in)


def update(*, db_session, source: Source, source_in: SourceUpdate) -> Source:
    """Updates an existing source."""
    source_data = source.dict()

    update_data = source_in.dict(
        skip_defaults=True,
        exclude={
            "project",
            "owner",
            "tags",
            "incidents",
            "queries",
            "source_environment",
            "source_data_format",
            "source_transport",
            "source_status",
            "source_type",
        },
    )

    if source_in.owner:
        source.owner = service_service.get_by_name_or_raise(
            db_session=db_session, project_id=source.project.id, service_in=source_in.owner
        )

    tags = []
    for t in source_in.tags:
        tags.append(
            tag_service.get_by_name_or_raise(
                db_session=db_session, tag_in=t, project_id=source.project.id
            )
        )

    source.tags = tags

    incidents = []
    for i in source_in.incidents:
        incidents.append(
            incident_service.get_by_name_or_raise(
                db_session=db_session, incident_in=i, project_id=source.project.id
            )
        )
    source.incidents = incidents

    queries = []
    for q in source_in.queries:
        queries.append(
            query_service.get_by_name_or_raise(
                db_session=db_session, query_in=q, project_id=source.project.id
            )
        )
    source.queries = queries

    if source_in.source_environment:
        source.source_environment = environment_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=source.project.id,
            source_environment_in=source_in.source_environment,
        )

    if source_in.source_type:
        source.source_type = type_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=source.project.id,
            source_type_in=source_in.source_type,
        )

    if source_in.source_transport:
        source.source_transport = transport_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=source.project.id,
            source_transport_in=source_in.source_transport,
        )

    if source_in.source_data_format:
        source.source_data_format = data_format_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=source.project.id,
            source_data_format_in=source_in.source_data_format,
        )

    if source_in.source_status:
        source.source_status = status_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=source.project.id,
            source_status_in=source_in.source_status,
        )

    for field in source_data:
        if field in update_data:
            setattr(source, field, update_data[field])

    db_session.commit()
    return source


def delete(*, db_session, source_id: int):
    """Deletes an existing source."""
    source = db_session.query(Source).filter(Source.id == source_id).one_or_none()
    db_session.delete(source)
    db_session.commit()
