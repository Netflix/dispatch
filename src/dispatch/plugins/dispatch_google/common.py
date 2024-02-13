import json
import socket
import tempfile

from google.oauth2 import service_account
import googleapiclient.discovery

from .config import GoogleConfiguration

TIMEOUT = 300

socket.setdefaulttimeout(TIMEOUT)


def get_service(
    config: GoogleConfiguration, service_name: str, version: str, scopes: list
) -> googleapiclient.discovery.Resource:
    """Formats specified credentials for Google clients."""
    data = {
        "type": "service_account",
        "project_id": config.service_account_project_id,
        "private_key_id": config.service_account_private_key_id,
        "private_key": config.service_account_private_key.get_secret_value().replace("\\n", "\n"),
        "client_email": config.service_account_client_email,
        "client_id": config.service_account_client_id,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    with tempfile.NamedTemporaryFile() as service_account_file:
        service_account_file.write(json.dumps(data).encode())
        service_account_file.seek(0)

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file.name, scopes=scopes
        )

        delegated_credentials = credentials.with_subject(config.service_account_delegated_account)

        return googleapiclient.discovery.build(
            service_name,
            version,
            credentials=delegated_credentials,
            cache_discovery=False,
            developerKey=config.developer_key.get_secret_value(),
        )
