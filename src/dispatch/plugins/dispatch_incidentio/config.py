from pydantic import Field, SecretStr
from dispatch.config import BaseConfigurationModel


class IncidentIOConfiguration(BaseConfigurationModel):
    """incident.io configuration"""

    api_key: SecretStr = Field(title="API Key", description="Your incident.io API key.")
