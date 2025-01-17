import functools
import logging
from datetime import datetime

from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, event
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import sessionmaker, Session
from starlette.requests import Request
from dispatch.database.base import Base

from dispatch import config

from dispatch.audit.models import Audit

log = logging.getLogger(__name__)

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_size=config.DATABASE_ENGINE_POOL_SIZE,
    max_overflow=config.DATABASE_ENGINE_MAX_OVERFLOW,
    pool_pre_ping=config.DATABASE_ENGINE_POOL_PING,
)

SessionLocal = sessionmaker(bind=engine)

raise_attribute_error = object()


def resolve_attr(obj, attr, default=None):
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


def get_db(request: Request):
    return request.state.db


DbSession = Annotated[Session, Depends(get_db)]


def serialize_value(value):
    """Helper function to serialize values, especially datetime objects."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        return value.isoformat(timespec="seconds")
    elif isinstance(value, Base) or isinstance(value, BaseModel):
        return {k: serialize_value(v) for k, v in value.dict().items()}
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(v) for v in value]
    return value


tracked_classes = [
    "CasePriority",
    "CaseSeverity",
    "CaseType",
    "Entity",
    "EntityType",
    "IncidentPriority",
    "IncidentSeverity",
    "IncidentType",
    "Organization",
    "Signal",
    "Service",
    "Workflow",
]


def track_changes(session, instances, flush_context, inspect=sqlalchemy_inspect):
    """
    Tracks changes to specified ORM instances within a SQLAlchemy session and logs them to an audit table.

    This function is designed to be used as an event listener for SQLAlchemy's "before_flush" event.
    It inspects changes to instances of specified classes within the session and records these changes
    in an audit log.

    Parameters:
    - session (Session): The SQLAlchemy session that is being flushed. This session contains the instances
    that are being tracked for changes.
    - instances (list): A list of instances that are being flushed. This parameter is not used directly
    in the function but is part of the event listener signature.
    - flush_context (FlushContext): The flush context provided by SQLAlchemy during the flush operation.
    This parameter is not used directly in the function but is part of the event listener signature.
    - inspect (function): A function used to inspect ORM instances. By default, this is set to
    `sqlalchemy.inspect`. This parameter is included to allow for easier testing by enabling the
    injection of a mock inspect function during unit tests.

    Behavior:
    - The function iterates over all "dirty" instances in the session, which are instances that have
    been modified.
    - For each instance, it checks if the class name is in the list of tracked classes.
    - It uses the `inspect` function to get the state of the instance and iterates over its attributes.
    - For each attribute, it retrieves the history of changes and records any modifications.
    - If changes are detected, they are serialized and added to an audit log entry, which is then
    added to the session.

    Exceptions:
    - The function catches and logs any exceptions that occur during the change tracking process,
    ensuring that the audit logging does not interfere with the main transaction.

    Note:
    - The `inspect` parameter is added to facilitate testing by allowing the injection of a mock
    inspect function. This makes it easier to simulate and verify the behavior of the function
    in a controlled test environment.
    - The `no_autoflush` block is used to prevent the session from automatically flushing changes
    to the database while the function is executing. This is important to avoid premature flushing
    that could interfere with the change tracking process, ensuring that all changes are captured
    accurately before any database operations are committed.
    - The `serialize_value` function is used to convert complex data types, such as datetime objects
    and Pydantic models, into JSON-serializable formats. This ensures that all changes can be
    stored in the audit log as JSON. By serializing values, the function can handle a wide range of
    data types and maintain the integrity of the audit log.
    """
    changes = {}
    id = None
    user = None
    tablename = ""
    with session.no_autoflush:
        try:
            for instance in session.dirty:
                if instance.__class__.__name__ in tracked_classes:
                    state = inspect(instance)
                    tablename = instance.__class__.__name__
                    for attr in state.attrs:
                        try:
                            hist = state.get_history(attr.key, True)
                        except Exception:
                            pass
                        if hist:
                            if attr.key == "id":
                                id = hist.unchanged[0]
                            if hist.has_changes():
                                key = f"{instance.__class__.__name__}.{attr.key}"
                                old = serialize_value(hist.deleted[0]) if hist.deleted else None
                                new = serialize_value(hist.added[0]) if hist.added else None
                                if old != new:
                                    changes[key] = {
                                        "old": old,
                                        "new": new,
                                    }
                    get_user = getattr(session, "user", None)
                    if get_user:
                        user = get_user
            if changes and user:
                log_entry = Audit(
                    table_name=tablename,
                    changed_data=changes,
                    record_id=id,
                    dispatch_user=user,
                )
                session.add(log_entry)
        except Exception as e:
            log.exception(
                f"Error logging changes in audit table. Changes to {tablename} with id {id}: {changes} by user {user} | error: {e}"
            )


# register event listener for database
event.listen(Session, "before_flush", track_changes)


def refetch_db_session(organization_slug: str) -> Session:
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization_slug}",
        }
    )
    db_session = sessionmaker(bind=schema_engine)()
    return db_session


@contextmanager
def get_session():
    """Context manager to ensure the session is closed after use."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_organization_session(organization_slug: str):
    """Context manager to ensure the session is closed after use."""
    session = refetch_db_session(organization_slug)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
