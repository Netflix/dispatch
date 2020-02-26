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


#config = Config(".env")

LOG_LEVEL = os.getenv("LOG_LEVEL", default=logging.WARNING)
ENV = os.getenv("ENV", default="local")

DISPATCH_HELP_EMAIL = os.getenv("DISPATCH_HELP_EMAIL", default="")
DISPATCH_HELP_SLACK_CHANNEL = os.getenv("DISPATCH_HELP_SLACK_CHANNEL", default="")

# authentication
JWKS_URL = os.getenv("JWKS_URL", default="")

DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "static/dispatch/dist"
)
STATIC_DIR = os.getenv("STATIC_DIR", default=DEFAULT_STATIC_DIR)

# metrics
METRIC_PROVIDERS = os.getenv("METRIC_PROVIDERS", cast=CommaSeparatedStrings, default="")

# sentry middleware
SENTRY_DSN = os.getenv("SENTRY_DSN", cast=Secret, default=None)

# database
DATABASE_HOSTNAME = os.getenv("DATABASE_HOSTNAME", default="")
DATABASE_CREDENTIALS = os.getenv("DATABASE_CREDENTIALS", cast=Secret)
DATABASE_NAME = os.getenv("DATABASE_NAME", default="dispatch")
DATABASE_PORT = os.getenv("DATABASE_PORT", default="5432")
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

# incident plugins
INCIDENT_PLUGIN_CONTACT_SLUG = os.getenv("INCIDENT_PLUGIN_CONTACT_SLUG", default="slack-contact")
INCIDENT_PLUGIN_CONVERSATION_SLUG = os.getenv(
    "INCIDENT_PLUGIN_CONVERSATION_SLUG", default="slack-conversation"
)
INCIDENT_PLUGIN_DOCUMENT_SLUG = os.getenv(
    "INCIDENT_PLUGIN_DOCUMENT_SLUG", default="google-docs-document"
)
INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG = os.getenv(
    "INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG", default="dispatch-document-resolver"
)
INCIDENT_PLUGIN_EMAIL_SLUG = os.getenv(
    "INCIDENT_PLUGIN_EMAIL_SLUG", default="google-gmail-conversation"
)
INCIDENT_PLUGIN_GROUP_SLUG = os.getenv(
    "INCIDENT_PLUGIN_GROUP_SLUG", default="google-group-participant-group"
)
INCIDENT_PLUGIN_PARTICIPANT_SLUG = os.getenv(
    "INCIDENT_PLUGIN_PARTICIPANT_SLUG", default="dispatch-participants"
)
INCIDENT_PLUGIN_STORAGE_SLUG = os.getenv(
    "INCIDENT_PLUGIN_STORAGE_SLUG", default="google-drive-storage"
)
INCIDENT_PLUGIN_TICKET_SLUG = os.getenv("INCIDENT_PLUGIN_TICKET_SLUG", default="jira-ticket")
INCIDENT_PLUGIN_TASK_SLUG = os.getenv("INCIDENT_PLUGIN_TASK_SLUG", default="google-drive-task")

# incident resources
INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID = os.getenv("INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID", default="")
INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID = os.getenv("INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID", default="")
INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID = os.getenv("INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID", default="")
INCIDENT_FAQ_DOCUMENT_ID = os.getenv("INCIDENT_FAQ_DOCUMENT_ID", default="")

INCIDENT_NOTIFICATION_CONVERSATIONS = os.getenv(
    "INCIDENT_NOTIFICATION_CONVERSATIONS", cast=CommaSeparatedStrings, default=""
)

INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS = os.getenv(
    "INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS", cast=CommaSeparatedStrings, default=""
)

INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID = os.getenv(
    "INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID", default=None
)

INCIDENT_RESOURCE_TACTICAL_GROUP = os.getenv(
    "INCIDENT_RESOURCE_TACTICAL_GROUP", default="google-group-participant-tactical-group"
)
INCIDENT_RESOURCE_NOTIFICATIONS_GROUP = os.getenv(
    "INCIDENT_RESOURCE_NOTIFICATIONS_GROUP", default="google-group-participant-notifications-group"
)
INCIDENT_RESOURCE_FAQ_DOCUMENT = os.getenv(
    "INCIDENT_RESOURCE_FAQ_DOCUMENT", default="google-docs-faq-document"
)
INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT = os.getenv(
    "INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT", default="google-docs-investigation-document"
)
INCIDENT_RESOURCE_INVESTIGATION_SHEET = os.getenv(
    "INCIDENT_RESOURCE_INVESTIGATION_SHEET", default="google-docs-investigation-sheet"
)
INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT = os.getenv(
    "INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT", default="google-docs-incident-review-document",
)
INCIDENT_RESOURCE_INCIDENT_TASK = os.getenv(
    "INCIDENT_RESOURCE_INCIDENT_TASK", default="google-docs-incident-task"
)

# Incident Cost Configuration
ANNUAL_COST_EMPLOYEE = os.getenv("ANNUAL_COST_EMPLOYEE", cast=int, default="650000")
BUSINESS_HOURS_YEAR = os.getenv("BUSINESS_HOURS_YEAR", cast=int, default="2080")
