import json
import logging
import socket
import tempfile
import urllib.parse

import googleapiclient.discovery
from google.oauth2 import service_account

from .config import (
    DWD_ENABLED,
    GOOGLE_DEVELOPER_KEY,
    GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
    GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
    GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT,
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY,
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
    GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
)

TIMEOUT = 300
log = logging.getLogger(__name__)

socket.setdefaulttimeout(TIMEOUT)


def get_credential_data():
    if DWD_ENABLED:
        return {
            "type": "service_account",
            "project_id": GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
            "private_key_id": GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
            "private_key": str(GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY).replace("\\n", "\n"),
            "client_email": GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
            "client_id": GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    else:
        return {
            "type": "service_account",
            "project_id": GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
            "private_key_id": GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
            "private_key": str(GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY).replace("\\n", "\n"),
            "client_email": GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
            "client_id": GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": urllib.parse.quote_plus(
                f"https://www.googleapis.com/robot/v1/metadata/x509/{GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL}"
            ),
        }


def get_service(service_name: str, version: str, scopes: list):
    """Formats specified credentials for Google clients."""
    data = get_credential_data()
    with tempfile.NamedTemporaryFile() as service_account_file:
        service_account_file.write(json.dumps(data).encode())
        service_account_file.seek(0)

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file.name, scopes=scopes
        )

        delegated_credentials = credentials.with_subject(GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT)

        # Prepare arguments to pass to discovery.build() call
        kwargs = {
            # Conditionally use delegated credentials when DWD is enabled.
            "credentials": delegated_credentials if DWD_ENABLED else credentials,
            "cache_discovery": False,
        }
        # Add developerKey only when DWD is enabled
        if DWD_ENABLED:
            log.debug("Adding the developerKey argument because domain-wide delegation is enabled.")
            kwargs.update({"developerKey": GOOGLE_DEVELOPER_KEY})

        return googleapiclient.discovery.build(service_name, version, **kwargs)
