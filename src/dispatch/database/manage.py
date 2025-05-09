import os
import logging

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateSchema, Table
from sqlalchemy_utils import create_database, database_exists

from dispatch import config
from dispatch.organization.models import Organization
from dispatch.project.models import Project
from dispatch.plugin.models import Plugin
from dispatch.search import fulltext
from dispatch.search.fulltext import (
    sync_trigger,
)

from .core import Base, sessionmaker
from .enums import DISPATCH_ORGANIZATION_SCHEMA_PREFIX


log = logging.getLogger(__file__)


def version_schema(script_location: str):
    """Applies alembic versioning to schema."""

    # add it to alembic table
    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_command.stamp(alembic_cfg, "head")


def get_core_tables()  -> list[Table]:
    """Fetches tables that belong to the 'dispatch_core' schema."""
    core_tables: list[Table] = []
    for _, table in Base.metadata.tables.items():
        if table.schema == "dispatch_core":
            core_tables.append(table)
    return core_tables


def get_tenant_tables() -> list[Table]:
    """Fetches tables that belong to their own tenant tables."""
    tenant_tables: list[Table] = []
    for _, table in Base.metadata.tables.items():
        if not table.schema:
            tenant_tables.append(table)
    return tenant_tables


def init_database(engine: Engine):
    """Initializes the database."""
    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        create_database(str(config.SQLALCHEMY_DATABASE_URI))

    schema_name = "dispatch_core"
    with engine.begin() as connection:
        connection.execute(CreateSchema(schema_name, if_not_exists=True))

    tables = get_core_tables()

    Base.metadata.create_all(engine, tables=tables)

    version_schema(script_location=config.ALEMBIC_CORE_REVISION_PATH)
    with engine.connect() as connection:
        setup_fulltext_search(connection, tables)

    # setup an required database functions
    session = sessionmaker(bind=engine)
    db_session = session()

    # we create the default organization if it doesn't exist
    organization = (
        db_session.query(Organization).filter(Organization.name == "default").one_or_none()
    )
    if not organization:
        print("Creating default organization...")
        organization = Organization(
            name="default",
            slug="default",
            default=True,
            description="Default Dispatch organization.",
        )

        db_session.add(organization)
        db_session.commit()

    # we initialize the database schema
    init_schema(engine=engine, organization=organization)

    # we install all plugins
    from dispatch.common.utils.cli import install_plugins
    from dispatch.plugins.base import plugins

    install_plugins()

    for p in plugins.all():
        plugin = Plugin(
            title=p.title,
            slug=p.slug,
            type=p.type,
            version=p.version,
            author=p.author,
            author_url=p.author_url,
            multiple=p.multiple,
            description=p.description,
        )
        db_session.add(plugin)
    db_session.commit()

    # we create the default project if it doesn't exist
    project = db_session.query(Project).filter(Project.name == "default").one_or_none()
    if not project:
        print("Creating default project...")
        project = Project(
            name="default",
            default=True,
            description="Default Dispatch project.",
            organization=organization,
        )
        db_session.add(project)
        db_session.commit()

        # we initialize the project with defaults
        from dispatch.project import flows as project_flows

        print("Initializing default project...")
        project_flows.project_init_flow(
            project_id=project.id, organization_slug=organization.slug, db_session=db_session
        )


def init_schema(*, engine: Engine, organization: Organization) -> Organization:
    """Initializes a new schema."""
    schema_name = f"{DISPATCH_ORGANIZATION_SCHEMA_PREFIX}_{organization.slug}"

    with engine.begin() as connection:
        connection.execute(CreateSchema(schema_name, if_not_exists=True))

    # set the schema for table creation
    tables = get_tenant_tables()

    # alter each table's schema
    for t in tables:
        t.schema = schema_name

    Base.metadata.create_all(engine, tables=tables)

    # put schema under version control
    version_schema(script_location=config.ALEMBIC_TENANT_REVISION_PATH)

    with engine.connect() as connection:
        # we need to map this for full text search as it uses sql literal strings
        # and schema translate map does not apply
        for t in tables:
            t.schema = schema_name

        setup_fulltext_search(connection, tables)

    session = sessionmaker(bind=engine)
    db_session = session()

    organization = db_session.merge(organization)
    db_session.add(organization)
    db_session.commit()
    return organization


def setup_fulltext_search(connection: Connection, tables: list[Table]) -> None:
    """Syncs any required fulltext table triggers and functions."""
    # parsing functions
    function_path = os.path.join(
        os.path.dirname(os.path.abspath(fulltext.__file__)), "expressions.sql"
    )
    connection.execute(text(open(function_path).read()))

    for table in tables:
        table_triggers = []
        for column in table.columns:
            if column.name.endswith("search_vector"):
                if hasattr(column.type, "columns"):
                    table_triggers.append(
                        {
                            "conn": connection,
                            "table": table,
                            "tsvector_column": "search_vector",
                            "indexed_columns": column.type.columns,
                        }
                    )
                else:
                    log.warning(
                        f"Column search_vector defined but no index columns found. Table: {table.name}"
                    )

        for trigger in table_triggers:
            sync_trigger(**trigger)
