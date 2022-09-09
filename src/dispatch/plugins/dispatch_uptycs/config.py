from pydantic import Field

from dispatch.config import BaseConfigurationModel, SecretStr


class UptycsConfiguration(BaseConfigurationModel):
    """Uptycs configuration description."""

    api_key: SecretStr = Field(
        title="API Key", description="This is the key used to talk to the Uptycs API."
    )
