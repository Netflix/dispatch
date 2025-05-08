"""
.. module: dispatch.database.core
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import functools
import re
from contextlib import contextmanager

from fastapi import Depends
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, object_session, sessionmaker, DeclarativeBase, declared_attr
from sqlalchemy.sql.expression import true
from sqlalchemy_utils import get_mapper
from starlette.requests import Request

from dispatch import config
from dispatch.search.fulltext import make_searchable
from dispatch.database.logging import SessionTracker


def create_db_engine(connection_string: str):
    """Create a database engine with proper timeout settings.

    Args:
        connection_string: Database connection string
    """
    url = make_url(connection_string)

    # Use existing configuration values with fallbacks
    timeout_kwargs = {
        # Connection timeout - how long to wait for a connection from the pool
        "pool_timeout": config.DATABASE_ENGINE_POOL_TIMEOUT,
        # Recycle connections after this many seconds
        "pool_recycle": config.DATABASE_ENGINE_POOL_RECYCLE,
        # Maximum number of connections to keep in the pool
        "pool_size": config.DATABASE_ENGINE_POOL_SIZE,
        # Maximum overflow connections allowed beyond pool_size
        "max_overflow": config.DATABASE_ENGINE_MAX_OVERFLOW,
        # Connection pre-ping to verify connection is still alive
        "pool_pre_ping": config.DATABASE_ENGINE_POOL_PING,
    }
    return create_engine(url, **timeout_kwargs)


# Create the default engine with standard timeout
engine = create_db_engine(
    config.SQLALCHEMY_DATABASE_URI,
)

# Enable query timing logging
#
# Set up logging for query debugging
# logger = logging.getLogger(__name__)
#
# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     conn.info.setdefault("query_start_time", []).append(time.time())
#     logger.debug("Start Query: %s", statement)

# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#     total = time.time() - conn.info["query_start_time"].pop(-1)
#     logger.debug("Query Complete!")
#     logger.debug("Total Time: %f", total)
#     # Log queries that take more than 1 second as warnings
#     if total > 1.0:
#         logger.warning("Slow Query (%.2fs): %s", total, statement)


SessionLocal = sessionmaker(bind=engine)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


raise_attribute_error = object()


def resolve_attr(obj, attr, default=None):
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    __repr_attrs__ = []
    __repr_max_length__ = 15

    @declared_attr.directive
    def __tablename__(cls):
        return resolve_table_name(cls.__name__)

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self):
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self):
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in __repr__attrs__".format(self.__class__, key)
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self):
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )
make_searchable(Base.metadata)


def get_db(request: Request) -> Session:
    """Get database session from request state."""
    session = request.state.db
    if not hasattr(session, "_dispatch_session_id"):
        session._dispatch_session_id = SessionTracker.track_session(
            session, context="fastapi_request"
        )
    return session


DbSession = Annotated[Session, Depends(get_db)]


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""

    def _find_class(name):
        for mapper in Base.registry.mappers:
            cls = mapper.class_
            if hasattr(cls, "__table__"):
                if cls.__table__.fullname.lower() == name.lower():
                    return cls

    mapped_name = resolve_table_name(table_fullname)
    mapped_class = _find_class(mapped_name)

    # try looking in the 'dispatch_core' schema
    if not mapped_class:
        mapped_class = _find_class(f"dispatch_core.{mapped_name}")

    if not mapped_class:
        raise ValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("filter",),
                    "msg": "Model not found. Check the name of your model.",
                }
            ],
            model=BaseModel,
        )

    return mapped_class


def get_table_name_by_class_instance(class_instance: Base) -> str:
    """Returns the name of the table for a given class instance."""
    return class_instance._sa_instance_state.mapper.mapped_table.name


def ensure_unique_default_per_project(target, value, oldvalue, initiator):
    """Ensures that only one row in table is specified as the default."""
    session = object_session(target)
    if session is None:
        return

    mapped_cls = get_mapper(target)

    if value:
        previous_default = (
            session.query(mapped_cls)
            .filter(mapped_cls.columns.default == true())
            .filter(mapped_cls.columns.project_id == target.project_id)
            .one_or_none()
        )
        if previous_default:
            # we want exclude updating the current default
            if previous_default.id != target.id:
                previous_default.default = False
                session.commit()


def refetch_db_session(organization_slug: str) -> Session:
    """Create a new database session for a specific organization."""
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization_slug}",
        }
    )
    session = sessionmaker(bind=schema_engine)()
    session._dispatch_session_id = SessionTracker.track_session(
        session, context=f"organization_{organization_slug}"
    )
    return session


@contextmanager
def get_session() -> Session:
    """Context manager to ensure the session is closed after use."""
    session = SessionLocal()
    session_id = SessionTracker.track_session(session, context="context_manager")
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        SessionTracker.untrack_session(session_id)
        session.close()


@contextmanager
def get_organization_session(organization_slug: str) -> Session:
    """Context manager to ensure the organization session is closed after use."""
    session = refetch_db_session(organization_slug)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        if hasattr(session, "_dispatch_session_id"):
            SessionTracker.untrack_session(session._dispatch_session_id)
        session.close()
