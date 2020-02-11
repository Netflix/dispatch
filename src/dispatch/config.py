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

# authentication
JWKS_URL = config("JWKS_URL")

DEFAULT_STATIC_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "static/dispatch/dist"
)
STATIC_DIR = config("STATIC_DIR", default=DEFAULT_STATIC_DIR)

METRIC_PROVIDERS = config("METRIC_PROVIDERS", cast=CommaSeparatedStrings, default="")

DISPATCH_HELP_EMAIL = config("DISPATCH_HELP_EMAIL")
DISPATCH_HELP_SLACK_CHANNEL = config("DISPATCH_HELP_SLACK_CHANNEL")

# sentry middleware
SENTRY_DSN = config("SENTRY_DSN", cast=Secret, default=None)

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME")
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret)
DATABASE_NAME = config("DATABASE_NAME", default="dispatch")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_CREDENTIALS}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}"

INCIDENT_CONTACT_PLUGIN_SLUG = config("INCIDENT_CONTACT_PLUGIN_SLUG", default="pandora-contact")
INCIDENT_CONVERSATION_APP_USER_SLUG = config("INCIDENT_CONVERSATION_APP_USER_SLUG")
INCIDENT_CONVERSATION_APP_BOT_SLUG = config("INCIDENT_CONVERSATION_APP_BOT_SLUG")
INCIDENT_CONVERSATION_SLUG = config("INCIDENT_CONVERSATION_SLUG", default="slack-conversation")
INCIDENT_DOCUMENT_SLUG = config("INCIDENT_DOCUMENT_SLUG", default="google-docs-document")
INCIDENT_DOCUMENT_FAQ_DOCUMENT_SLUG = config(
    "INCIDENT_DOCUMENT_FAQ_DOCUMENT_SLUG", default="google-docs-faq-document"
)
INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG = config(
    "INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG", default="google-docs-investigation-document"
)
INCIDENT_DOCUMENT_INVESTIGATION_SHEET_SLUG = config(
    "INCIDENT_DOCUMENT_INVESTIGATION_SHEET_SLUG", default="google-docs-investigation-sheet"
)
INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG = config(
    "INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG",
    default="google-docs-incident-review-document",
)
INCIDENT_DOCUMENT_RESOLVER_PLUGIN_SLUG = config(
    "INCIDENT_DOCUMENT_RESOLVER_PLUGIN_SLUG", default="dispatch-document-resolver"
)
INCIDENT_FORM_FEEDBACK_FORM_SLUG = config(
    "INCIDENT_FORM_FEEDBACK_FORM_SLUG", default="google-forms-feedback-form"
)
INCIDENT_EMAIL_SLUG = config("INCIDENT_EMAIL_SLUG", default="google-gmail-conversation")
INCIDENT_GROUP_SLUG = config("INCIDENT_GROUP_SLUG", default="google-group-participant-group")

INCIDENT_ONCALL_PLUGIN_SLUG = config("INCIDENT_ONCALL_PLUGIN_SLUG", default="pagerduty-oncall")
INCIDENT_PARTICIPANT_PLUGIN_SLUG = config(
    "INCIDENT_PARTICIPANT_PLUGIN_SLUG", default="dispatch-participants"
)
INCIDENT_STORAGE_SLUG = config("INCIDENT_STORAGE_SLUG", default="google-drive-storage")
INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID_SLUG = config("INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID")
INCIDENT_STORAGE_DRIVE_ID_SLUG = config("INCIDENT_STORAGE_DRIVE_ID_SLUG")
INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID_SLUG = config(
    "INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID_SLUG"
)
INCIDENT_TACTICAL_GROUP_SLUG = config(
    "INCIDENT_TACTICAL_GROUP_SLUG", default="google-group-participant-tactical-group"
)
INCIDENT_NOTIFICATIONS_GROUP_SLUG = config(
    "INCIDENT_NOTIFICATIONS_GROUP_SLUG", default="google-group-participant-notifications-group"
)
INCIDENT_TICKET_PLUGIN_SLUG = config("INCIDENT_TICKET_PLUGIN_SLUG", default="jira-ticket")
INCIDENT_TASK_PLUGIN_SLUG = config("INCIDENT_TASK_PLUGIN_SLUG", default="google-drive-task")
INCIDENT_TASK_SLUG = config("INCIDENT_TASK_SLUG", default="google-docs-incident-task")
INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID = config("INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID")

INCIDENT_FAQ_DOCUMENT_ID = config("INCIDENT_FAQ_DOCUMENT_ID")

INCIDENT_NOTIFICATION_CONVERSATIONS = config(
    "INCIDENT_NOTIFICATION_CONVERSATIONS", cast=CommaSeparatedStrings
)

INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS = config(
    "INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS", cast=CommaSeparatedStrings
)

INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID = config(
    "INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID", default=None
)

# Incident Cost Configuration
ANNUAL_COST_EMPLOYEE = config("ANNUAL_COST_EMPLOYEE", cast=int, default="650000")
