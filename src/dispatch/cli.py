import logging
import os
import sys

import click
import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from tabulate import tabulate

from dispatch import __version__, config

from .main import *  # noqa
from .database import Base, engine
from .exceptions import DispatchException
from .plugins.base import plugins
from .scheduler import scheduler
from .logging import configure_logging

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

log = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
@click.version_option(version=__version__)
def dispatch_cli():
    """Command-line interface to Dispatch."""
    configure_logging()


@dispatch_cli.group("plugins")
def plugins_group():
    """All commands for plugin manipulation."""
    pass


@plugins_group.command("list")
def list_plugins():
    """Shows all available plugins"""
    from dispatch.database import SessionLocal
    from dispatch.plugin import service as plugin_service

    db_session = SessionLocal()
    table = []
    for p in plugins.all():
        record = plugin_service.get_by_slug(db_session=db_session, slug=p.slug)

        if not record:
            log.warning(
                f"Plugin {p.slug} available, but not installed. Run `dispatch plugins install` to install it."
            )
            continue

        table.append(
            [
                record.title,
                record.slug,
                record.version,
                record.enabled,
                record.type,
                record.author,
                record.description,
            ]
        )

    click.secho(
        tabulate(
            table,
            headers=[
                "Title",
                "Slug",
                "Version",
                "Enabled",
                "Type",
                "Author",
                "Description",
            ],
        ),
        fg="blue",
    )


@plugins_group.command("install")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force a plugin to update all details about itself, this will overwrite the current database entry.",
)
def install_plugins(force):
    """Installs all plugins, or only one."""
    from dispatch.database import SessionLocal
    from dispatch.plugin import service as plugin_service
    from dispatch.plugin.models import Plugin

    db_session = SessionLocal()
    for p in plugins.all():
        record = plugin_service.get_by_slug(db_session=db_session, slug=p.slug)
        if not record:
            click.secho(f"Installing plugin... Slug: {p.slug} Version: {p.version}", fg="blue")
            record = Plugin(
                title=p.title,
                slug=p.slug,
                type=p.type,
                version=p.version,
                author=p.author,
                author_url=p.author_url,
                required=p.required,
                multiple=p.multiple,
                description=p.description,
                enabled=p.enabled,
            )
            db_session.add(record)

        if force:
            click.secho(f"Updating plugin... Slug: {p.slug} Version: {p.version}", fg="blue")
            # we only update values that should change
            record.tile = p.title
            record.version = p.version
            record.author = p.author
            record.author_url = p.author_url
            record.description = p.description
            record.required = p.required
            record.type = p.type
            db_session.add(record)

        db_session.commit()


def sync_triggers():
    from sqlalchemy_searchable import sync_trigger

    sync_trigger(engine, "definition", "search_vector", ["text"])
    sync_trigger(engine, "document", "search_vector", ["name"])
    sync_trigger(engine, "incident", "search_vector", ["name", "title", "description"])
    sync_trigger(engine, "incident_type", "search_vector", ["name", "description"])
    sync_trigger(
        engine, "individual_contact", "search_vector", ["name", "title", "company", "notes"]
    )
    sync_trigger(engine, "plugin", "search_vector", ["title"])
    sync_trigger(engine, "policy", "search_vector", ["name", "description"])
    sync_trigger(engine, "report", "search_vector", ["details_raw"])
    sync_trigger(engine, "service", "search_vector", ["name"])
    sync_trigger(engine, "tag", "search_vector", ["name"])
    sync_trigger(engine, "task", "search_vector", ["description"])
    sync_trigger(engine, "team_contact", "search_vector", ["name", "company", "notes"])
    sync_trigger(engine, "term", "search_vector", ["text"])
    sync_trigger(engine, "dispatch_user", "search_vector", ["email"])
    sync_trigger(engine, "workflow", "search_vector", ["name", "description"])


@dispatch_cli.group("database")
def dispatch_database():
    """Container for all dispatch database commands."""
    pass


@dispatch_database.command("sync-triggers")
def database_trigger_sync():
    """Ensures that all database triggers have been installed."""
    sync_triggers()

    click.secho("Success.", fg="green")


@dispatch_database.command("init")
def init_database():
    """Initializes a new database."""
    from sqlalchemy_utils import create_database, database_exists

    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        create_database(str(config.SQLALCHEMY_DATABASE_URI))
    Base.metadata.create_all(engine)
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.stamp(alembic_cfg, "head")

    sync_triggers()
    click.secho("Success.", fg="green")


@dispatch_database.command("restore")
@click.option(
    "--dump-file",
    default="dispatch-backup.dump",
    help="Path to a PostgreSQL text format dump file.",
)
def restore_database(dump_file):
    """Restores the database via psql."""
    from sh import psql, createdb, ErrorReturnCode_1
    from dispatch.config import (
        DATABASE_HOSTNAME,
        DATABASE_NAME,
        DATABASE_PORT,
        DATABASE_CREDENTIALS,
    )

    username, password = str(DATABASE_CREDENTIALS).split(":")

    try:
        print(
            createdb(
                "-h",
                DATABASE_HOSTNAME,
                "-p",
                DATABASE_PORT,
                "-U",
                username,
                DATABASE_NAME,
                _env={"PGPASSWORD": password},
            )
        )
    except ErrorReturnCode_1:
        print("Database already exists.")

    print(
        psql(
            "-h",
            DATABASE_HOSTNAME,
            "-p",
            DATABASE_PORT,
            "-U",
            username,
            "-d",
            DATABASE_NAME,
            "-f",
            dump_file,
            _env={"PGPASSWORD": password},
        )
    )
    click.secho("Success.", fg="green")


@dispatch_database.command("dump")
@click.option(
    "--dump-file",
    default="dispatch-backup.dump",
    help="Path to a PostgreSQL text format dump file.",
)
def dump_database(dump_file):
    """Dumps the database via pg_dump."""
    from sh import pg_dump
    from dispatch.config import (
        DATABASE_HOSTNAME,
        DATABASE_NAME,
        DATABASE_PORT,
        DATABASE_CREDENTIALS,
    )

    username, password = str(DATABASE_CREDENTIALS).split(":")

    pg_dump(
        "-f",
        dump_file,
        "-h",
        DATABASE_HOSTNAME,
        "-p",
        DATABASE_PORT,
        "-U",
        username,
        DATABASE_NAME,
        _env={"PGPASSWORD": password},
    )


@dispatch_database.command("drop")
@click.option("--yes", is_flag=True, help="Silences all confirmation prompts.")
def drop_database(yes):
    """Drops all data in database."""
    from sqlalchemy_utils import drop_database

    if yes:
        drop_database(str(config.SQLALCHEMY_DATABASE_URI))
        click.secho("Success.", fg="green")

    if click.confirm(
        f"Are you sure you want to drop: '{config.DATABASE_HOSTNAME}:{config.DATABASE_NAME}'?"
    ):
        drop_database(str(config.SQLALCHEMY_DATABASE_URI))
        click.secho("Success.", fg="green")


@dispatch_database.command("upgrade")
@click.option(
    "--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts."
)
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
def upgrade_database(tag, sql, revision):
    """Upgrades database schema to newest version."""
    from sqlalchemy_utils import database_exists, create_database
    from alembic.migration import MigrationContext

    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        create_database(str(config.SQLALCHEMY_DATABASE_URI))
        Base.metadata.create_all(engine)
        alembic_command.stamp(alembic_cfg, "head")
    else:
        conn = engine.connect()
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
        if not current_rev:
            Base.metadata.create_all(engine)
            alembic_command.stamp(alembic_cfg, "head")
        else:
            alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)
    sync_triggers()
    click.secho("Success.", fg="green")


@dispatch_database.command("merge")
@click.argument("revisions", nargs=-1)
@click.option("--message")
def merge_revisions(revisions, message):
    """Combines two revisions."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.merge(alembic_cfg, revisions, message=message)


@dispatch_database.command("heads")
def head_database():
    """Shows the heads of the database."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.heads(alembic_cfg)


@dispatch_database.command("history")
def history_database():
    """Shows the history of the database."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.history(alembic_cfg)


@dispatch_database.command("downgrade")
@click.option(
    "--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts."
)
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
@click.option("--revision", nargs=1, default="head", help="Revision identifier.")
def downgrade_database(tag, sql, revision):
    """Downgrades database schema to next newest version."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)

    if sql and revision == "-1":
        revision = "head:-1"

    alembic_command.downgrade(alembic_cfg, revision, sql=sql, tag=tag)
    click.secho("Success.", fg="green")


@dispatch_database.command("stamp")
@click.argument("revision", nargs=1, default="head")
@click.option(
    "--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts."
)
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
def stamp_database(revision, tag, sql):
    """Forces the database to a given revision."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.stamp(alembic_cfg, revision, sql=sql, tag=tag)


@dispatch_database.command("revision")
@click.option(
    "-d", "--directory", default=None, help=('migration script directory (default is "migrations")')
)
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=(
        "Populate revision script with candidate migration "
        "operations, based on comparison of database to model"
    ),
)
@click.option(
    "--sql", is_flag=True, help=("Don't emit SQL to database - dump to standard output " "instead")
)
@click.option(
    "--head",
    default="head",
    help=("Specify head revision or <branchname>@head to base new " "revision on"),
)
@click.option(
    "--splice", is_flag=True, help=('Allow a non-head revision as the "head" to splice onto')
)
@click.option(
    "--branch-label", default=None, help=("Specify a branch label to apply to the new revision")
)
@click.option(
    "--version-path", default=None, help=("Specify specific path from config for version file")
)
@click.option(
    "--rev-id", default=None, help=("Specify a hardcoded revision id instead of generating " "one")
)
def revision_database(
    directory, message, autogenerate, sql, head, splice, branch_label, version_path, rev_id
):
    """Create new database revision."""
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.revision(
        alembic_cfg,
        message,
        autogenerate=autogenerate,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
    )


@dispatch_cli.group("scheduler")
def dispatch_scheduler():
    """Container for all dispatch scheduler commands."""
    # we need scheduled tasks to be imported
    from .document.scheduled import sync_document_terms  # noqa
    from .incident.scheduled import daily_summary, auto_tagger  # noqa
    from .report.scheduled import incident_report_reminders  # noqa
    from .tag.scheduled import sync_tags  # noqa
    from .task.scheduled import sync_tasks, create_task_reminders  # noqa
    from .term.scheduled import sync_terms  # noqa
    from .workflow.scheduled import sync_workflows, sync_active_stable_workflows  # noqa


@dispatch_scheduler.command("list")
def list_tasks():
    """Prints and runs all currently configured periodic tasks, in seperate event loop."""
    table = []
    for task in scheduler.registered_tasks:
        table.append([task["name"], task["job"].period, task["job"].at_time])

    click.secho(tabulate(table, headers=["Task Name", "Period", "At Time"]), fg="blue")


@dispatch_scheduler.command("start")
@click.argument("tasks", nargs=-1)
@click.option("--eager", is_flag=True, default=False, help="Run the tasks immediately.")
def start_tasks(tasks, eager):
    """Starts the scheduler."""
    if tasks:
        for task in scheduler.registered_tasks:
            if task["name"] not in tasks:
                scheduler.remove(task)

    if eager:
        for task in tasks:
            for r_task in scheduler.registered_tasks:
                if task == r_task["name"]:
                    click.secho(f"Eagerly running: {task}", fg="blue")
                    r_task["func"]()
                    break
            else:
                click.secho(f"Task not found. TaskName: {task}", fg="red")

    click.secho("Starting scheduler...", fg="blue")
    scheduler.start()


@dispatch_cli.group("server")
def dispatch_server():
    """Container for all dispatch server commands."""
    pass


@dispatch_server.command("routes")
def show_routes():
    """Prints all available routes."""
    from dispatch.main import api_router

    table = []
    for r in api_router.routes:
        auth = False
        for d in r.dependencies:
            if d.dependency.__name__ == "get_current_user":  # TODO this is fragile
                auth = True
        table.append([r.path, auth, ",".join(r.methods)])

    click.secho(tabulate(table, headers=["Path", "Authenticated", "Methods"]), fg="blue")


@dispatch_server.command("config")
def show_config():
    """Prints the current config as dispatch sees it."""
    import sys
    import inspect
    from dispatch import config

    func_members = inspect.getmembers(sys.modules[config.__name__])

    table = []
    for key, value in func_members:
        if key.isupper():
            table.append([key, value])

    click.secho(tabulate(table, headers=["Key", "Value"]), fg="blue")


@dispatch_server.command("develop")
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "error", "warning", "critical"]),
    default="debug",
    help="Log level to use.",
)
def run_server(log_level):
    """Runs a simple server for development."""
    # Uvicorn expects lowercase logging levels; the logging package expects upper.
    os.environ["LOG_LEVEL"] = log_level.upper()
    if not config.STATIC_DIR:
        import atexit
        from subprocess import Popen

        # take our frontend vars and export them for the frontend to consume
        envvars = os.environ.copy()
        envvars.update({x: getattr(config, x) for x in dir(config) if x.startswith("VUE_APP_")})

        p = Popen(["npm", "run", "serve"], cwd="src/dispatch/static/dispatch", env=envvars)
        atexit.register(p.terminate)
    uvicorn.run("dispatch.main:app", debug=True, log_level=log_level)


dispatch_server.add_command(uvicorn.main, name="start")


@dispatch_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    """Starts an ipython shell importing our app. Useful for debugging."""
    import IPython
    from IPython.terminal.ipapp import load_default_config

    config = load_default_config()

    config.TerminalInteractiveShell.banner1 = f"""Python {sys.version} on {sys.platform}
IPython: {IPython.__version__}"""

    IPython.start_ipython(argv=ipython_args, user_ns={}, config=config)


def entrypoint():
    """The entry that the CLI is executed from"""
    try:
        dispatch_cli()
    except DispatchException as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()
