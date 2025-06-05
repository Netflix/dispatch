from alembic import context
from sqlalchemy import create_engine, text

from dispatch.logging import logging
from dispatch.config import SQLALCHEMY_DATABASE_URI
from dispatch.database.core import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
log = logging.getLogger(__name__)


config.set_main_option("sqlalchemy.url", str(SQLALCHEMY_DATABASE_URI))

target_metadata = Base.metadata  # noqa

CORE_SCHEMA_NAME = "dispatch_core"


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema == CORE_SCHEMA_NAME
    return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    def process_revision_directives(context, revision, directives):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            log.info("No changes found skipping revision creation.")

    connectable = create_engine(SQLALCHEMY_DATABASE_URI)

    log.info("Migrating dispatch core schema...")
    # migrate common tables
    with connectable.connect() as connection:
        set_search_path = text(f'set search_path to "{CORE_SCHEMA_NAME}"')
        connection.execute(set_search_path)
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    log.info("Can't run migrations offline")
else:
    run_migrations_online()
