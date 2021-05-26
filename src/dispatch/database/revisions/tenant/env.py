from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, inspect


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


def is_tenant_table(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if not object.schema:
            return True
    return False


def is_tenant_schema(name, type_, parent_names):
    if type_ == "schema":
        if name.startswith("dispatch_organization_"):
            return True
    return False


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    print("Migrating dispatch tenant schemas...\n")

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=is_tenant_schema,
            include_object=is_tenant_table,
        )


if context.is_offline_mode():
    print("Can't run migrations offline")
else:
    run_migrations_online()
