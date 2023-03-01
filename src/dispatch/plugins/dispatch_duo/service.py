import duo_client
from duo_client.auth import Auth

from dispatch.plugins.dispatch_duo.config import DuoConfiguration


def create_duo_auth_client(config: DuoConfiguration) -> Auth:
    """Creates a Duo Auth API client."""
    return duo_client.Auth(
        ikey=config.integration_key.get_secret_value(),
        skey=config.integration_secret_key.get_secret_value(),
        host=config.host,
    )
