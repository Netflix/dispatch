import json
import socket
import tempfile

from google.oauth2 import service_account
import googleapiclient.discovery

from .config import (
    GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
    GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
    GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT,
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY,
    GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
    GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
    GOOGLE_DEVELOPER_KEY,
)

TIMEOUT = 300

socket.setdefaulttimeout(TIMEOUT)


def get_service(service_name: str, version: str, scopes: list):
    """Formats specified credentials for Google clients."""
    data = {
        "type": "service_account",
        "project_id": GOOGLE_SERVICE_ACCOUNT_PROJECT_ID,
        "private_key_id": GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
        "private_key": str(GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY).replace("\\n", "\n"),
        "client_email": GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL,
        "client_id": GOOGLE_SERVICE_ACCOUNT_CLIENT_ID,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    with tempfile.NamedTemporaryFile() as service_account_file:
        service_account_file.write(json.dumps(data).encode())
        service_account_file.seek(0)

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file.name, scopes=scopes
        )

        delegated_credentials = credentials.with_subject(GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT)

        return googleapiclient.discovery.build(
            service_name,
            version,
            credentials=delegated_credentials,
            cache_discovery=False,
            developerKey=GOOGLE_DEVELOPER_KEY,
        )
