from pydantic import Field, SecretStr
from dispatch.config import BaseConfigurationModel


class DuoConfiguration(BaseConfigurationModel):
    """Duo configuration description."""

    integration_key: SecretStr = Field(
        title="Integration Key", description="Admin API integration key ('DI...'):"
    )
    integration_secret_key: SecretStr = Field(
        title="Integration Secret Key",
        description="Secret token used in conjunction with integration key.",
    )
    host: str = Field(
        title="API Hostname",
        description="API hostname ('api-....duosecurity.com'): ",
    )
