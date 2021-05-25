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

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        print()
        print("-" * 80)
        print("Migrating schema 'dispatch'\n")

        with context.begin_transaction():
            context.run_migrations()

        try:
            # get the schema names
            tenant_schemas = inspect(connection).get_schema_names()

            # attempt to migrate all project tenant schemas
            for schema in tenant_schemas:
                if schema.startswith("dispatch_organization."):
                    print()
                    print("-" * 80)
                    print(f"Migrating schema '{schema}'\n")
                    connection.execute(f'set search_path to "{schema}", dispatch')
                    with context.begin_transaction():
                        context.run_migrations()
        finally:
            connection.close()


if context.is_offline_mode():
    print("Can't run migrations offline")
else:
    run_migrations_online()
