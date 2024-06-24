import os
from alembic import context
from sqlalchemy import engine_from_config, pool, inspect


from dispatch.logging import logging
from dispatch.config import SQLALCHEMY_DATABASE_URI
from dispatch.database.core import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
log = logging.getLogger(__name__)

config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URI)

target_metadata = Base.metadata


def get_tenant_schemas(connection):
    tenant_schemas = []
    for s in inspect(connection).get_schema_names():
        if s.startswith("dispatch_organization_"):
            tenant_schemas.append(s)
    return tenant_schemas


# produce an include object function that filters on the given schemas
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if object.schema:
            return False
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

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={'options': '-c lock_timeout=4000 -c statement_timeout=5000'}
    )

    with connectable.connect() as connection:
        # get the schema names
        for schema in get_tenant_schemas(connection):
            log.info(f"Migrating {schema}...")
            connection.execute(f'set search_path to "{schema}"')
            connection.dialect.default_schema_name = schema

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                transaction_per_migration=True,
                process_revision_directives=process_revision_directives,
            )

            with context.begin_transaction():
                context.run_migrations()

            if context.config.cmd_opts:
                if context.config.cmd_opts.cmd == "revision":
                    break


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    # Get the URL from the config
    url = config.get_main_option("sqlalchemy.url")

    # Set the migration options
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_schemas=True,
        include_object=include_object,
        literal_binds=True,  # Binds parameters with their string values
    )

    # Start a transaction and run migrations
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
