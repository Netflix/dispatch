import logging
import os

import click
import uvicorn
from dispatch import __version__, config
from dispatch.enums import UserRoles
from dispatch.plugin.models import PluginInstance

from .scheduler import scheduler

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

log = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def dispatch_cli():
    """Command-line interface to Dispatch."""
    from .logging import configure_logging

    configure_logging()


@dispatch_cli.group("plugins")
def plugins_group():
    """All commands for plugin manipulation."""
    pass


@plugins_group.command("list")
def list_plugins():
    """Shows all available plugins."""
    from tabulate import tabulate

    from dispatch.database.core import SessionLocal
    from dispatch.plugin import service as plugin_service

    db_session = SessionLocal()
    table = []
    for record in plugin_service.get_all(db_session=db_session):
        table.append(
            [
                record.title,
                record.slug,
                record.version,
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
    from dispatch.database.core import SessionLocal
    from dispatch.plugin import service as plugin_service
    from dispatch.plugin.models import Plugin
    from dispatch.common.utils.cli import install_plugins
    from dispatch.plugins.base import plugins

    install_plugins()

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
                multiple=p.multiple,
                description=p.description,
            )
            db_session.add(record)

        if force:
            click.secho(f"Updating plugin... Slug: {p.slug} Version: {p.version}", fg="blue")
            # we only update values that should change
            record.title = p.title
            record.version = p.version
            record.author = p.author
            record.author_url = p.author_url
            record.description = p.description
            record.type = p.type
            db_session.add(record)

        db_session.commit()


@plugins_group.command("uninstall")
@click.argument("plugins", nargs=-1)
def uninstall_plugins(plugins):
    """Uninstalls all plugins, or only one."""
    from dispatch.database.core import SessionLocal
    from dispatch.plugin import service as plugin_service

    db_session = SessionLocal()

    for plugin_slug in plugins:
        plugin = plugin_service.get_by_slug(db_session=db_session, slug=plugin_slug)
        if not plugin:
            click.secho(
                f"Plugin slug {plugin_slug} does not exist. Make sure you're passing the plugin's slug.",
                fg="red",
            )

        plugin_service.delete(db_session=db_session, plugin_id=plugin.id)


@dispatch_cli.group("user")
def dispatch_user():
    """Container for all user commands."""
    pass


@dispatch_user.command("update")
@click.argument("email")
@click.option(
    "--organization",
    "-o",
    required=True,
    help="Organization to set role for.",
)
@click.option(
    "--role",
    "-r",
    required=True,
    type=click.Choice(UserRoles),
    help="Role to be assigned to the user.",
)
def update_user(email: str, role: str, organization: str):
    """Updates a user's roles."""
    from dispatch.database.core import SessionLocal
    from dispatch.auth import service as user_service
    from dispatch.auth.models import UserUpdate, UserOrganization

    db_session = SessionLocal()
    user = user_service.get_by_email(email=email, db_session=db_session)
    if not user:
        click.secho(f"No user found. Email: {email}", fg="red")
        return

    organization = UserOrganization(role=role, organization={"name": organization})
    user_service.update(
        user=user,
        user_in=UserUpdate(id=user.id, organizations=[organization]),
        db_session=db_session,
    )
    click.secho("User successfully updated.", fg="green")


@dispatch_user.command("reset")
@click.argument("email")
@click.password_option()
def reset_user_password(email: str, password: str):
    """Resets a user's password."""
    from dispatch.database.core import SessionLocal
    from dispatch.auth import service as user_service
    from dispatch.auth.models import UserUpdate

    db_session = SessionLocal()
    user = user_service.get_by_email(email=email, db_session=db_session)
    if not user:
        click.secho(f"No user found. Email: {email}", fg="red")
        return

    user_service.update(
        user=user, user_in=UserUpdate(id=user.id, password=password), db_session=db_session
    )
    click.secho("User successfully updated.", fg="green")


@dispatch_cli.group("database")
def dispatch_database():
    """Container for all dispatch database commands."""
    pass


@dispatch_database.command("init")
def database_init():
    """Initializes a new database."""
    click.echo("Initializing new database...")
    from .database.core import engine
    from .database.manage import (
        init_database,
    )

    init_database(engine)
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
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
def upgrade_database(tag, sql, revision, revision_type):
    """Upgrades database schema to newest version."""
    import sqlalchemy
    from sqlalchemy import inspect
    from sqlalchemy_utils import database_exists
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    from .database.core import engine

    from .database.manage import (
        get_core_tables,
        get_tenant_tables,
        init_database,
        setup_fulltext_search,
    )

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)

    if not database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        click.secho("Found no database to upgrade, initializing new database...")
        init_database(engine)
    else:
        conn = engine.connect()

        # detect if we need to convert to a multi-tenant schema structure
        schema_names = inspect(engine).get_schema_names()
        if "dispatch_core" not in schema_names:
            click.secho("Detected single tenant database, converting to multi-tenant...")
            conn.execute(sqlalchemy.text(open(config.ALEMBIC_MULTI_TENANT_MIGRATION_PATH).read()))

        if revision_type:
            if revision_type == "core":
                path = config.ALEMBIC_CORE_REVISION_PATH

            elif revision_type == "tenant":
                path = config.ALEMBIC_TENANT_REVISION_PATH

            alembic_cfg.set_main_option("script_location", path)
            alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)
        else:
            for path in [config.ALEMBIC_CORE_REVISION_PATH, config.ALEMBIC_TENANT_REVISION_PATH]:
                alembic_cfg.set_main_option("script_location", path)
                alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)

    # ensure triggers
    conn.execute("set search_path to dispatch_core")
    setup_fulltext_search(conn, get_core_tables())

    for s in inspect(engine).get_schema_names():
        if not s.startswith("dispatch_organization_"):
            continue

        tenant_tables = get_tenant_tables()
        for t in tenant_tables:
            t.schema = s
        conn.execute(f"set search_path to {s}")
        setup_fulltext_search(conn, tenant_tables)

    click.secho("Success.", fg="green")


@dispatch_database.command("merge")
@click.argument("revisions", nargs=-1)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option("--message")
def merge_revisions(revisions, revision_type, message):
    """Combines two revisions."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.merge(alembic_cfg, revisions, message=message)


@dispatch_database.command("heads")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def head_database(revision_type):
    """Shows the heads of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.heads(alembic_cfg)


@dispatch_database.command("history")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def history_database(revision_type):
    """Shows the history of the database."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
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
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
def downgrade_database(tag, sql, revision, revision_type):
    """Downgrades database schema to next newest version."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    if sql and revision == "-1":
        revision = "head:-1"

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)
    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.downgrade(alembic_cfg, revision, sql=sql, tag=tag)
    click.secho("Success.", fg="green")


@dispatch_database.command("stamp")
@click.argument("revision", nargs=1, default="head")
@click.option("--revision-type", type=click.Choice(["core", "tenant"]), default="core")
@click.option(
    "--tag", default=None, help="Arbitrary 'tag' name - can be used by custom env.py scripts."
)
@click.option(
    "--sql",
    is_flag=True,
    default=False,
    help="Don't emit SQL to database - dump to standard output instead.",
)
def stamp_database(revision, revision_type, tag, sql):
    """Forces the database to a given revision."""
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)

    if revision_type == "core":
        path = config.ALEMBIC_CORE_REVISION_PATH

    elif revision_type == "tenant":
        path = config.ALEMBIC_TENANT_REVISION_PATH

    alembic_cfg.set_main_option("script_location", path)
    alembic_command.stamp(alembic_cfg, revision, sql=sql, tag=tag)


@dispatch_database.command("revision")
@click.option("-m", "--message", default=None, help="Revision message")
@click.option(
    "--autogenerate",
    is_flag=True,
    help=(
        "Populate revision script with candidate migration "
        "operations, based on comparison of database to model"
    ),
)
@click.option("--revision-type", type=click.Choice(["core", "tenant"]))
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
    message, autogenerate, revision_type, sql, head, splice, branch_label, version_path, rev_id
):
    """Create new database revision."""
    import types
    from alembic import command as alembic_command
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig(config.ALEMBIC_INI_PATH)

    if revision_type:
        if revision_type == "core":
            path = config.ALEMBIC_CORE_REVISION_PATH
        elif revision_type == "tenant":
            path = config.ALEMBIC_TENANT_REVISION_PATH

        alembic_cfg.set_main_option("script_location", path)
        alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
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
    else:
        for path in [
            config.ALEMBIC_CORE_REVISION_PATH,
            config.ALEMBIC_TENANT_REVISION_PATH,
        ]:
            alembic_cfg.set_main_option("script_location", path)
            alembic_cfg.cmd_opts = types.SimpleNamespace(cmd="revision")
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
    from .evergreen.scheduled import create_evergreen_reminders
    from .feedback.scheduled import daily_report  # noqa
    from .incident.scheduled import daily_report, auto_tagger, close_incident_reminder  # noqa
    from .incident_cost.scheduled import calculate_incidents_response_cost  # noqa
    from .report.scheduled import incident_report_reminders  # noqa
    from .tag.scheduled import sync_tags, build_tag_models  # noqa
    from .task.scheduled import (
        create_task_reminders,
        daily_sync_task,
        sync_active_stable_tasks,
    )  # noqa
    from .term.scheduled import sync_terms  # noqa
    from .workflow.scheduled import (
        daily_sync_workflow,  # noqa
        sync_active_stable_workflows,  # noqa
    )
    from .monitor.scheduled import sync_active_stable_monitors  # noqa
    from .data.source.scheduled import sync_sources  # noqa


@dispatch_scheduler.command("list")
def list_tasks():
    """Prints and runs all currently configured periodic tasks, in seperate event loop."""
    from tabulate import tabulate

    table = []
    for task in scheduler.registered_tasks:
        table.append([task["name"], task["job"].period, task["job"].at_time])

    click.secho(tabulate(table, headers=["Task Name", "Period", "At Time"]), fg="blue")


@dispatch_scheduler.command("start")
@click.argument("tasks", nargs=-1)
@click.option("--eager", is_flag=True, default=False, help="Run the tasks immediately.")
def start_tasks(tasks, eager):
    """Starts the scheduler."""
    from dispatch.common.utils.cli import install_plugins

    install_plugins()

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
    from tabulate import tabulate
    from dispatch.main import api_router

    table = []
    for r in api_router.routes:
        table.append([r.path, ",".join(r.methods)])

    click.secho(tabulate(table, headers=["Path", "Authenticated", "Methods"]), fg="blue")


@dispatch_server.command("config")
def show_config():
    """Prints the current config as dispatch sees it."""
    import sys
    import inspect
    from tabulate import tabulate
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
    if not os.path.isdir(config.STATIC_DIR):
        import atexit
        from subprocess import Popen

        # take our frontend vars and export them for the frontend to consume
        envvars = os.environ.copy()
        envvars.update({x: getattr(config, x) for x in dir(config) if x.startswith("VUE_APP_")})
        is_windows = os.name == "nt"
        windows_cmds = ["cmd", "/c"]
        default_cmds = ["npm", "run", "serve"]
        cmds = windows_cmds + default_cmds if is_windows else default_cmds
        p = Popen(
            cmds,
            cwd=os.path.join("src", "dispatch", "static", "dispatch"),
            env=envvars,
        )
        atexit.register(p.terminate)
    uvicorn.run("dispatch.main:app", debug=True, log_level=log_level)


dispatch_server.add_command(uvicorn.main, name="start")


@dispatch_server.command("slack")
@click.argument("organization")
@click.argument("project")
def run_slack_websocket(organization: str, project: str):
    """Runs the slack websocket process."""
    import asyncio
    from sqlalchemy import true
    from dispatch.project.models import ProjectRead
    from dispatch.project import service as project_service
    from dispatch.plugins.dispatch_slack import socket_mode
    from dispatch.plugins.dispatch_slack.decorators import get_organization_scope_from_slug
    from dispatch.common.utils.cli import install_plugins

    install_plugins()

    session = get_organization_scope_from_slug(organization)

    project = project_service.get_by_name_or_raise(
        db_session=session, project_in=ProjectRead(name=project)
    )

    instances = (
        session.query(PluginInstance)
        .filter(PluginInstance.enabled == true())
        .filter(PluginInstance.project_id == project.id)
        .all()
    )

    instance = None
    for i in instances:
        if i.plugin.slug == "slack-conversation":
            instance = i
            break

    if not instance:
        click.secho(
            f"No slack plugin has been configured for this organization/plugin. Organization: {organization} Project: {project}",
            fg="red",
        )
        return

    click.secho("Slack websocket process started...", fg="blue")
    asyncio.run(socket_mode.run_websocket_process(instance.configuration))


@dispatch_server.command("shell")
@click.argument("ipython_args", nargs=-1, type=click.UNPROCESSED)
def shell(ipython_args):
    """Starts an ipython shell importing our app. Useful for debugging."""
    import sys
    import IPython
    from IPython.terminal.ipapp import load_default_config

    config = load_default_config()

    config.TerminalInteractiveShell.banner1 = f"""Python {sys.version} on {sys.platform}
IPython: {IPython.__version__}"""

    IPython.start_ipython(argv=ipython_args, user_ns={}, config=config)


def entrypoint():
    """The entry that the CLI is executed from"""
    from .exceptions import DispatchException

    try:
        dispatch_cli()
    except DispatchException as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()
