import logging
import os
import base64

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

# if we have metatron available to us, lets use it to decrypt our secrets in memory
try:
    import metatron.decrypt

    class Secret:
        """
        Holds a string value that should not be revealed in tracebacks etc.
        You should cast the value to `str` at the point it is required.
        """

        def __init__(self, value: str):
            self._value = value
            self._decrypted_value = (
                metatron.decrypt.MetatronDecryptor()
                .decryptBytes(base64.b64decode(self._value))
                .decode("utf-8")
            )

        def __repr__(self) -> str:
            class_name = self.__class__.__name__
            return f"{class_name}('**********')"

        def __str__(self) -> str:
            return self._decrypted_value


except Exception:
    from starlette.datastructures import Secret


config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)
ENV = config("ENV", default="local")

DISPATCH_UI_URL = config("DISPATCH_UI_URL")
DISPATCH_HELP_EMAIL = config("DISPATCH_HELP_EMAIL")
DISPATCH_HELP_SLACK_CHANNEL = config("DISPATCH_HELP_SLACK_CHANNEL")

# authentication
DISPATCH_PKCE_AUTH_ENABLED = config("DISPATCH_PKCE_AUTH", cast=bool, default=True)
DISPATCH_HEADER_AUTH_ENABLED = config("DISPATCH_HEADER_AUTH", cast=bool, default=False)

DISPATCH_AUTH_HEADER_KEY = config("DISPATCH_AUTH_HEADER", default=None)
JWKS_URL = config("JWKS_URL", default=None)

if DISPATCH_PKCE_AUTH_ENABLED:
    if not JWKS_URL:
        raise Exception("JWKS_URL must be set when DISPATCH_PKCE_AUTH_ENABLED")

if DISPATCH_HEADER_AUTH_ENABLED:
    if not DISPATCH_AUTH_HEADER_KEY:
        raise Exception("DISPATCH_AUTH_HEADER_KEY must be when when DISPATCH_HEADER_AUTH_ENABLED")

# static files
DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "static/dispatch/dist"
)
STATIC_DIR = config("STATIC_DIR", default=DEFAULT_STATIC_DIR)

# metrics
METRIC_PROVIDERS = config("METRIC_PROVIDERS", cast=CommaSeparatedStrings, default="")

# sentry middleware
SENTRY_DSN = config("SENTRY_DSN", cast=Secret, default=None)

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret)
DATABASE_NAME = config("DATABASE_NAME", default="dispatch")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

# incident plugins
INCIDENT_PLUGIN_CONTACT_SLUG = config("INCIDENT_PLUGIN_CONTACT_SLUG", default="slack-contact")
INCIDENT_PLUGIN_CONVERSATION_SLUG = config(
    "INCIDENT_PLUGIN_CONVERSATION_SLUG", default="slack-conversation"
)
INCIDENT_PLUGIN_DOCUMENT_SLUG = config(
    "INCIDENT_PLUGIN_DOCUMENT_SLUG", default="google-docs-document"
)
INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG = config(
    "INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG", default="dispatch-document-resolver"
)
INCIDENT_PLUGIN_EMAIL_SLUG = config(
    "INCIDENT_PLUGIN_EMAIL_SLUG", default="google-gmail-conversation"
)
INCIDENT_PLUGIN_GROUP_SLUG = config(
    "INCIDENT_PLUGIN_GROUP_SLUG", default="google-group-participant-group"
)
INCIDENT_PLUGIN_PARTICIPANT_SLUG = config(
    "INCIDENT_PLUGIN_PARTICIPANT_SLUG", default="dispatch-participants"
)
INCIDENT_PLUGIN_STORAGE_SLUG = config(
    "INCIDENT_PLUGIN_STORAGE_SLUG", default="google-drive-storage"
)

INCIDENT_PLUGIN_CONFERENCE_SLUG = config(
    "INCIDENT_PLUGIN_CONFERENCE_SLUG", default="google-calendar-conference"
)
INCIDENT_PLUGIN_TICKET_SLUG = config("INCIDENT_PLUGIN_TICKET_SLUG", default="jira-ticket")
INCIDENT_PLUGIN_TASK_SLUG = config("INCIDENT_PLUGIN_TASK_SLUG", default="google-drive-task")

# incident resources
INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID = config(
    "INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID"
)
INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID = config("INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID")
INCIDENT_FAQ_DOCUMENT_ID = config("INCIDENT_FAQ_DOCUMENT_ID")
INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID = config("INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID")
INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID = config("INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID")

INCIDENT_NOTIFICATION_CONVERSATIONS = config(
    "INCIDENT_NOTIFICATION_CONVERSATIONS", cast=CommaSeparatedStrings, default=""
)

INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS = config(
    "INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS", cast=CommaSeparatedStrings, default=""
)

INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID = config(
    "INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID", default=None
)

INCIDENT_RESOURCE_TACTICAL_GROUP = config(
    "INCIDENT_RESOURCE_TACTICAL_GROUP", default="google-group-participant-tactical-group"
)
INCIDENT_RESOURCE_NOTIFICATIONS_GROUP = config(
    "INCIDENT_RESOURCE_NOTIFICATIONS_GROUP", default="google-group-participant-notifications-group"
)

INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT = config(
    "INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT", default="google-docs-investigation-document"
)
INCIDENT_RESOURCE_INVESTIGATION_SHEET = config(
    "INCIDENT_RESOURCE_INVESTIGATION_SHEET", default="google-docs-investigation-sheet"
)
INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT = config(
    "INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT", default="google-docs-incident-review-document"
)
INCIDENT_RESOURCE_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT = config(
    "INCIDENT_RESOURCE_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT",
    default="google-docs-conversation-commands-reference-document",
)
INCIDENT_RESOURCE_FAQ_DOCUMENT = config(
    "INCIDENT_RESOURCE_FAQ_DOCUMENT", default="google-docs-faq-document"
)
INCIDENT_RESOURCE_INCIDENT_TASK = config(
    "INCIDENT_RESOURCE_INCIDENT_TASK", default="google-docs-incident-task"
)

# Incident Cost Configuration
ANNUAL_COST_EMPLOYEE = config("ANNUAL_COST_EMPLOYEE", cast=int, default="650000")
BUSINESS_HOURS_YEAR = config("BUSINESS_HOURS_YEAR", cast=int, default="2080")
