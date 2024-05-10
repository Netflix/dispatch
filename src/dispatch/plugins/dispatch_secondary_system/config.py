from pydantic import Field, SecretStr
from dispatch.config import BaseConfigurationModel


class SecondarySytemConfiguration(BaseConfigurationModel):
    """Secondary system configuration description."""

    api_key: SecretStr = Field(title="API Key", description="Your secondary system API key.")
