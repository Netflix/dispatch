from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool


from dispatch.config import SQLALCHEMY_DATABASE_URI
from dispatch.database.core import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)


config.set_main_option("sqlalchemy.url", str(SQLALCHEMY_DATABASE_URI))


target_metadata = Base.metadata  # noqa
default_schema_name = "dispatch_organization_default"


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if reflected and compare_to is None:
            return False

        if not object.schema:
            return True
    else:
        return True


def include_name(name, type_, parent_names):
    if type_ == "schema":
        if name in [default_schema_name]:
            return True
    else:
        return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # don't create empty revisions
    def process_revision_directives(context, revision, directives):
        if config.cmd_opts.autogenerate:
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []

    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    print("Migrating dispatch tenant schemas...\n")

    with connectable.connect() as connection:

        for tenant_schema_name in ["dispatch_organization_default"]:
            print(f"Migrating dispatch tenant schema {tenant_schema_name}...\n")
            connection.dialect.default_schema_name = tenant_schema_name
            connection.execute(f'set search_path to "{tenant_schema_name}"')

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                include_schemas=True,
                include_object=include_object,
                # include_name=include_name,
                process_revision_directives=process_revision_directives,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    print("Can't run migrations offline")
else:
    run_migrations_online()
