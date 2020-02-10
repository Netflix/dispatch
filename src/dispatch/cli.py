import logging
import os
import sys

import click
import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from tabulate import tabulate
from uvicorn import main as uvicorn_main

from dispatch import __version__, config
from dispatch.application.models import *  # noqa
from dispatch.common.utils.cli import install_plugin_events, install_plugins

from .database import Base, engine
from .exceptions import DispatchException
from .plugins.base import plugins
from .scheduler import scheduler

from dispatch.models import *  # noqa; noqa

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

log = logging.getLogger(__name__)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def insert_newlines(string, every=64):
    return "\n".join(string[i : i + every] for i in range(0, len(string), every))


@click.group()
@click.version_option(version=__version__)
def dispatch_cli():
    """Command-line interface to Dispatch."""
    pass


@dispatch_cli.group("plugins")
def plugins_group():
    """All commands for plugin manipulation."""
    install_plugins()


@plugins_group.command("list")
def list_plugins():
    """Shows all available plugins"""
    table = []
    for p in plugins.all():
        table.append([p.title, p.slug, p.version, p.type, p.author, p.description])
    click.secho(
        tabulate(table, headers=["Title", "Slug", "Version", "Type", "Author", "Description"]),
        fg="blue",
    )


@dispatch_cli.group("term")
def term_command_group():
    """All commands for term manipulation."""
    pass


@dispatch_cli.group("contact")
def contact_command_group():
    """All commands for contact manipulation."""
    pass


@contact_command_group.group("load")
def contact_load_group():
    """All contact load commands."""
    pass


@contact_load_group.command("csv")
@click.argument("input", type=click.File("r"))
@click.option("--first-row-is-header", is_flag=True, default=True)
def contact_load_csv_command(input, first_row_is_header):
    """Load contacts via CSV."""
    import csv
    from pydantic import ValidationError
    from dispatch.individual import service as individual_service
    from dispatch.team import service as team_service
    from dispatch.database import SessionLocal

    db_session = SessionLocal()

    individual_contacts = []
    team_contacts = []
    if first_row_is_header:
        reader = csv.DictReader(input)
        for row in reader:
            row = dict((k.lower(), v) for k, v in row.items())
            if not row.get("email"):
                continue

            individual_contacts.append(row)

    for i in individual_contacts:
        i["is_external"] = True
        try:
            click.secho(f"Adding new individual contact. Email: {i['email']}", fg="blue")
            individual_service.get_or_create(db_session=db_session, **i)
        except ValidationError as e:
            click.secho(f"Failed to add individual contact. {e} {row}", fg="red")

    for t in team_contacts:
        i["is_external"] = True
        try:
            click.secho(f"Adding new team contact. Email: {t['email']}", fg="blue")
            team_service.get_or_create(db_session=db_session, **t)
        except ValidationError as e:
            click.secho(f"Failed to add team contact. {e} {row}", fg="red")


@dispatch_cli.group("incident")
def incident_command_group():
    """All commands for incident manipulation."""
    pass


@incident_command_group.group("load")
def incident_load_group():
    """All incient load commands."""
    pass


@incident_load_group.command("csv")
@click.argument("input", type=click.File("r"))
@click.option("--first-row-is-header", is_flag=True, default=True)
def incident_load_csv_command(input, first_row_is_header):
    """Load incidents via CSV."""
    import csv
    from dispatch.database import SessionLocal
    from datetime import datetime
    from dispatch.incident import service as incident_service

    db_session = SessionLocal()

    if first_row_is_header:
        reader = csv.DictReader(input)
        for row in reader:
            incident = incident_service.get_by_name(
                db_session=db_session, incident_name=row["name"]
            )
            if incident:
                incident.created_at = datetime.fromisoformat(row["created"])
            else:
                click.secho(f"No incident found. Name: {row['name']}", fg="red")


# This has been left as an example of how to import a jira issue
# @incident_load_group.command("jira")
# @click.argument("query")
# @click.option("--url", help="Jira instance url.", default=JIRA_URL)
# @click.option("--username", help="Jira username.", default=JIRA_USERNAME)
# @click.option("--password", help="Jira password.", default=JIRA_PASSWORD)
# def incident_load_jira(query, url, username, password):
#    """Loads incident data from jira."""
#    install_plugins()
#    import re
#    from jira import JIRA
#    from dispatch.incident.models import Incident
#    from dispatch.database import SessionLocal
#    from dispatch.incident_priority import service as incident_priority_service
#    from dispatch.incident_type import service as incident_type_service
#    from dispatch.individual import service as individual_service
#    from dispatch.participant import service as participant_service
#    from dispatch.participant_role import service as participant_role_service
#    from dispatch.participant_role.models import ParticipantRoleType
#    from dispatch.ticket import service as ticket_service
#    from dispatch.conversation import service as conversation_service
#    from dispatch.config import (
#        INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
#        INCIDENT_CONVERSATION_SLUG,
#        INCIDENT_TICKET_PLUGIN_SLUG,
#    )
#    from dispatch.document import service as document_service
#    from dispatch.document.models import DocumentCreate
#
#    db_session = SessionLocal()
#
#    client = JIRA(str(JIRA_URL), basic_auth=(JIRA_USERNAME, str(JIRA_PASSWORD)))
#
#    block_size = 100
#    block_num = 0
#
#
#    while True:
#        start_idx = block_num * block_size
#        issues = client.search_issues(query, start_idx, block_size)
#
#        click.secho(f"Collecting. PageSize: {block_size} PageNum: {block_num}", fg="blue")
#        if not issues:
#            # Retrieve issues until there are no more to come
#            break
#
#        block_num += 1
#
#        for issue in issues:
#            try:
#                participants = []
#                incident_name = issue.key
#                created_at = issue.fields.created
#
#                # older tickets don't have a component
#                if not issue.fields.components:
#                    incident_type = "Other"
#                else:
#                    incident_type = issue.fields.components[0].name
#
#                title = issue.fields.summary
#
#                if issue.fields.reporter:
#                    reporter_email = issue.fields.reporter.emailAddress
#                else:
#                    reporter_email = "joe@example.com"
#
#                status = issue.fields.status.name
#
#                # older tickets don't have priority
#                if not issue.fields.customfield_10551:
#                    incident_priority = "Low"
#                else:
#                    incident_priority = issue.fields.customfield_10551.value
#
#                incident_cost = issue.fields.customfield_20250
#                if incident_cost:
#                    incident_cost = incident_cost.replace("$", "")
#                    incident_cost = incident_cost.replace(",", "")
#                    incident_cost = float(incident_cost)
#
#                if issue.fields.assignee:
#                    commander_email = issue.fields.assignee.emailAddress
#                else:
#                    commander_email = "joe@example.com"
#
#                resolved_at = issue.fields.resolutiondate
#
#                description = issue.fields.description or "No Description"
#
#                match = re.findall(r"\[(?P<type>.*?)\|(?P<link>.*?)\]", description)
#
#                conversation_weblink = None
#                incident_document_weblink = None
#                for m_type, m_link in match:
#                    if "conversation" in m_type.lower():
#                        conversation_weblink = m_link
#
#                    if "document" in m_type.lower():
#                        incident_document_weblink = m_link
#
#                ticket = {
#                    "resource_type": INCIDENT_TICKET_PLUGIN_SLUG,
#                    "weblink": f"{JIRA_URL}/projects/SEC/{incident_name}",
#                }
#                ticket_obj = ticket_service.create(db_session=db_session, **ticket)
#
#                documents = []
#                if incident_document_weblink:
#                    document_in = DocumentCreate(
#                        name=f"{incident_name} - Investigation Document",
#                        resource_id=incident_document_weblink.split("/")[-2],
#                        resource_type=INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
#                        weblink=incident_document_weblink,
#                    )
#
#                    document_obj = document_service.create(
#                        db_session=db_session, document_in=document_in
#                    )
#
#                    documents.append(document_obj)
#
#                conversation_obj = None
#                if conversation_weblink:
#                    conversation_obj = conversation_service.create(
#                        db_session=db_session,
#                        resource_id=incident_name.lower(),
#                        resource_type=INCIDENT_CONVERSATION_SLUG,
#                        weblink=conversation_weblink,
#                        channel_id=incident_name.lower(),
#                    )
#
#                # TODO should some of this logic be in the incident_create_flow_instead? (kglisson)
#                incident_priority = incident_priority_service.get_by_name(
#                    db_session=db_session, name=incident_priority
#                )
#
#                incident_type = incident_type_service.get_by_name(
#                    db_session=db_session, name=incident_type
#                )
#
#                try:
#                    commander_info = individual_service.resolve_user_by_email(commander_email)
#                except KeyError:
#                    commander_info = {"email": commander_email, "fullname": "", "weblink": ""}
#
#                incident_commander_role = participant_role_service.create(
#                    db_session=db_session, role=ParticipantRoleType.incident_commander
#                )
#
#                commander_participant = participant_service.create(
#                    db_session=db_session, participant_role=[incident_commander_role]
#                )
#
#                commander = individual_service.get_or_create(
#                    db_session=db_session,
#                    email=commander_info["email"],
#                    name=commander_info["fullname"],
#                    weblink=commander_info["weblink"],
#                )
#
#                incident_reporter_role = participant_role_service.create(
#                    db_session=db_session, role=ParticipantRoleType.reporter
#                )
#
#                if reporter_email == commander_email:
#                    commander_participant.participant_role.append(incident_reporter_role)
#                else:
#                    reporter_participant = participant_service.create(
#                        db_session=db_session, participant_role=[incident_reporter_role]
#                    )
#
#                    try:
#                        reporter_info = individual_service.resolve_user_by_email(reporter_email)
#                    except KeyError:
#                        reporter_info = {"email": reporter_email, "fullname": "", "weblink": ""}
#
#                    reporter = individual_service.get_or_create(
#                        db_session=db_session,
#                        email=reporter_info["email"],
#                        name=reporter_info["fullname"],
#                        weblink=commander_info["weblink"],
#                    )
#                    reporter.participant.append(reporter_participant)
#                    db_session.add(reporter)
#                    participants.append(reporter_participant)
#
#                participants.append(commander_participant)
#                incident = Incident(
#                    title=title,
#                    description=description,
#                    status=status,
#                    name=incident_name,
#                    cost=incident_cost,
#                    created_at=created_at,
#                    closed_at=resolved_at,
#                    incident_priority=incident_priority,
#                    incident_type=incident_type,
#                    participants=participants,
#                    conversation=conversation_obj,
#                    documents=documents,
#                    ticket=ticket_obj,
#                )
#
#                commander.participant.append(commander_participant)
#                db_session.add(commander)
#                db_session.add(incident)
#                db_session.commit()
#                click.secho(
#                    f"Imported Issue. Key: {issue.key} Reporter: {incident.reporter.email}, Commander: {incident.commander.email}",
#                    fg="blue",
#                )
#            except Exception as e:
#                click.secho(f"Error importing issue. Key: {issue.key} Reason: {e}", fg="red")
#


@incident_command_group.command("close")
@click.argument("username")
@click.argument("name", nargs=-1)
def close_incidents(name, username):
    """This command will close a specific incident (running the close flow or all open incidents). Useful for development."""
    from dispatch.incident.flows import incident_closed_flow
    from dispatch.incident.models import Incident
    from dispatch.database import SessionLocal

    install_plugins()

    incidents = []
    db_session = SessionLocal()

    if not name:
        incidents = db_session.query(Incident).all()
    else:
        incidents = [db_session.query(Incident).filter(Incident.name == x).first() for x in name]

    for i in incidents:
        if i.conversation:
            if i.status == "Active":
                command = {"channel_id": i.conversation.channel_id, "user_id": username}
                try:
                    incident_closed_flow(command=command, db_session=db_session, incident_id=i.id)
                except Exception:
                    click.echo("Incident close failed.")


@incident_command_group.command("clean")
@click.argument("pattern", nargs=-1)
def clean_incident_artifacts(pattern):
    """This command will clean up incident artifacts. Useful for development."""
    import re
    from dispatch.plugins.dispatch_google.drive.config import GOOGLE_DOMAIN
    from dispatch.plugins.dispatch_google.common import get_service
    from dispatch.plugins.dispatch_google.drive.drive import (
        delete_team_drive,
        list_team_drives,
    )

    from dispatch.plugins.dispatch_slack.service import (
        slack,
        list_conversations,
        archive_conversation,
    )
    from dispatch.plugins.dispatch_slack.config import SLACK_API_BOT_TOKEN

    from dispatch.plugins.dispatch_google.groups.plugin import delete_group, list_groups

    install_plugins()

    patterns = [re.compile(p) for p in pattern]

    click.secho("Deleting google groups...", fg="red")

    scopes = [
        "https://www.googleapis.com/auth/admin.directory.group",
        "https://www.googleapis.com/auth/apps.groups.settings",
    ]
    client = get_service("admin", "directory_v1", scopes)

    for group in list_groups(client, query="email:sec-test*", domain=GOOGLE_DOMAIN)["groups"]:
        for p in patterns:
            if p.match(group["name"]):
                click.secho(group["name"], fg="red")
                delete_group(client, group_key=group["email"])

    click.secho("Archiving slack channels...", fg="red")
    client = slack.WebClient(token=SLACK_API_BOT_TOKEN)
    for c in list_conversations(client):
        for p in patterns:
            if p.match(c["name"]):
                archive_conversation(client, c["id"])

    click.secho("Deleting google drives...", fg="red")
    scopes = ["https://www.googleapis.com/auth/drive"]
    client = get_service("drive", "v3", scopes)

    for drive in list_team_drives(client):
        for p in patterns:
            if p.match(drive["name"]):
                click.secho(f"Deleting drive: {drive['name']}", fg="red")
                delete_team_drive(client, drive["id"], empty=True)


def sync_triggers():
    from sqlalchemy_searchable import sync_trigger
    sync_trigger(engine, "application", "search_vector", ["name"])
    sync_trigger(engine, "definition", "search_vector", ["text"])
    sync_trigger(engine, "incident", "search_vector", ["name", "title", "description"])
    sync_trigger(
        engine, "individual_contact", "search_vector", ["name", "title", "company", "notes"]
    )
    sync_trigger(engine, "team_contact", "search_vector", ["name", "company", "notes"])
    sync_trigger(engine, "term", "search_vector", ["text"])
    sync_trigger(engine, "document", "search_vector", ["name"])
    sync_trigger(engine, "incident_type", "search_vector", ["name", "description"])
    sync_trigger(engine, "policy", "search_vector", ["name", "description"])
    sync_trigger(engine, "service", "search_vector", ["name"])
    sync_trigger(engine, "task", "search_vector", ["description"])


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
    from sqlalchemy_utils import create_database

    create_database(str(config.SQLALCHEMY_DATABASE_URI))
    Base.metadata.create_all(engine)
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.stamp(alembic_cfg, "head")

    sync_triggers()
    click.secho("Success.", fg="green")


@dispatch_database.command("populate")
def populate_database():
    """Populates database with default values."""
    from dispatch.database import SessionLocal
    from dispatch.incident_type.models import IncidentType
    from dispatch.incident_priority.models import IncidentPriority, IncidentPriorityType

    db_session = SessionLocal()

    db_session.add(IncidentType(name="Other", slug="other", description="Default incident type."))

    for i in IncidentPriorityType:
        db_session.add(IncidentPriority(name=i.value))

    db_session.commit()
    click.secho("Success.", fg="green")


@dispatch_database.command("drop")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to drop the database?",
)
def drop_database():
    """Drops all data in database."""
    from sqlalchemy_utils import drop_database

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
    alembic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "alembic.ini")
    alembic_cfg = AlembicConfig(alembic_path)
    alembic_command.upgrade(alembic_cfg, revision, sql=sql, tag=tag)
    click.secho("Success.", fg="green")


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
    from .incident.scheduled import daily_summary, active_incidents_cost  # noqa
    from .task.scheduled import sync_tasks, create_task_reminders  # noqa
    from .term.scheduled import sync_terms  # noqa
    from .document.scheduled import sync_document_terms  # noqa
    from .application.scheduled import sync_applications  # noqa

    install_plugins()


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
    install_plugins()


@dispatch_server.command("routes")
def show_routes():
    """Prints all available routes."""
    from dispatch.api import api_router

    install_plugin_events(api_router)

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
    from dispatch.config import config

    table = []
    for k, v in config.file_values.items():
        table.append([k, v])

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
    uvicorn.run("dispatch.main:app", debug=True, log_level=log_level)


dispatch_server.add_command(uvicorn_main, name="start")


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
