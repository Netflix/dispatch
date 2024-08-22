"""Migrates plugin instance configuration column to encrypted column.

Revision ID: 3820a792d88a
Revises: ebe0cb6528ba
Create Date: 2021-09-16 16:33:40.605881

"""
from alembic import op
from pydantic import SecretStr, ValidationError
from pydantic.json import pydantic_encoder
from starlette.datastructures import URL
from sqlalchemy.dialects import postgresql

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import StringEncryptedType, types
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from dispatch.config import config, Secret, DISPATCH_ENCRYPTION_KEY


# revision identifiers, used by Alembic.
revision = "3820a792d88a"
down_revision = "ebe0cb6528ba"
branch_labels = None
depends_on = None

Base = declarative_base()


def show_secrets_encoder(obj):
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    else:
        return pydantic_encoder(obj)


def migrate_config(instances, slug, config):
    for instance in instances:
        if slug == instance.plugin.slug:
            instance.configuration = config


class Plugin(Base):
    __tablename__ = "plugin"
    __table_args__ = {"schema": "dispatch_core"}
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)


class PluginInstance(Base):
    __tablename__ = "plugin_instance"
    id = Column(Integer, primary_key=True)
    _configuration = Column(
        StringEncryptedType(key=str(DISPATCH_ENCRYPTION_KEY), engine=AesEngine, padding="pkcs5")
    )
    plugin_id = Column(Integer, ForeignKey(Plugin.id))
    plugin = relationship(Plugin, backref="instances")

    @hybrid_property
    def configuration(self):
        """Property that correctly returns a plugins configuration object."""
        pass

    @configuration.setter
    def configuration(self, configuration):
        """Property that correctly sets a plugins configuration object."""
        if configuration:
            self._configuration = configuration.json(encoder=show_secrets_encoder)


def upgrade():
    op.add_column(
        "plugin_instance",
        Column(
            "_configuration",
            types.encrypted.encrypted_type.StringEncryptedType(),
            nullable=True,
        ),
    )

    bind = op.get_bind()
    session = Session(bind=bind)

    instances = session.query(PluginInstance).all()

    from dispatch.plugins.dispatch_google.config import GoogleConfiguration

    GOOGLE_DEVELOPER_KEY = config("GOOGLE_DEVELOPER_KEY", cast=Secret, default=None)
    GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL = config(
        "GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL", default=None
    )
    GOOGLE_SERVICE_ACCOUNT_CLIENT_ID = config("GOOGLE_SERVICE_ACCOUNT_CLIENT_ID", default=None)
    GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT = config(
        "GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT", default=None
    )
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY = config(
        "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY", cast=Secret, default=None
    )
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID = config(
        "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID", default=None
    )
    GOOGLE_SERVICE_ACCOUNT_PROJECT_ID = config("GOOGLE_SERVICE_ACCOUNT_PROJECT_ID", default=None)
    GOOGLE_DOMAIN = config("GOOGLE_DOMAIN", default=None)

    try:
        google_config = GoogleConfiguration(
            developer_key=str(GOOGLE_DEVELOPER_KEY),
            service_account_client_email=GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
            service_account_client_id=GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
            service_account_private_key=str(GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY),
            service_account_private_key_id=GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
            service_account_delegated_account=GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT,
            service_account_project_id=GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
            google_domain=GOOGLE_DOMAIN,
        )
        migrate_config(instances, "google-calendar-conference", google_config)
        migrate_config(instances, "google-docs-document", google_config)
        migrate_config(instances, "google-drive-storage", google_config)
        migrate_config(instances, "google-drive-task", google_config)
        migrate_config(instances, "google-gmail-email", google_config)
        migrate_config(instances, "google-group-participant-group", google_config)
    except ValidationError:
        print(
            "Skipping automatic migration of google plugin credentials, if you are using the google suite of plugins manually migrate credentials."
        )

    from dispatch.plugins.dispatch_pagerduty.plugin import PagerdutyConfiguration

    PAGERDUTY_API_KEY = config("PAGERDUTY_API_KEY", cast=Secret, default=None)
    PAGERDUTY_API_FROM_EMAIL = config("PAGERDUTY_API_FROM_EMAIL", default=None)

    try:
        pagerduty_config = PagerdutyConfiguration(
            api_key=str(PAGERDUTY_API_KEY), from_email=PAGERDUTY_API_FROM_EMAIL
        )
        migrate_config(instances, "pagerduty-oncall", pagerduty_config)
    except ValidationError:
        print(
            "Skipping automatic migration of pagerduty plugin credentials, if you are using the pagerduty plugin manually migrate credentials."
        )

    from dispatch.plugins.dispatch_zoom.plugin import ZoomConfiguration

    ZOOM_API_USER_ID = config("ZOOM_API_USER_ID", default=None)
    ZOOM_API_KEY = config("ZOOM_API_KEY", default=None)
    ZOOM_API_SECRET = config("ZOOM_API_SECRET", cast=Secret, default=None)

    try:
        zoom_config = ZoomConfiguration(
            api_user_id=ZOOM_API_USER_ID, api_key=ZOOM_API_KEY, api_secret=str(ZOOM_API_SECRET)
        )
        migrate_config(instances, "zoom-conference", zoom_config)
    except ValidationError:
        print(
            "Skipping automatic migration of zoom plugin credentials, if you are using the zoom plugin manually migrate credentials."
        )

    from dispatch.plugins.dispatch_jira.plugin import JiraConfiguration

    JIRA_API_URL = config("JIRA_API_URL", cast=URL, default=None)
    JIRA_BROWSER_URL = config("JIRA_BROWSER_URL", cast=URL, default=None)
    JIRA_HOSTING_TYPE = config("JIRA_HOSTING_TYPE", default="cloud")
    JIRA_PASSWORD = config("JIRA_PASSWORD", cast=Secret, default=None)
    JIRA_USERNAME = config("JIRA_USERNAME", default=None)
    JIRA_PROJECT_ID = config("JIRA_PROJECT_ID", default=None)
    JIRA_ISSUE_TYPE_NAME = config("JIRA_ISSUE_TYPE_NAME", default=None)

    try:
        jira_config = JiraConfiguration(
            api_url=str(JIRA_API_URL),
            browser_url=str(JIRA_BROWSER_URL),
            hosting_type=JIRA_HOSTING_TYPE,
            username=JIRA_USERNAME,
            default_project_id=JIRA_PROJECT_ID,
            default_issue_type_name=JIRA_ISSUE_TYPE_NAME,
            password=str(JIRA_PASSWORD),
        )
        migrate_config(instances, "jira-ticket", jira_config)
    except ValidationError:
        print(
            "Skipping automatic migration of jira plugin credentials, if you are using the jira plugin manually migrate credentials."
        )

    from dispatch.plugins.dispatch_opsgenie.plugin import OpsgenieConfiguration

    OPSGENIE_API_KEY = config("OPSGENIE_API_KEY", default=None, cast=Secret)

    try:
        opsgenie_config = OpsgenieConfiguration(api_key=str(OPSGENIE_API_KEY), default=None)
        migrate_config(instances, "opsgenie-oncall", opsgenie_config)
    except ValidationError:
        print(
            "Skipping automatic migration of opsgenie plugin credentials, if you are using the opsgenie plugin manually migrate credentials."
        )

    from dispatch.plugins.dispatch_slack.config import (
        SlackContactConfiguration,
        SlackConversationConfiguration,
    )

    SLACK_API_BOT_TOKEN = config("SLACK_API_BOT_TOKEN", cast=Secret, default=None)
    SLACK_SOCKET_MODE_APP_TOKEN = config("SLACK_SOCKET_MODE_APP_TOKEN", cast=Secret, default=None)
    SLACK_APP_USER_SLUG = config("SLACK_APP_USER_SLUG", default=None)
    SLACK_BAN_THREADS = config("SLACK_BAN_THREADS", default=True)
    SLACK_PROFILE_DEPARTMENT_FIELD_ID = config("SLACK_PROFILE_DEPARTMENT_FIELD_ID", default="")
    SLACK_PROFILE_TEAM_FIELD_ID = config("SLACK_PROFILE_TEAM_FIELD_ID", default="")
    SLACK_PROFILE_WEBLINK_FIELD_ID = config("SLACK_PROFILE_WEBLINK_FIELD_ID", default="")
    SLACK_SIGNING_SECRET = config("SLACK_SIGNING_SECRET", cast=Secret, default=None)
    SLACK_TIMELINE_EVENT_REACTION = config("SLACK_TIMELINE_EVENT_REACTION", default="stopwatch")

    # Slash commands
    SLACK_COMMAND_LIST_TASKS_SLUG = config(
        "SLACK_COMMAND_LIST_TASKS_SLUG", default="/dispatch-list-tasks"
    )
    SLACK_COMMAND_LIST_MY_TASKS_SLUG = config(
        "SLACK_COMMAND_LIST_MY_TASKS_SLUG", default="/dispatch-list-my-tasks"
    )
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG = config(
        "SLACK_COMMAND_LIST_PARTICIPANTS_SLUG", default="/dispatch-list-participants"
    )
    SLACK_COMMAND_ASSIGN_ROLE_SLUG = config(
        "SLACK_COMMAND_ASSIGN_ROLE_SLUG", default="/dispatch-assign-role"
    )
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG = config(
        "SLACK_COMMAND_UPDATE_INCIDENT_SLUG", default="/dispatch-update-incident"
    )
    SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG = config(
        "SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG", default="/dispatch-update-participant"
    )
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG = config(
        "SLACK_COMMAND_ENGAGE_ONCALL_SLUG", default="/dispatch-engage-oncall"
    )
    SLACK_COMMAND_LIST_RESOURCES_SLUG = config(
        "SLACK_COMMAND_LIST_RESOURCES_SLUG", default="/dispatch-list-resources"
    )
    SLACK_COMMAND_REPORT_INCIDENT_SLUG = config(
        "SLACK_COMMAND_REPORT_INCIDENT_SLUG", default="/dispatch-report-incident"
    )
    SLACK_COMMAND_REPORT_TACTICAL_SLUG = config(
        "SLACK_COMMAND_REPORT_TACTICAL_SLUG", default="/dispatch-report-tactical"
    )
    SLACK_COMMAND_REPORT_EXECUTIVE_SLUG = config(
        "SLACK_COMMAND_REPORT_EXECUTIVE_SLUG", default="/dispatch-report-executive"
    )
    SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG = config(
        "SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG", default="/dispatch-notifications-group"
    )
    SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG = config(
        "SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG", default="/dispatch-add-timeline-event"
    )
    SLACK_COMMAND_LIST_INCIDENTS_SLUG = config(
        "SLACK_COMMAND_LIST_INCIDENTS_SLUG", default="/dispatch-list-incidents"
    )
    SLACK_COMMAND_RUN_WORKFLOW_SLUG = config(
        "SLACK_COMMAND_RUN_WORKFLOW_SLUG", default="/dispatch-run-workflow"
    )
    SLACK_COMMAND_LIST_WORKFLOWS_SLUG = config(
        "SLUG_COMMAND_LIST_WORKFLOWS_SLUG", default="/dispatch-list-workflows"
    )

    try:
        slack_conversation_config = SlackConversationConfiguration(
            api_bot_token=str(SLACK_API_BOT_TOKEN),
            socket_mode_app_token=str(SLACK_SOCKET_MODE_APP_TOKEN),
            signing_secret=str(SLACK_SIGNING_SECRET),
            app_user_slug=SLACK_APP_USER_SLUG,
            ban_threads=SLACK_BAN_THREADS,
            timeline_event_reaction=SLACK_TIMELINE_EVENT_REACTION,
            slack_command_tasks=SLACK_COMMAND_LIST_TASKS_SLUG,
            slack_command_list_my_tasks=SLACK_COMMAND_LIST_MY_TASKS_SLUG,
            slack_command_list_participants=SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
            slack_command_assign_role=SLACK_COMMAND_ASSIGN_ROLE_SLUG,
            slack_command_update_incident=SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
            slack_command_update_participant=SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG,
            slack_command_engage_oncall=SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
            slack_command_list_resource=SLACK_COMMAND_LIST_RESOURCES_SLUG,
            slack_command_report_incident=SLACK_COMMAND_REPORT_INCIDENT_SLUG,
            slack_command_report_tactical=SLACK_COMMAND_REPORT_TACTICAL_SLUG,
            slack_command_report_executive=SLACK_COMMAND_REPORT_EXECUTIVE_SLUG,
            slack_command_update_notifications_group=SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG,
            slack_command_add_timeline_event=SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG,
            slack_command_list_incidents=SLACK_COMMAND_LIST_INCIDENTS_SLUG,
            slack_command_run_workflow=SLACK_COMMAND_RUN_WORKFLOW_SLUG,
            slack_command_list_workflow=SLACK_COMMAND_LIST_WORKFLOWS_SLUG,
        )

        slack_contact_config = SlackContactConfiguration(
            api_bot_token=str(SLACK_API_BOT_TOKEN),
            socket_mode_app_token=str(SLACK_SOCKET_MODE_APP_TOKEN),
            signing_secret=str(SLACK_SIGNING_SECRET),
            profile_department_field_id=SLACK_PROFILE_DEPARTMENT_FIELD_ID,
            profile_team_field_id=SLACK_PROFILE_TEAM_FIELD_ID,
            profile_weblink_field_id=SLACK_PROFILE_WEBLINK_FIELD_ID,
        )

        migrate_config(instances, "slack-conversation", slack_conversation_config)
        migrate_config(instances, "slack-contact", slack_contact_config)

    except ValidationError:
        print(
            "Skipping automatic migration of slack plugin credentials, if you are using the slack plugin manually migrate credentials."
        )

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "plugin_instance",
        Column("configuration", postgresql.BYTEA(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
